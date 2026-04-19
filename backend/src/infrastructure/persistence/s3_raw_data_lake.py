import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.config import Config

from src.domain.ports.raw_data_lake import RawDataLakePort


class S3RawDataLake(RawDataLakePort):
    def __init__(self) -> None:
        self._bucket = os.environ["S3_RAW_BUCKET"]
        self._prefix = os.getenv("S3_RAW_PREFIX", "raw/")
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

    def get_all(self) -> list[dict]:
        records: list[dict] = []
        try:
            paginator = self._client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self._bucket, Prefix=self._prefix):
                if "Contents" not in page:
                    continue
                
                for obj in page["Contents"]:
                    if not obj["Key"].endswith(".json"):
                        continue
                        
                    response = self._client.get_object(Bucket=self._bucket, Key=obj["Key"])
                    content = response["Body"].read().decode("utf-8")
                    data = json.loads(content)
                    records.append(data)
        except Exception as e:
            print(f"Error recuperando datos de S3: {e}")
            
        return records
