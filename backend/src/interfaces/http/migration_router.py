from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.infrastructure import container

router = APIRouter(prefix="/pqrs", tags=["pqrs", "migration"])


class MigrationResponse(BaseModel):
    total_raw_processed: int
    pqrs_found: int
    keys_migrated: list[str]


@router.post("/migrate-raw", response_model=MigrationResponse)
def migrate_raw_to_curated() -> MigrationResponse:
    """
    Procesa todos los mensajes crudos (raw) usando NLP (Hugging Face).
    Si detecta que el mensaje es una PQRS (Petición, Queja, Denuncia),
    lo mapea al formato CuratedRecord y lo ingesta en S3.
    Luego borra el mensaje original crudo.
    """
    try:
        migrate_uc = container.get_migrate_raw_to_curated()
        result = migrate_uc.execute()
        return MigrationResponse(
            total_raw_processed=result.total_raw_processed,
            pqrs_found=result.pqrs_found,
            keys_migrated=result.keys_migrated
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
