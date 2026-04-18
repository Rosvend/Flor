"""
Instagram Graph API sync — fetches comments + DMs from the last 24 h.
No classification at this stage: all messages go to the raw datalake.

Env vars required:
    IG_USER_ID
    IG_PAGE_ACCESS_TOKEN
"""

import os
from datetime import datetime, timedelta, timezone

import httpx

GRAPH_BASE = "https://graph.facebook.com/v19.0"

MOCK_COMMENTS = [
    {
        "canal": "IG_COMMENT",
        "usuario": {"nombre": "laura_medellin", "id_meta": "ig_001"},
        "contenido": "El parque del barrio lleva 3 semanas sin alumbrado, por favor revisar",
        "metadata": {"post_id": "ig_post_001", "created_time": "2026-04-18T09:00:00+0000"},
    },
    {
        "canal": "IG_COMMENT",
        "usuario": {"nombre": "carlos_ciudadano", "id_meta": "ig_002"},
        "contenido": "¡Qué bonita foto de la alcaldía!",
        "metadata": {"post_id": "ig_post_001", "created_time": "2026-04-18T10:30:00+0000"},
    },
    {
        "canal": "IG_COMMENT",
        "usuario": {"nombre": None, "id_meta": "ig_003"},
        "contenido": "Solicito información sobre cómo radicar una petición formal",
        "metadata": {"post_id": "ig_post_002", "created_time": "2026-04-18T11:00:00+0000"},
    },
]

MOCK_DMS = [
    {
        "canal": "IG_DM",
        "usuario": {"nombre": "maria_perez_med", "id_meta": "ig_004"},
        "contenido": "Buenos días, necesito saber el estado de mi solicitud de hace dos semanas",
        "metadata": {"post_id": None, "created_time": "2026-04-18T08:00:00+0000"},
    },
    {
        "canal": "IG_DM",
        "usuario": {"nombre": None, "id_meta": "ig_005"},
        "contenido": "Hay un hueco enorme en la calle 45 con carrera 80, es peligroso",
        "metadata": {"post_id": None, "created_time": "2026-04-18T12:00:00+0000"},
    },
]


def _since_dt() -> datetime:
    return datetime.now(timezone.utc) - timedelta(hours=24)


def fetch_comments(session: httpx.Client, ig_user_id: str, access_token: str) -> list[dict]:
    since = _since_dt()
    url = f"{GRAPH_BASE}/{ig_user_id}/media"
    params = {
        "fields": "id,timestamp,comments{id,text,username,timestamp,from}",
        "access_token": access_token,
    }
    resp = session.get(url, params=params, timeout=30)
    resp.raise_for_status()

    items = []
    for media in resp.json().get("data", []):
        for comment in media.get("comments", {}).get("data", []):
            try:
                comment_time = datetime.fromisoformat(
                    comment.get("timestamp", "").replace("Z", "+00:00")
                )
            except ValueError:
                continue
            if comment_time < since:
                continue
            from_field = comment.get("from", {})
            items.append({
                "canal": "IG_COMMENT",
                "usuario": {
                    "nombre": from_field.get("username") or comment.get("username"),
                    "id_meta": from_field.get("id", "unknown"),
                },
                "contenido": comment.get("text", ""),
                "metadata": {
                    "post_id": media.get("id"),
                    "created_time": comment.get("timestamp"),
                },
            })
    return items


def fetch_dms(session: httpx.Client, ig_user_id: str, access_token: str) -> list[dict]:
    since = _since_dt()
    url = f"{GRAPH_BASE}/{ig_user_id}/conversations"
    params = {
        "platform": "instagram",
        "fields": "messages{message,from,created_time}",
        "since": int(since.timestamp()),
        "until": int(datetime.now(timezone.utc).timestamp()),
        "access_token": access_token,
    }
    resp = session.get(url, params=params, timeout=30)
    resp.raise_for_status()

    items = []
    for conv in resp.json().get("data", []):
        for msg in conv.get("messages", {}).get("data", []):
            from_field = msg.get("from", {})
            items.append({
                "canal": "IG_DM",
                "usuario": {
                    "nombre": from_field.get("username") or from_field.get("name"),
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
        items = MOCK_COMMENTS + MOCK_DMS
        print(f"  [instagram] MOCK — {len(MOCK_COMMENTS)} comments + {len(MOCK_DMS)} DMs")
        return items

    ig_user_id = os.getenv("IG_USER_ID", "")
    access_token = os.getenv("IG_PAGE_ACCESS_TOKEN", "")
    if not ig_user_id or not access_token:
        raise EnvironmentError("IG_USER_ID and IG_PAGE_ACCESS_TOKEN must be set in .env")

    with httpx.Client() as session:
        comments = fetch_comments(session, ig_user_id, access_token)
        dms = fetch_dms(session, ig_user_id, access_token)

    items = comments + dms
    print(f"  [instagram] {len(comments)} comments + {len(dms)} DMs")
    return items
