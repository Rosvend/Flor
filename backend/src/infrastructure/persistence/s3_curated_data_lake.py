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

    def store(self, records: list[dict]) -> list[str]:
        date_prefix = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        keys: list[str] = []

        for record in records:
            key = f"{self._prefix}{date_prefix}/{uuid.uuid4()}.json"
            self._client.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=json.dumps(record, ensure_ascii=False),
                ContentType="application/json",
            )
            keys.append(key)

        return keys
