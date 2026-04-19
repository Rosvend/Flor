"""
Test del pipeline completo de ingesta (Instagram + Facebook) → backend → datalake.
En modo mock no necesita credenciales de Meta.
Con S3_RAW_BUCKET seteado en .env, los registros van a S3 real.

Run:
    python tests/test_sync_mock.py
    python -m pytest tests/test_sync_mock.py -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx
from src.infrastructure.classification import instagram_sync, facebook_sync

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")
ENDPOINT = f"{BACKEND}/api/v1/ingest/raw"


def test_backend_is_up():
    resp = httpx.get(f"{BACKEND}/health")
    assert resp.status_code == 200, f"Backend no disponible: {resp.status_code}"
    print("✓ Backend up")


def test_ingest_instagram():
    items = instagram_sync.run(mock=True)
    resp = httpx.post(ENDPOINT, json=items, timeout=10)
    assert resp.status_code == 201, f"Error: {resp.status_code} — {resp.text}"
    data = resp.json()
    assert data["count"] == len(items)
    assert len(data["stored_keys"]) == len(items)
    print(f"✓ Instagram: {data['count']} registros → keys: {[k[:30] for k in data['stored_keys']]}")


def test_ingest_facebook():
    items = facebook_sync.run(mock=True)
    resp = httpx.post(ENDPOINT, json=items, timeout=10)
    assert resp.status_code == 201, f"Error: {resp.status_code} — {resp.text}"
    data = resp.json()
    assert data["count"] == len(items)
    assert len(data["stored_keys"]) == len(items)
    print(f"✓ Facebook: {data['count']} registros → keys: {[k[:30] for k in data['stored_keys']]}")


def test_full_pipeline():
    all_items = instagram_sync.run(mock=True) + facebook_sync.run(mock=True)
    resp = httpx.post(ENDPOINT, json=all_items, timeout=10)
    assert resp.status_code == 201
    data = resp.json()
    assert data["count"] == len(all_items)
    assert len(data["stored_keys"]) == len(all_items)

    using_s3 = os.getenv("S3_RAW_BUCKET") is not None
    destino = f"s3://{os.getenv('S3_RAW_BUCKET')}" if using_s3 else "memory"

    print(f"✓ Pipeline completo: {data['count']} registros → {destino}")
    print(f"  Primeras keys:")
    for k in data["stored_keys"]:
        print(f"    {k}")


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  TEST PIPELINE INGESTA RAW — IG + FB")
    s3 = os.getenv("S3_RAW_BUCKET")
    print(f"  Datalake: {'S3 → ' + s3 if s3 else 'InMemory (sin S3_RAW_BUCKET)'}")
    print("="*55 + "\n")

    tests = [test_backend_is_up, test_ingest_instagram, test_ingest_facebook, test_full_pipeline]
    failed = 0
    for t in tests:
        try:
            t()
        except Exception as e:
            print(f"✗ {t.__name__}: {e}")
            failed += 1

    print(f"\n{'='*55}")
    print(f"  {'✓ Todos OK' if not failed else f'✗ {failed} fallaron'} ({len(tests)-failed}/{len(tests)})")
    print("="*55 + "\n")
    sys.exit(failed)
