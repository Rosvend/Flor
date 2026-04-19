import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.config import Config

from src.domain.ports.curated_data_lake import CuratedDataLakePort


class S3CuratedDataLake(CuratedDataLakePort):
    def __init__(self) -> None:
        self._bucket = os.environ["S3_RAW_BUCKET"]
        self._prefix = os.getenv("S3_CURATED_PREFIX", "curated/")
        self._client = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            config=Config(connect_timeout=5, read_timeout=10, retries={"max_attempts": 1}),
        )

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

        return keys

    def update(self, key: str, record: dict) -> None:
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=json.dumps(record, ensure_ascii=False),
            ContentType="application/json",
        )
