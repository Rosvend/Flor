"""
Facebook Graph API sync — fetches DMs from the last 24 h.
No classification at this stage: all messages go to the raw datalake.

Env vars required:
    FB_PAGE_ID
    FB_PAGE_ACCESS_TOKEN
"""

import os
from datetime import datetime, timedelta, timezone

import httpx

GRAPH_BASE = "https://graph.facebook.com/v19.0"

MOCK_DMS = [
    {
        "canal": "FB_DM",
        "usuario": {"nombre": "Pedro Gomez", "id_meta": "fb_001"},
        "contenido": "Buenos días, quiero interponer una queja formal por el mal servicio de agua",
        "metadata": {"post_id": None, "created_time": "2026-04-18T07:30:00+0000"},
    },
    {
        "canal": "FB_DM",
        "usuario": {"nombre": "Ana Lucia Torres", "id_meta": "fb_002"},
        "contenido": "¿Cuándo abren las inscripciones para el programa de vivienda?",
        "metadata": {"post_id": None, "created_time": "2026-04-18T09:45:00+0000"},
    },
    {
        "canal": "FB_DM",
        "usuario": {"nombre": None, "id_meta": "fb_003"},
        "contenido": "Denuncia: están construyendo sin permiso en el lote de la esquina",
        "metadata": {"post_id": None, "created_time": "2026-04-18T13:00:00+0000"},
    },
]


def _window() -> tuple[int, int]:
    now = datetime.now(timezone.utc)
    since = int((now - timedelta(hours=24)).timestamp())
    until = int(now.timestamp())
    return since, until


def fetch_dms(session: httpx.Client, page_id: str, access_token: str) -> list[dict]:
    since, until = _window()
    url = f"{GRAPH_BASE}/me/conversations"
    params = {
        "fields": "messages{message,from,created_time}",
        "since": since,
        "until": until,
        "access_token": access_token,
    }
    resp = session.get(url, params=params, timeout=30)
    resp.raise_for_status()

    items = []
    for conv in resp.json().get("data", []):
        for msg in conv.get("messages", {}).get("data", []):
            from_field = msg.get("from", {})
            # skip messages sent by the page itself
            if from_field.get("id") == page_id:
                continue
            items.append({
                "canal": "FB_DM",
                "usuario": {
                    "nombre": from_field.get("name"),
                    "id_meta": from_field.get("id", "unknown"),
                },
                "contenido": msg.get("message", ""),
                "metadata": {
                    "post_id": None,
                    "created_time": msg.get("created_time"),
                },
            })
    return items


def run(mock: bool = False) -> list[dict]:
    if mock:
        print(f"  [facebook]  MOCK — {len(MOCK_DMS)} DMs")
        return MOCK_DMS

    page_id = os.getenv("FB_PAGE_ID", "")
    access_token = os.getenv("FB_PAGE_ACCESS_TOKEN", "")
    if not page_id or not access_token:
        raise EnvironmentError("FB_PAGE_ID and FB_PAGE_ACCESS_TOKEN must be set in .env")

    with httpx.Client() as session:
        dms = fetch_dms(session, page_id, access_token)

    print(f"  [facebook]  {len(dms)} DMs")
    return dms
