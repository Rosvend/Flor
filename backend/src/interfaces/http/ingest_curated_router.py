import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.application.dtos.ingest_curated_dtos import IngestCuratedMessagesInput
from src.infrastructure import container

router = APIRouter(prefix="/ingest", tags=["ingest"])


class CuratedUsuario(BaseModel):
    nombre: str | None = None
    id_meta: str | None = None
    documento: str | None = None
    telefono: str | None = None


class CuratedMetadata(BaseModel):
    post_id: str | None = None
    created_time: str | None = None


class CuratedRecord(BaseModel):
    radicado: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_radicacion: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    tipo: str
    canal: str
    anonima: bool
    usuario: CuratedUsuario
    contenido: str
    metadata: CuratedMetadata = Field(default_factory=CuratedMetadata)


class IngestCuratedResponse(BaseModel):
    count: int
    stored_keys: list[str]


@router.post("/curated", response_model=IngestCuratedResponse, status_code=201)
def ingest_curated(records: list[CuratedRecord]) -> IngestCuratedResponse:
    """
    Receives curated records with the unified data-lake schema and stores them in S3.
    Generates radicado and timestamp_radicacion if not provided.
    """
    if not records:
        raise HTTPException(status_code=422, detail="records list is empty")

    result = container.ingest_curated_messages.execute(
        IngestCuratedMessagesInput(records=[r.model_dump() for r in records])
    )
    return IngestCuratedResponse(count=result.count, stored_keys=result.stored_keys)
