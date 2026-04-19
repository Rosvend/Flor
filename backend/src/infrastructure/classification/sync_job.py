"""
Sync job — fetches Facebook DMs, classifies them via the curated ingest
endpoint (which assigns radicado, runs AI analysis, and uploads to S3).

Usage:
    python -m src.infrastructure.classification.sync_job
"""

import os
from datetime import datetime, timezone

import httpx
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
INGEST_ENDPOINT = f"{BACKEND_URL}/api/v1/ingest/curated"


def _to_curated(item: dict) -> dict:
    """Map a raw facebook_sync record to the unified curated format."""
    usuario = item.get("usuario") or {}
    nombre = usuario.get("nombre")
    id_meta = usuario.get("id_meta")
    anonima = not bool(nombre)
    return {
        "canal": "META_DM",
        "anonima": anonima,
        "ciudadano": {
            "nombres": nombre,
            "apellidos": None,
            "tipo_documento": None,
            "numero_documento": None,
            "tipo_persona": "Natural",
            "genero": None,
            "correo_electronico": None,
            "telefono": None,
            "id_meta": id_meta,
        },
        "contenido": item.get("contenido", ""),
        "metadata": item.get("metadata", {}),
    }


def run() -> None:
    from src.infrastructure.classification import facebook_sync

    print(f"\n{'='*50}")
    print(f"  Sync job — {datetime.now(timezone.utc).isoformat()}")
    print(f"{'='*50}")

    raw_items = facebook_sync.run()

    print(f"\n  Total a ingestar: {len(raw_items)} mensajes")

    if not raw_items:
        print("  Nada que ingestar.")
        print(f"{'='*50}\n")
        return

    curated_items = [_to_curated(i) for i in raw_items]

    print(f"  Enviando a {INGEST_ENDPOINT} ...")
    resp = httpx.post(INGEST_ENDPOINT, json=curated_items, timeout=60)
    resp.raise_for_status()

    result = resp.json()
    print(f"\n  ✓ {result['count']} PQRSDs radicadas en S3:")
    for key in result["stored_keys"]:
        print(f"    {key}")

    print(f"\n{'='*50}\n")


if __name__ == "__main__":
    run()
