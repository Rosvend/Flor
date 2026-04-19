from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from fastapi import Body

from src.application.dtos.ingest_curated_dtos import IngestCuratedMessagesInput
from src.infrastructure import container
from src.interfaces.schemas.pqrsd_schemas import get_contenido, is_anonymous

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestCuratedResponse(BaseModel):
    count: int
    stored_keys: list[str]


def _ai_and_notify(keys: list[str], records: list[dict]) -> None:
    try:
        process_pqrs = container.get_process_pqrs()
        for key, record in zip(keys, records):
            texto = get_contenido(record)
            if len(texto) > 5:
                from src.application.dtos.pqrs_dtos import ProcessPQRSInput
                analisis = process_pqrs.execute(ProcessPQRSInput(text=texto))
                record["analisis_ia"] = {
                    "sentimiento":        analisis.sentiment,
                    "is_offensive":       analisis.is_offensive,
                    "toxicity_warning":   analisis.toxicity_warning,
                    "offensive_words":    analisis.offensive_words,
                    "tipo_sugerido":      analisis.tipo_sugerido,
                    "secretaria_asignada": analisis.secretaria_asignada,
                    "texto_mejorado":     analisis.improved_text,
                }
                container.curated_data_lake.update_by_radicado(record["radicado"], record)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("Error en análisis IA background: %s", exc)


@router.post("/curated", response_model=IngestCuratedResponse, status_code=201)
def ingest_curated(
    records: list[dict] = Body(...),
    background_tasks: BackgroundTasks = None,
) -> IngestCuratedResponse:
    """
    Receives curated PQRSDs in the unified format and stores them in S3.
    Generates radicado (RAD-YYYYMMDD-XXXXXXXX) and timestamp if missing.
    Auto-assigns estado=abierto.
    """
    if not records:
        raise HTTPException(status_code=422, detail="records list is empty")

    now = datetime.now(timezone.utc).isoformat()
    record_dicts: list[dict] = []

    for r in records:
        if not r.get("radicado"):
            r["radicado"] = container.curated_data_lake.next_radicado()
        if not r.get("timestamp_radicacion"):
            r["timestamp_radicacion"] = now
        if not r.get("estado"):
            r["estado"] = "abierto"
        if "respuesta" not in r:
            r["respuesta"] = None
        record_dicts.append(r)

    result = container.ingest_curated_messages.execute(
        IngestCuratedMessagesInput(records=record_dicts)
    )

    # Background: AI analysis + email notification on creation
    background_tasks.add_task(_ai_and_notify, result.stored_keys, record_dicts)
    background_tasks.add_task(_notify_created_batch, record_dicts)

    return IngestCuratedResponse(count=result.count, stored_keys=result.stored_keys)


def _notify_created_batch(records: list[dict]) -> None:
    try:
        for record in records:
            if not is_anonymous(record):
                container.notifier.notify_created(record)
    except Exception as exc:
        import logging
        logging.getLogger(__name__).error("Error en notificación de creación: %s", exc)
