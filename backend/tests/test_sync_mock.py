"""
Test de integración del pipeline completo:
    Facebook Graph API → sync_job → POST /api/v1/ingest/raw → S3

Requisitos:
    - Backend corriendo en localhost:8000
    - .env con FB_PAGE_ID, FB_PAGE_ACCESS_TOKEN, S3_RAW_BUCKET, AWS_*

Run:
    python tests/test_sync_mock.py
    python -m pytest tests/test_sync_mock.py -v
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import httpx

BACKEND = os.getenv("BACKEND_URL", "http://localhost:8000")
ENDPOINT = f"{BACKEND}/api/v1/ingest/raw"


def test_backend_is_up():
    resp = httpx.get(f"{BACKEND}/health", timeout=5)
    assert resp.status_code == 200, f"Backend no disponible: {resp.status_code}"
    print("✓ Backend up")


def test_env_vars():
    missing = [v for v in ("FB_PAGE_ID", "FB_PAGE_ACCESS_TOKEN", "S3_RAW_BUCKET") if not os.getenv(v)]
    assert not missing, f"Faltan variables en .env: {missing}"
    print("✓ Variables de entorno OK")


def test_facebook_fetch():
    from src.infrastructure.classification.facebook_sync import run
    items = run()
    assert isinstance(items, list), "run() debe retornar una lista"
    print(f"✓ Facebook fetch: {len(items)} DMs recibidos de la API")
    return items


def test_ingest_pipeline():
    from src.infrastructure.classification.facebook_sync import run
    items = run()

    if not items:
        print("⚠ Sin mensajes en las últimas 24 h — pipeline no ejecutado")
        return

    resp = httpx.post(ENDPOINT, json=items, timeout=30)
    assert resp.status_code == 201, f"Error {resp.status_code}: {resp.text}"

    data = resp.json()
    assert data["count"] == len(items)
    assert len(data["stored_keys"]) == len(items)

    destino = f"s3://{os.getenv('S3_RAW_BUCKET')}" if os.getenv("S3_RAW_BUCKET") else "memory"
    print(f"✓ Pipeline completo: {data['count']} registros → {destino}")
    for key in data["stored_keys"]:
        print(f"    {key}")


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  TEST PIPELINE — Facebook DMs → ingest/raw → S3")
    print("="*55 + "\n")

    tests = [test_backend_is_up, test_env_vars, test_facebook_fetch, test_ingest_pipeline]
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
