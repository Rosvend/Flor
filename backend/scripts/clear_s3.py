"""
Elimina todos los objetos del bucket S3 (raw/ y curated/).
Usa las mismas credenciales del .env.

Run:
    uv run python scripts/clear_s3.py
"""

import os
import boto3
from dotenv import load_dotenv

load_dotenv()

bucket = os.environ["S3_RAW_BUCKET"]
client = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

paginator = client.get_paginator("list_objects_v2")
deleted = 0

for page in paginator.paginate(Bucket=bucket):
    objects = page.get("Contents", [])
    if not objects:
        continue
    client.delete_objects(
        Bucket=bucket,
        Delete={"Objects": [{"Key": o["Key"]} for o in objects]},
    )
    deleted += len(objects)

print(f"✓ {deleted} objetos eliminados de s3://{bucket}")
