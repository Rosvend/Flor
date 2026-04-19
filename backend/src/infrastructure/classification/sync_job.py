"""
Sync job — fetches raw Facebook DMs and sends them to the ingest endpoint,
which stores each record in the raw datalake (S3).

Usage:
    python -m src.infrastructure.classification.sync_job
"""

import os
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
INGEST_ENDPOINT = f"{BACKEND_URL}/api/v1/ingest/raw"


def run() -> None:
    from src.infrastructure.classification import facebook_sync

    print(f"\n{'='*50}")
    print(f"  Sync job — {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*50}")

    items = facebook_sync.run()

    print(f"\n  Total a ingestar: {len(items)} mensajes")

    if not items:
        print("  Nada que ingestar.")
        print(f"{'='*50}\n")
        return

    print(f"  Enviando a {INGEST_ENDPOINT} ...")
    resp = httpx.post(INGEST_ENDPOINT, json=items, timeout=30)
    resp.raise_for_status()

    result = resp.json()
    print(f"\n  ✓ {result['count']} registros almacenados en S3:")
    for key in result["stored_keys"]:
        print(f"    {key}")

    print(f"\n{'='*50}\n")


if __name__ == "__main__":
    run()
