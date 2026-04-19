import logging
from pathlib import Path
from dotenv import load_dotenv

# Configurar logging antes de cargar nada
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:     %(message)s",
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno lo antes posible usando ruta absoluta
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.interfaces.http.auth_router import router as auth_router
from src.interfaces.http.chatbot_router import router as chatbot_router
from src.interfaces.http.ingest_router import router as ingest_router
from src.interfaces.http.ingest_curated_router import router as ingest_curated_router
from src.interfaces.http.pqrs_router import router as pqrs_router
from src.interfaces.http.migration_router import router as migration_router

app = FastAPI(title="PQRS Optimization API", version="0.1.0")

_cors_origins = [
    o.strip() for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://flor.vercel.app",
    ).split(",") if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router, prefix="/api/v1")
app.include_router(ingest_curated_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(pqrs_router, prefix="/api/v1")
app.include_router(migration_router, prefix="/api/v1")
app.include_router(chatbot_router, prefix="/api/v1")


# ── Scheduler: ingesta IMAP periódica ────────────────────────────────────────
from apscheduler.schedulers.background import BackgroundScheduler

_email_scheduler: BackgroundScheduler | None = None


def _run_email_ingest() -> None:
    try:
        from src.infrastructure import container
        result = container.get_ingest_email_pqrs().execute()
        if result.get("count"):
            logger.info(
                "Ingesta IMAP: %s PQRS nuevas (%s)",
                result["count"],
                result.get("radicados"),
            )
    except Exception as exc:
        logger.error("Error en ingesta IMAP programada: %s", exc)


@app.on_event("startup")
def _start_email_scheduler() -> None:
    global _email_scheduler
    if os.getenv("EMAIL_INGEST_ENABLED", "true").lower() in ("0", "false", "no"):
        logger.info("Scheduler de ingesta IMAP desactivado (EMAIL_INGEST_ENABLED=false).")
        return
    interval_sec_env = os.getenv("EMAIL_INGEST_INTERVAL_SEC")
    if interval_sec_env:
        interval_sec = int(interval_sec_env)
    else:
        interval_sec = int(os.getenv("EMAIL_INGEST_INTERVAL_MIN", "5")) * 60
    _email_scheduler = BackgroundScheduler(timezone="UTC")
    _email_scheduler.add_job(
        _run_email_ingest,
        "interval",
        seconds=interval_sec,
        id="email_ingest",
        max_instances=1,
        coalesce=True,
    )
    _email_scheduler.start()
    logger.info("Scheduler de ingesta IMAP activado cada %s s.", interval_sec)


@app.on_event("shutdown")
def _stop_email_scheduler() -> None:
    global _email_scheduler
    if _email_scheduler is not None:
        _email_scheduler.shutdown(wait=False)
        _email_scheduler = None


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "pqrs-backend"}
