"""
Instagram Graph API sync agent — runs every 24 h.
Fetches ALL comments + DMs from the last 24 hours and POSTs them
to the raw ingest endpoint. No classification at this stage.

Usage:
    python -m src.infrastructure.classification.meta_sync

Required env vars:
    IG_USER_ID              Instagram Business Account ID
    IG_PAGE_ACCESS_TOKEN    Page Access Token de la página de Facebook conectada
    BACKEND_URL             (default: http://localhost:8000)
"""

import os
from datetime import datetime, timedelta, timezone

import httpx
from dotenv import load_dotenv

load_dotenv()

IG_USER_ID = os.getenv("IG_USER_ID", "")
ACCESS_TOKEN = os.getenv("IG_PAGE_ACCESS_TOKEN", "")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
GRAPH_BASE = "https://graph.facebook.com/v19.0"


def _window() -> tuple[datetime, int, int]:
    now = datetime.now(timezone.utc)
    since_dt = now - timedelta(hours=24)
    return since_dt, int(since_dt.timestamp()), int(now.timestamp())


def fetch_comments(session: httpx.Client, since_dt: datetime) -> list[dict]:
    """
    Fetches recent media and extracts comments from the last 24 h.
    IG API does not support since/until on nested comment fields,
    so we filter by timestamp in Python.
    """
    url = f"{GRAPH_BASE}/{IG_USER_ID}/media"
    params = {
        "fields": "id,timestamp,comments{id,text,username,timestamp,from}",
        "access_token": ACCESS_TOKEN,
    }
    resp = session.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for media in data.get("data", []):
        for comment in media.get("comments", {}).get("data", []):
            comment_time_str = comment.get("timestamp", "")
            try:
                comment_time = datetime.fromisoformat(comment_time_str.replace("Z", "+00:00"))
            except ValueError:
                continue

            if comment_time < since_dt:
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
                    "created_time": comment_time_str,
                },
            })
    return items


def fetch_dms(session: httpx.Client, since: int, until: int) -> list[dict]:
    url = f"{GRAPH_BASE}/{IG_USER_ID}/conversations"
    params = {
        "platform": "instagram",
        "fields": "messages{message,from,created_time}",
        "since": since,
        "until": until,
        "access_token": ACCESS_TOKEN,
    }
    resp = session.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for conv in data.get("data", []):
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


def run_sync() -> None:
    if not IG_USER_ID or not ACCESS_TOKEN:
        raise EnvironmentError("IG_USER_ID and IG_PAGE_ACCESS_TOKEN must be set in .env")

    since_dt, since_ts, until_ts = _window()

    with httpx.Client() as session:
        comments = fetch_comments(session, since_dt)
        dms = fetch_dms(session, since_ts, until_ts)

    all_items = comments + dms
    print(f"[ig_sync] Fetched {len(comments)} comments + {len(dms)} DMs = {len(all_items)} total")

    if not all_items:
        print("[ig_sync] Nothing to ingest.")
        return

    resp = httpx.post(
        f"{BACKEND_URL}/api/v1/ingest/meta/raw",
        json=all_items,
        timeout=30,
    )
    resp.raise_for_status()
    records = resp.json()
    print(f"[ig_sync] Stored {len(records)} records")
    for r in records:
        print(f"  [{r['canal']}] id={r['id'][:8]}... | \"{r['contenido'][:60]}\"")


if __name__ == "__main__":
    run_sync()
