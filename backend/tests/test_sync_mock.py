"""
Test automatizado del flujo completo de ingesta (Instagram + Facebook) en modo mock.
No necesita credenciales reales ni acceso a la API de Meta.

Requisito: backend corriendo en localhost:8000

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
ENDPOINT = f"{BACKEND}/api/v1/ingest/meta/raw"

EXPECTED_CANALES = {"IG_COMMENT", "IG_DM", "FB_DM"}


def test_backend_is_up():
    resp = httpx.get(f"{BACKEND}/health")
    assert resp.status_code == 200, f"Backend no disponible: {resp.status_code}"
    print("✓ Backend up")


def test_instagram_mock_data():
    items = instagram_sync.run(mock=True)
    assert len(items) > 0
    canales = {i["canal"] for i in items}
    assert "IG_COMMENT" in canales, "Faltan comentarios de Instagram"
    assert "IG_DM" in canales, "Faltan DMs de Instagram"
    print(f"✓ Instagram mock: {len(items)} items ({canales})")


def test_facebook_mock_data():
    items = facebook_sync.run(mock=True)
    assert len(items) > 0
    assert all(i["canal"] == "FB_DM" for i in items)
    print(f"✓ Facebook mock: {len(items)} DMs")


def test_ingest_instagram():
    items = instagram_sync.run(mock=True)
    resp = httpx.post(ENDPOINT, json=items, timeout=10)
    assert resp.status_code == 201, f"Error: {resp.status_code} — {resp.text}"
    records = resp.json()
    assert len(records) == len(items)
    for r in records:
        assert r["canal"] in ("IG_COMMENT", "IG_DM")
        assert r["id"]
        assert r["ingested_at"]
    print(f"✓ Ingesta Instagram: {len(records)} registros almacenados")


def test_ingest_facebook():
    items = facebook_sync.run(mock=True)
    resp = httpx.post(ENDPOINT, json=items, timeout=10)
    assert resp.status_code == 201, f"Error: {resp.status_code} — {resp.text}"
    records = resp.json()
    assert len(records) == len(items)
    for r in records:
        assert r["canal"] == "FB_DM"
        assert r["id"]
    print(f"✓ Ingesta Facebook: {len(records)} registros almacenados")


def test_full_sync_flow():
    all_items = instagram_sync.run(mock=True) + facebook_sync.run(mock=True)
    resp = httpx.post(ENDPOINT, json=all_items, timeout=10)
    assert resp.status_code == 201
    records = resp.json()
    assert len(records) == len(all_items)

    canales = {r["canal"] for r in records}
    assert canales == EXPECTED_CANALES, f"Canales esperados: {EXPECTED_CANALES}, recibidos: {canales}"

    anonimos = [r for r in records if r["usuario"]["nombre"] is None]
    con_nombre = [r for r in records if r["usuario"]["nombre"] is not None]

    print(f"✓ Flujo completo: {len(records)} registros")
    print(f"  Canales: {canales}")
    print(f"  Con nombre: {len(con_nombre)} | Anónimos: {len(anonimos)}")
    print("\n  Detalle:")
    for r in records:
        nombre = r["usuario"]["nombre"] or "(anónimo)"
        print(f"    [{r['canal']:<12}] {nombre:<25} | \"{r['contenido'][:45]}\"")


if __name__ == "__main__":
    print("\n" + "="*55)
    print("  TEST INGESTA RAW — Instagram + Facebook (MOCK)")
    print("="*55 + "\n")

    tests = [
        test_backend_is_up,
        test_instagram_mock_data,
        test_facebook_mock_data,
        test_ingest_instagram,
        test_ingest_facebook,
        test_full_sync_flow,
    ]

    failed = 0
    for t in tests:
        try:
            t()
        except Exception as e:
            print(f"✗ {t.__name__}: {e}")
            failed += 1

    print(f"\n{'='*55}")
    if failed == 0:
        print(f"  ✓ Todos los tests pasaron ({len(tests)}/{len(tests)})")
    else:
        print(f"  ✗ {failed} tests fallaron")
    print("="*55 + "\n")
    sys.exit(failed)
