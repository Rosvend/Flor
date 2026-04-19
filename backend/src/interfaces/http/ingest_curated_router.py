import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from src.application.dtos.ingest_curated_dtos import IngestCuratedMessagesInput
from src.application.dtos.pqrs_dtos import ProcessPQRSInput
from src.infrastructure import container

router = APIRouter(prefix="/ingest", tags=["ingest"])


class CuratedCiudadano(BaseModel):
    tipo_persona: str                    # natural | juridica
    tipo_documento: str                  # cedula_ciudadania | cedula_extranjeria | tarjeta_identidad | pasaporte | nit
    numero_documento: str
    nombres: str
    apellidos: str
    genero: str                          # masculino | femenino | no_binario | prefiero_no_decirlo | otro
    pais: str = "Colombia"
    departamento: str
    ciudad: str
    direccion: str | None = None
    correo_electronico: str | None = None
    telefono: str | None = None
    id_meta: str | None = None           # presente si viene de canal Meta


class CuratedMetadata(BaseModel):
    post_id: str | None = None
    created_time: str | None = None


class CuratedRecord(BaseModel):
    radicado: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_radicacion: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    canal: str
    anonima: bool
    ciudadano: CuratedCiudadano
    asunto_principal: str                # peticion | queja | reclamo | solicitud | denuncia
    atencion_preferencial: str = "ninguna"  # ninguna | adulto_mayor | persona_con_discapacidad | mujer_embarazada | victima_conflicto | otro
    autoriza_notificacion_correo: bool
    descripcion_detallada: str
    metadata: CuratedMetadata = Field(default_factory=CuratedMetadata)


class IngestCuratedResponse(BaseModel):
    count: int
    stored_keys: list[str]


def analyze_and_update_records(keys: list[str], records: list[dict]):
    """Background task to run the heavy AI process on each new record."""
    try:
        process_pqrs = container.get_process_pqrs()
        for key, record in zip(keys, records):
            texto = record.get("descripcion_detallada", "")
            if len(texto) > 5:
                analisis = process_pqrs.execute(ProcessPQRSInput(text=texto))
                record["analisis_ia"] = {
                    "sentimiento": analisis.sentiment,
                    "is_offensive": analisis.is_offensive,
                    "toxicity_warning": analisis.toxicity_warning,
                    "offensive_words": analisis.offensive_words,
                    "tipo_sugerido": analisis.tipo_sugerido,
                    "secretaria_asignada": analisis.secretaria_asignada,
                    "texto_mejorado": analisis.improved_text
                }
                # Actualizamos el archivo en S3 con los nuevos datos de IA
                container.curated_data_lake.update(key, record)
    except Exception as e:
        print(f"Error en análisis en segundo plano: {e}")


@router.post("/curated", response_model=IngestCuratedResponse, status_code=201)
def ingest_curated(records: list[CuratedRecord], background_tasks: BackgroundTasks) -> IngestCuratedResponse:
    """
    Receives curated records with the unified data-lake schema and stores them in S3.
    Generates radicado and timestamp_radicacion if not provided.
    Automatically triggers a background task to process the records with IA.
    """
    if not records:
        raise HTTPException(status_code=422, detail="records list is empty")

    record_dicts = [r.model_dump() for r in records]
    result = container.ingest_curated_messages.execute(
        IngestCuratedMessagesInput(records=record_dicts)
    )
    
    # Encolar análisis de IA para no bloquear al usuario
    background_tasks.add_task(analyze_and_update_records, result.stored_keys, record_dicts)
    
    return IngestCuratedResponse(count=result.count, stored_keys=result.stored_keys)
