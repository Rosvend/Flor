import uuid
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/ingest", tags=["ingest"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class MetaUser(BaseModel):
    nombre: str | None = None
    id_meta: str


class MetaMetadata(BaseModel):
    post_id: str | None = None
    created_time: str


class RawMetaItem(BaseModel):
    canal: str          # META_DM | META_COMMENT
    usuario: MetaUser
    contenido: str
    metadata: MetaMetadata


class RawMetaRecord(BaseModel):
    id: str
    ingested_at: str
    canal: str
    usuario: MetaUser
    contenido: str
    metadata: MetaMetadata


# ── Endpoint ──────────────────────────────────────────────────────────────────

@router.post("/meta/raw", response_model=list[RawMetaRecord], status_code=201)
def ingest_meta_raw(items: list[RawMetaItem]) -> list[RawMetaRecord]:
    """
    Receives ALL Meta messages (DMs + comments) from the last 24 h, unfiltered.
    No classification here — a separate job will determine which are PQRS.
    """
    ingested_at = datetime.now(timezone.utc).isoformat()

    return [
        RawMetaRecord(
            id=str(uuid.uuid4()),
            ingested_at=ingested_at,
            canal=item.canal,
            usuario=item.usuario,
            contenido=item.contenido,
            metadata=item.metadata,
        )
        for item in items
    ]
