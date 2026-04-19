import concurrent.futures
import json
import os
import threading
import time

import boto3
from botocore.config import Config

from src.domain.ports.curated_data_lake import CuratedDataLakePort

_COUNTER_KEY = "curated/_metadata/counter.txt"


class S3CuratedDataLake(CuratedDataLakePort):
    def __init__(self) -> None:
        self._bucket  = os.environ["S3_RAW_BUCKET"]
        self._prefix  = os.getenv("S3_CURATED_PREFIX", "curated/")
        self._client  = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            config=Config(connect_timeout=5, read_timeout=10, retries={"max_attempts": 1}),
        )
        self._cache: list[dict] = []
        self._cache_time = 0.0
        self._cache_ttl  = 60
        self._lock = threading.Lock()

    # ── Radicado counter ──────────────────────────────────────────────────────

    def next_radicado(self) -> str:
        import uuid
        from datetime import datetime, timezone
        date = datetime.now(timezone.utc).strftime("%Y%m%d")
        suffix = uuid.uuid4().hex[:8].upper()
        return f"RAD-{date}-{suffix}"

    # ── Storage: key = curated/{radicado}.json → O(1) lookup ─────────────────

    def _key(self, radicado: str) -> str:
        return f"{self._prefix}{radicado}.json"

    def store(self, records: list[dict]) -> list[str]:
        keys: list[str] = []
        for record in records:
            radicado = record.get("radicado") or self.next_radicado()
            record["radicado"] = radicado
            key = self._key(radicado)
            self._client.put_object(
                Bucket=self._bucket, Key=key,
                Body=json.dumps(record, ensure_ascii=False),
                ContentType="application/json",
            )
            keys.append(key)
        self._cache_time = 0.0
        return keys

    def _find_key(self, radicado: str) -> str:
        """Returns the actual S3 key for a radicado (handles legacy path formats)."""
        direct = self._key(radicado)
        try:
            self._client.head_object(Bucket=self._bucket, Key=direct)
            return direct
        except Exception:
            pass
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self._bucket, Prefix=self._prefix):
            for obj in page.get("Contents", []):
                k = obj["Key"]
                if k.endswith(".json") and "_metadata" not in k:
                    try:
                        res = self._client.get_object(Bucket=self._bucket, Key=k)
                        data = json.loads(res["Body"].read().decode())
                        if data.get("radicado") == radicado:
                            return k
                    except Exception:
                        pass
        return direct

    def update_by_radicado(self, radicado: str, updates: dict) -> dict | None:
        """Merge-update: reads the existing record, merges `updates` on top,
        and writes the result back. Returns the merged record."""
        key = self._find_key(radicado)
        # Read existing record (if any) to merge
        existing = {}
        try:
            res = self._client.get_object(Bucket=self._bucket, Key=key)
            existing = json.loads(res["Body"].read().decode())
        except Exception:
            pass
        existing.update(updates)
        self._client.put_object(
            Bucket=self._bucket, Key=key,
            Body=json.dumps(existing, ensure_ascii=False),
            ContentType="application/json",
        )
        self._cache_time = 0.0
        return existing

    def get_by_radicado(self, radicado: str) -> dict | None:
        # Try direct key first (new records stored as curated/{radicado}.json)
        try:
            res = self._client.get_object(Bucket=self._bucket, Key=self._key(radicado))
            return json.loads(res["Body"].read().decode())
        except Exception:
            pass
        # Fall back to scanning the full list (legacy keys like curated/YYYY/MM/DD/{uuid}.json)
        for record in self.get_all():
            if record.get("radicado") == radicado:
                return record
        return None

    # ── Bulk read (cached, concurrent) ────────────────────────────────────────

    def get_all(self) -> list[dict]:
        if time.time() - self._cache_time < self._cache_ttl and self._cache:
            return self._cache

        with self._lock:
            if time.time() - self._cache_time < self._cache_ttl and self._cache:
                return self._cache

            keys_to_fetch: list[str] = []
            paginator = self._client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self._bucket, Prefix=self._prefix):
                for obj in page.get("Contents", []):
                    k = obj["Key"]
                    if k.endswith(".json") and "_metadata" not in k:
                        keys_to_fetch.append(k)

            def _fetch(key: str) -> dict | None:
                try:
                    res = self._client.get_object(Bucket=self._bucket, Key=key)
                    return json.loads(res["Body"].read().decode())
                except Exception:
                    return None

            records: list[dict] = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
                for result in ex.map(_fetch, keys_to_fetch):
                    if result:
                        records.append(result)

            self._cache = records
            self._cache_time = time.time()
            return records
