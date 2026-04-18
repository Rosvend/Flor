"""
Validates that ALL messages (PQRS or not) arrive at the raw ingest endpoint.

Run:  python tests/test_meta_ingest.py
      (backend must be running on localhost:8000)
"""

import httpx

BACKEND = "http://localhost:8000"

MOCK_PAYLOAD = [
    {
        "canal": "META_COMMENT",
        "usuario": {"nombre": "Juan Pérez", "id_meta": "111"},
        "contenido": "Queja por el mal estado de la vía principal del barrio",
        "metadata": {"post_id": "post_001", "created_time": "2026-04-18T10:00:00+0000"},
    },
    {
        "canal": "META_DM",
        "usuario": {"nombre": None, "id_meta": "222"},
        "contenido": "¿Cuándo es el próximo evento cultural en el parque?",
        "metadata": {"post_id": None, "created_time": "2026-04-18T11:00:00+0000"},
    },
    {
        "canal": "META_COMMENT",
        "usuario": {"nombre": "María López", "id_meta": "333"},
        "contenido": "¡Qué bonita foto del alcalde!",
        "metadata": {"post_id": "post_002", "created_time": "2026-04-18T12:00:00+0000"},
    },
]


def test_all_messages_ingested():
    resp = httpx.post(f"{BACKEND}/api/v1/ingest/meta/raw", json=MOCK_PAYLOAD)
    assert resp.status_code == 201, f"Expected 201, got {resp.status_code}: {resp.text}"

    records = resp.json()
    assert len(records) == len(MOCK_PAYLOAD), (
        f"Expected {len(MOCK_PAYLOAD)} records, got {len(records)}"
    )

    for record in records:
        assert "id" in record
        assert "ingested_at" in record
        assert record["canal"] in ("META_COMMENT", "META_DM")
        assert "contenido" in record

    print(f"\n✓ {len(records)} mensajes almacenados (sin filtro):")
    for r in records:
        print(f"  [{r['canal']}] id={r['id'][:8]}... | \"{r['contenido'][:50]}\"")


if __name__ == "__main__":
    test_all_messages_ingested()
    print("\n✓ Test passed — todos los mensajes llegaron al backend")
