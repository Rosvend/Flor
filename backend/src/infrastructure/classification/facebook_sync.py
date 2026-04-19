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
from dotenv import load_dotenv

load_dotenv()

GRAPH_BASE = "https://graph.facebook.com/v25.0"


def _window() -> tuple[datetime, datetime]:
    now = datetime.now(timezone.utc)
    return now - timedelta(hours=24), now


def fetch_dms(session: httpx.Client, page_id: str, access_token: str) -> list[dict]:
    since_dt, _ = _window()
    url = f"{GRAPH_BASE}/{page_id}/conversations"
    params = {
        "fields": "messages{message,from,created_time}",
        "access_token": access_token,
    }

    items = []
    while url:
        resp = session.get(url, params=params, timeout=30)
        if not resp.is_success:
            print(f"  [facebook] Error {resp.status_code}: {resp.text}")
        resp.raise_for_status()
        data = resp.json()

        for conv in data.get("data", []):
            for msg in conv.get("messages", {}).get("data", []):
                created_time = msg.get("created_time", "")
                try:
                    msg_dt = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
                except ValueError:
                    continue
                if msg_dt < since_dt:
                    continue

                from_field = msg.get("from", {})
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
                        "created_time": created_time,
                    },
                })

        url = data.get("paging", {}).get("next")
        params = {}

    return items


def run() -> list[dict]:
    page_id = os.getenv("FB_PAGE_ID", "")
    access_token = os.getenv("FB_PAGE_ACCESS_TOKEN", "")

    if not page_id or not access_token:
        raise EnvironmentError(
            "FB_PAGE_ID y FB_PAGE_ACCESS_TOKEN deben estar seteados en el .env"
        )

    with httpx.Client() as session:
        dms = fetch_dms(session, page_id, access_token)

    print(f"  [facebook] {len(dms)} DMs fetched")
    return dms
