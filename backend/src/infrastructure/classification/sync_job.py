"""
Unified sync job — fetches raw messages from Instagram + Facebook
and stores them in the raw datalake endpoint.

Usage:
    # Con credenciales reales (.env configurado)
    python -m src.infrastructure.classification.sync_job

    # Modo mock (no necesita credenciales, ideal para testing)
    python -m src.infrastructure.classification.sync_job --mock
"""

import sys
import os
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
INGEST_ENDPOINT = f"{BACKEND_URL}/api/v1/ingest/raw"


def post_to_datalake(items: list[dict]) -> list[dict]:
    resp = httpx.post(INGEST_ENDPOINT, json=items, timeout=30)
    resp.raise_for_status()
    return resp.json()


def run(mock: bool = False) -> None:
    from src.infrastructure.classification import instagram_sync, facebook_sync

    mode = "MOCK" if mock else "REAL"
    print(f"\n{'='*50}")
    print(f"  Sync job — {datetime.now(timezone.utc).isoformat()} [{mode}]")
    print(f"{'='*50}")

    ig_items = instagram_sync.run(mock=mock)
    fb_items = facebook_sync.run(mock=mock)
    all_items = ig_items + fb_items

    print(f"\n  Total a ingestar: {len(all_items)} mensajes")

    if not all_items:
        print("  Nada que ingestar.")
        return

    print(f"  Enviando al backend ({INGEST_ENDPOINT})...")
    records = post_to_datalake(all_items)

    print(f"\n  ✓ {len(records)} registros almacenados:\n")
    for r in records:
        print(f"    [{r['canal']:<12}] {r['id'][:8]}... | \"{r['contenido'][:55]}\"")

    print(f"\n{'='*50}\n")


if __name__ == "__main__":
    mock_mode = "--mock" in sys.argv
    run(mock=mock_mode)
