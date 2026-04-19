import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.config import Config

from src.domain.ports.curated_data_lake import CuratedDataLakePort


class S3CuratedDataLake(CuratedDataLakePort):
    def __init__(self) -> None:
        import time
        self._bucket = os.environ["S3_RAW_BUCKET"]
        self._prefix = os.getenv("S3_CURATED_PREFIX", "curated/")
        self._client = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            config=Config(connect_timeout=5, read_timeout=10, retries={"max_attempts": 1}),
        )
        self._cache = []
        self._cache_time = 0
        self._cache_ttl = 60  # Cache for 60 seconds
        
        import threading
        self._lock = threading.Lock()

    def _get_next_id_and_increment(self, count: int) -> int:
        if count <= 0:
            return 1
        counter_key = f"{self._prefix}_metadata/counter.txt"
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=counter_key)
            current_id = int(response["Body"].read().decode("utf-8").strip())
        except Exception:
            current_id = 0

        next_id = current_id + 1
        new_max_id = current_id + count

        try:
            self._client.put_object(
                Bucket=self._bucket,
                Key=counter_key,
                Body=str(new_max_id),
                ContentType="text/plain",
            )
        except Exception as e:
            print(f"Error updating counter: {e}")

        return next_id

    def store(self, records: list[dict]) -> list[str]:
        date_prefix = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        keys: list[str] = []

        start_id = self._get_next_id_and_increment(len(records))

        for i, record in enumerate(records):
            if "id" not in record or record["id"] is None:
                record["id"] = start_id + i
                
            key = f"{self._prefix}{date_prefix}/{uuid.uuid4()}.json"
            self._client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=json.dumps(record, ensure_ascii=False),
                ContentType="application/json",
            )
            keys.append(key)

        self._cache_time = 0  # Invalidate cache
        return keys

    def update(self, key: str, record: dict) -> None:
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=json.dumps(record, ensure_ascii=False),
            ContentType="application/json",
        )
        self._cache_time = 0  # Invalidate cache

    def get_all(self) -> list[dict]:
        import time
        
        # Fast path if cache is valid (no lock needed for reading the time)
        if time.time() - self._cache_time < self._cache_ttl and self._cache:
            return self._cache
            
        with self._lock:
            # Check again inside lock
            if time.time() - self._cache_time < self._cache_ttl and self._cache:
                return self._cache

            import concurrent.futures
            keys_to_fetch = []
            paginator = self._client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self._bucket, Prefix=self._prefix):
                if "Contents" not in page:
                    continue
                for obj in page["Contents"]:
                    if obj["Key"].endswith(".json"):
                        keys_to_fetch.append(obj["Key"])
            
            records = []
            # Fetch files concurrently to speed up the process
            def fetch_s3_object(key):
                try:
                    res = self._client.get_object(Bucket=self._bucket, Key=key)
                    return json.loads(res["Body"].read().decode("utf-8"))
                except Exception:
                    return None
                    
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
                results = executor.map(fetch_s3_object, keys_to_fetch)
                for res in results:
                    if res:
                        records.append(res)
                        
            self._cache = records
            self._cache_time = time.time()
            return records

    def get_by_radicado(self, radicado: str) -> dict | None:
        # In this simple implementation, we might need to scan if we don't have an index.
        # However, we can also store by radicado in the key to make it O(1).
        # For now, let's scan all or assume get_all is called and filtered by the caller.
        # Optimized version:
        all_records = self.get_all()
        for r in all_records:
            if r.get("radicado") == radicado:
                return r
        return None

    def update_by_radicado(self, radicado: str, patch: dict) -> dict | None:
        # Scan the bucket to find the key whose body matches the radicado, then
        # shallow-merge the patch and put it back. We intentionally bypass the
        # get_all cache because we need the S3 key, not just the record body.
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self._bucket, Prefix=self._prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if not key.endswith(".json"):
                    continue
                try:
                    res = self._client.get_object(Bucket=self._bucket, Key=key)
                    record = json.loads(res["Body"].read().decode("utf-8"))
                except Exception:
                    continue
                if record.get("radicado") != radicado:
                    continue
                record.update(patch)
                self._client.put_object(
                    Bucket=self._bucket,
                    Key=key,
                    Body=json.dumps(record, ensure_ascii=False),
                    ContentType="application/json",
                )
                self._cache_time = 0
                return record
        return None
