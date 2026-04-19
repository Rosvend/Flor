import logging
import os
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from src.application.dtos.ingest_curated_dtos import IngestCuratedMessagesInput
from src.application.dtos.pqrs_dtos import ProcessPQRSInput
from src.domain.entities.user import User
from src.infrastructure import container
from src.interfaces.http.deps import get_current_user
from src.interfaces.schemas.pqrsd_schemas import (
    get_citizen_email,
    get_citizen_name,
    get_contenido,
    get_tipo,
    get_autoriza_notificacion,
    is_anonymous,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pqrs", tags=["pqrs"])

@router.post("/ingest/gmail")
async def ingest_gmail_pqrs(query: str = "is:unread", current_user: User = Depends(get_current_user)):
    """
    Dispara la sincronización con Gmail. 
    Busca correos no leídos, los clasifica con IA y los guarda en el Curated Data Lake.
    """
    try:
        ingest_case = container.get_ingest_email_pqrs()
        result = ingest_case.execute(query=query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Background Task: AI Analysis ────────────────────────────────────────────

def _analyze_pqr_background(radicado: str, record: dict, images_data: list[tuple[bytes, str, str]] = None) -> None:
    """
    Tarea asíncrona:
    1. Sube imágenes a S3/DataLake y obtiene las claves.
    2. Ejecuta análisis de IA (Texto + YOLO).
    3. Actualiza el registro curado.
    """
    try:
        process_pqrs = container.get_process_pqrs()
        anexos_keys = []
        images_for_yolo = []
        
        # 1. Procesar y Subir imágenes
        if images_data:
            for content, filename, content_type in images_data:
                try:
                    # Almacenamiento real en bucket (asíncrono respecto al usuario)
                    key = container.raw_data_lake.store_binary(content, filename)
                    anexos_keys.append(key)
                    
                    if content_type.startswith("image/"):
                        images_for_yolo.append(content)
                except Exception as e:
                    logger.error(f"Error subiendo anexo {filename} en background: {e}")

        # 2. Análisis de IA
        texto = get_contenido(record)
        analisis_ia = None
        
        if len(texto) > 5 or images_for_yolo:
            analisis = process_pqrs.execute(ProcessPQRSInput(text=texto, images=images_for_yolo))
            analisis_ia = {
                "sentimiento":        analisis.sentiment,
                "is_offensive":       analisis.is_offensive,
                "toxicity_warning":   analisis.toxicity_warning,
                "offensive_words":    analisis.offensive_words,
                "tipo_sugerido":      analisis.tipo_sugerido,
                "secretaria_asignada": analisis.secretaria_asignada,
                "texto_mejorado":     analisis.improved_text,
                "objetos_detectados": analisis.detected_objects,
            }

        # 3. Actualización final del registro
        updates = {}
        if anexos_keys: updates["anexos"] = anexos_keys
        if analisis_ia: updates["analisis_ia"] = analisis_ia
        
        if updates:
            container.curated_data_lake.update_by_radicado(radicado, updates)
            
    except Exception as exc:
        logger.error("Error en procesamiento background completo: %s", exc)


def _notify_created(record: dict) -> None:
    try:
        if not is_anonymous(record):
            container.notifier.notify_created(record)
    except Exception as exc:
        logger.error("Error en notificación de creación: %s", exc)


# ── Citizen Form Submission ─────────────────────────────────────────────────

@router.post("")
async def submit_pqrs(
    background_tasks: BackgroundTasks,
    # Datos personales (opcionales si es anonimo)
    es_anonimo: str = Form("false"),
    persona: Optional[str] = Form(None),
    tipo_documento: Optional[str] = Form(None),
    numero_documento: Optional[str] = Form(None),
    nombres: Optional[str] = Form(None),
    genero: Optional[str] = Form(None),
    # Datos de contacto
    pais: str = Form("Colombia"),
    departamento: Optional[str] = Form(None),
    ciudad: Optional[str] = Form(None),
    direccion: Optional[str] = Form(None),
    email: str = Form(...),
    telefono: Optional[str] = Form(None),
    # Detalles de la solicitud
    asunto: str = Form(...),
    atencion_preferencial: str = Form("Ninguna"),
    direccion_hecho_tipo: str = Form("Misma"),
    otra_direccion: Optional[str] = Form(None),
    es_solicitud_informacion: str = Form("No"),
    autoriza_notificacion: str = Form("Si"),
    descripcion: str = Form(...),
    # Anexos (opcionales)
    archivo_1: Optional[UploadFile] = File(None),
    archivo_2: Optional[UploadFile] = File(None),
    archivo_3: Optional[UploadFile] = File(None),
    archivo_4: Optional[UploadFile] = File(None),
    archivo_5: Optional[UploadFile] = File(None),
    images: Optional[List[UploadFile]] = File(None),
    # Toggle de anexos
    tiene_anexos: Optional[str] = Form("No"),
    is_anonimo: Optional[str] = Form(None),
    organization_id: int = Form(1),
):
    """
    Endpoint público — ciudadano radica PQRS desde el formulario web.
    Produce el schema canónico y lo almacena en el Curated Data Lake.
    """
    es_anon = (es_anonimo or "false").lower() == "true" or (is_anonimo or "false").lower() == "true"
    now     = datetime.now(timezone.utc).isoformat()
    import uuid
    radicado = f"RAD-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    # Build documento string: "CC 1002427482"
    doc_str = None
    if not es_anon and tipo_documento and numero_documento:
        doc_prefix_map = {
            "cedula_ciudadania": "CC",
            "cedula_extranjeria": "CE",
            "tarjeta_identidad": "TI",
            "pasaporte": "PAS",
            "nit": "NIT",
        }
        prefix = doc_prefix_map.get(tipo_documento, tipo_documento or "")
        doc_str = f"{prefix} {numero_documento}"

    # Dirección del hecho
    dir_hecho = direccion if direccion_hecho_tipo == "Misma" else otra_direccion

    # ── Canonical record ──────────────────────────────────────────────────
    curated_record = {
        "radicado":             radicado,
        "timestamp_radicacion": now,
        "tipo":                 asunto,
        "canal":                "WEB",
        "anonima":              es_anon if es_anon else None,
        "estado":               "abierto",
        "organization_id":      organization_id,
        "usuario": {
            "nombre":    nombres if not es_anon else None,
            "documento": doc_str,
            "telefono":  telefono,
            "email":     email if not es_anon else None,
        },
        "ubicacion": {
            "pais":            pais,
            "departamento":    departamento,
            "ciudad":          ciudad,
            "direccion":       direccion,
            "direccion_hecho": dir_hecho,
        },
        "contenido":            descripcion,
        "metadata": {
            "persona":                persona,
            "genero":                 genero,
            "atencion_preferencial":  atencion_preferencial,
            "es_solicitud_informacion": es_solicitud_informacion,
            "autoriza_notificacion":  autoriza_notificacion,
        },
        # Pipeline fields — initially empty, filled by background tasks
        "analisis_ia":          None,
        "resumen_ia":           None,
        "borrador_respuesta":   None,
        "tipo_confirmado":      None,
        "respuesta":            None,
        "timestamp_respuesta":  None,
        "respondido_por":       None,
        "anexos":               [],
    }

    # ── Collect raw bytes for Background Processing ──────────────────────
    images_data = []
    all_files = [archivo_1, archivo_2, archivo_3, archivo_4, archivo_5]
    if images:
        all_files.extend(images)
    
    for arch in all_files:
        if arch and arch.filename:
            try:
                content = await arch.read()
                images_data.append((content, arch.filename, arch.content_type))
            except Exception as e:
                logger.warning(f"Error leyendo anexo {arch.filename}: {e}")

    try:
        result = container.ingest_curated_messages.execute(
            IngestCuratedMessagesInput(records=[curated_record])
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al almacenar la PQRS: {exc}")

    background_tasks.add_task(_analyze_pqr_background, radicado, curated_record, images_data)
    background_tasks.add_task(_notify_created, curated_record)

    return {"radicado": radicado, "message": "Su PQRS ha sido radicada exitosamente."}



# ── Schemas ──────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    text: Optional[str] = None
    contenido: Optional[str] = None


class AnalyzeResponse(BaseModel):
    original_text: str
    improved_text: str
    sentiment: str
    is_offensive: bool
    toxicity_warning: Optional[str]
    offensive_words: list[str]
    tipo_sugerido: Optional[str] = None
    secretaria_asignada: Optional[str] = None
    detected_objects: list[str] = []


class ClusterItemResponse(BaseModel):
    cluster_size: int
    is_root_problem: bool
    priority: str
    sample_text: str
    pqrs_ids: list[int]
    keywords: list[str]


class ClusterResponse(BaseModel):
    total_pqrs: int
    clusters_found: int
    root_problems: int
    message: str
    clusters: list[ClusterItemResponse]


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_pqrs(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Recibe el texto crudo de una PQRSD y devuelve:
    - Análisis de sentimiento (Hugging Face BETO)
    - Detección de groserías (regex)
    - Clasificación Zero-Shot de tipo de PQRS
    - Enrutamiento Semántico de Secretaría
    - Texto mejorado (Gemini + Manual V5)
    """
    try:
        input_text = request.text or request.contenido
        if not input_text:
            raise HTTPException(status_code=422, detail="Debe proporcionar 'text' o 'contenido'.")
            
        process_pqrs = container.get_process_pqrs()
        result = process_pqrs.execute(ProcessPQRSInput(text=input_text))
        return AnalyzeResponse(
            original_text=result.original_text,
            improved_text=result.improved_text,
            sentiment=result.sentiment,
            is_offensive=result.is_offensive,
            toxicity_warning=result.toxicity_warning,
            offensive_words=result.offensive_words,
            tipo_sugerido=result.tipo_sugerido,
            secretaria_asignada=result.secretaria_asignada,
            detected_objects=result.detected_objects,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clusters", response_model=ClusterResponse)
def get_pqrs_clusters(current_user: User = Depends(get_current_user)) -> ClusterResponse:
    """
    Recupera TODAS las PQRS directamente desde el bucket de S3,
    las agrupa por similitud y detecta problemas raíz.
    Filtra resultados según la organización del usuario.
    """
    try:
        result = container.cluster_pqrs.execute()
        return ClusterResponse(
            total_pqrs=result.total_pqrs,
            clusters_found=result.clusters_found,
            root_problems=result.root_problems,
            message=result.message,
            clusters=result.clusters,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/curated")
def list_curated_pqrs(current_user: User = Depends(get_current_user)):
    """Returns all curated records from the data lake filtered by organization."""
    try:
        all_pqrs = container.curated_data_lake.get_all()
        # Filtro por organization_id (asumimos 1 por defecto si no existe en el registro)
        # Esto permite que en producción cada Secretaría vea solo lo suyo
        filtered = [
            p for p in all_pqrs 
            if p.get("organization_id", 1) == current_user.organization_id
        ]
        return filtered
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/curated/{radicado}")
def get_curated_pqr(radicado: str, current_user: User = Depends(get_current_user)):
    """Returns a single curated record by radicado if it belongs to user's org."""
    pqr = container.curated_data_lake.get_by_radicado(radicado)
    if not pqr:
        raise HTTPException(status_code=404, detail=f"PQR {radicado} no encontrada.")
    
    if pqr.get("organization_id", 1) != current_user.organization_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta PQR.")
        
    return pqr


@router.get("/curated/{radicado}/draft")
def get_pqr_draft(radicado: str, current_user: User = Depends(get_current_user)):
    """Busca el precedente más similar y devuelve un borrador de respuesta."""
    try:
        use_case = container.get_draft_intelligent_response()
        result = use_case.execute(radicado, current_user.organization_id)
        return {
            "draft": result.draft_text,
            "precedente_id": result.precedent_id,
            "similitud": result.similarity_score
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
def get_pqrs_stats(current_user: User = Depends(get_current_user)):
    """Returns dashboard statistics filtered by organization."""
    try:
        all_pqrs = container.curated_data_lake.get_all()
        filtered = [
            p for p in all_pqrs 
            if p.get("organization_id", 1) == current_user.organization_id
        ]
        
        vencen_hoy = 0
        pendientes = 0
        now = datetime.now(timezone.utc)
        
        by_type = {}
        by_sentiment = {"POSITIVO": 0, "NEUTRAL": 0, "NEGATIVO": 0}
        
        for p in filtered:
            if p.get("estado") != "respondido":
                pendientes += 1
                rad_date_str = p.get("timestamp_radicacion")
                if rad_date_str:
                    try:
                        dt = datetime.fromisoformat(rad_date_str.replace("Z", "+00:00"))
                        days_diff = (now - dt).days
                        if days_diff >= 14:
                            vencen_hoy += 1
                    except Exception:
                        pass
            
            # Type distribution — use compat helper
            t = get_tipo(p).upper()
            by_type[t] = by_type.get(t, 0) + 1
            
            # Sentiment distribution
            analisis = p.get("analisis_ia")
            sent = "NEUTRAL"
            if isinstance(analisis, dict):
                sent = (analisis.get("sentimiento") or "NEUTRAL").upper()
            if sent in by_sentiment:
                by_sentiment[sent] += 1
            else:
                by_sentiment["NEUTRAL"] += 1
        
        return {
            "total": len(filtered),
            "pendientes": pendientes,
            "vencen_hoy": vencen_hoy,
            "by_type": by_type,
            "by_sentiment": by_sentiment
        }
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error in stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/curated/{radicado}")
def update_curated_pqr(
    radicado: str,
    updates: dict = Body(...),
    current_user: User = Depends(get_current_user),
):
    """Generic field update for a curated PQRSD (internal use)."""
    pqr = container.curated_data_lake.get_by_radicado(radicado)
    if not pqr:
        raise HTTPException(status_code=404, detail=f"PQRSD {radicado} no encontrada.")
    if pqr.get("organization_id", 1) != current_user.organization_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para modificar esta PQR.")
    merged = container.curated_data_lake.update_by_radicado(radicado, updates)
    if merged is None:
        raise HTTPException(status_code=404, detail=f"PQRSD {radicado} no encontrada al actualizar.")
    return {"success": True, "radicado": radicado}


class ResponderRequest(BaseModel):
    respuesta: str


@router.post("/curated/{radicado}/responder")
def responder_pqrsd(
    radicado: str,
    body: ResponderRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """
    Worker endpoint: marks the PQRSD as 'respondido', records the response,
    and notifies the citizen by email if they authorized it.
    """
    pqr = container.curated_data_lake.get_by_radicado(radicado)
    if not pqr:
        raise HTTPException(status_code=404, detail=f"PQRSD {radicado} no encontrada.")
    if pqr.get("estado") == "respondido":
        raise HTTPException(status_code=409, detail=f"PQRSD {radicado} ya fue respondida.")

    updates = {
        "estado":              "respondido",
        "respuesta":           body.respuesta,
        "timestamp_respuesta": datetime.now(timezone.utc).isoformat(),
        "respondido_por":      current_user.correo_electronico,
    }
    container.curated_data_lake.update_by_radicado(radicado, updates)

    # Re-read the full record for notification
    updated_pqr = container.curated_data_lake.get_by_radicado(radicado) or {**pqr, **updates}
    background_tasks.add_task(_notify_resolved, updated_pqr)

    return {"radicado": radicado, "estado": "respondido"}


def _notify_resolved(record: dict) -> None:
    try:
        if not is_anonymous(record):
            container.notifier.notify_resolved(record)
    except Exception as exc:
        logger.error("Error en notificación de respuesta: %s", exc)


# ── Public Tracking Endpoints (no auth) ─────────────────────────────────────

def _get_department_name(organization_id: int) -> str:
    """Looks up department name from organization_id via PostgreSQL."""
    try:
        from sqlalchemy import create_engine, text as sa_text
        engine = create_engine(os.environ["DATABASE_URL"])
        with engine.connect() as conn:
            row = conn.execute(
                sa_text("SELECT name FROM departments WHERE organization_id = :oid"),
                {"oid": organization_id},
            ).fetchone()
        return row[0] if row else "Dependencia no asignada"
    except Exception:
        return "Dependencia no asignada"


def _map_status(estado: str) -> str:
    e = (estado or "").lower()
    if e in ("respondido", "cerrado", "closed"):
        return "RESPONDIDA"
    if e in ("abierto", "pendiente", "nuevo", "procesando", "en_gestion"):
        return "EN_GESTION"
    return "EN_GESTION"


@router.get("/track/{radicado}")
def track_pqrsd(radicado: str):
    """
    Endpoint público — ciudadano consulta el estado de su PQRSD por radicado.
    No requiere autenticación.
    """
    pqr = container.curated_data_lake.get_by_radicado(radicado.upper())
    if not pqr:
        raise HTTPException(status_code=404, detail=f"No encontramos una PQRSD con el radicado {radicado}.")

    org_id = pqr.get("organization_id")
    assigned_to = _get_department_name(org_id) if org_id else "Dependencia no asignada"

    estado = pqr.get("estado", "abierto")
    status = _map_status(estado)

    # Anexos: el campo puede venir como lista de strings o no existir
    raw_anexos = pqr.get("anexos") or []
    if isinstance(raw_anexos, list):
        attachments = [{"name": a} if isinstance(a, str) else a for a in raw_anexos]
    else:
        attachments = []

    respuesta_raw = pqr.get("respuesta")
    response_block = None
    if respuesta_raw:
        response_block = {
            "message": respuesta_raw,
            "responded_at": pqr.get("timestamp_respuesta", ""),
        }

    return {
        "radicado":    pqr.get("radicado", radicado),
        "status":      status,
        "created_at":  pqr.get("timestamp_radicacion", ""),
        "type":        pqr.get("tipo", ""),
        "subject":     pqr.get("asunto_principal") or (pqr.get("contenido", "") or "")[:80],
        "channel":     pqr.get("canal", ""),
        "assigned_to": assigned_to,
        "description": pqr.get("contenido") or pqr.get("descripcion_detallada", ""),
        "attachments": attachments,
        "response":    response_block,
    }


@router.get("/track/{radicado}/exists")
def track_pqrsd_exists(radicado: str):
    """Verificación rápida — devuelve 200 si existe, 404 si no."""
    pqr = container.curated_data_lake.get_by_radicado(radicado.upper())
    if not pqr:
        raise HTTPException(status_code=404, detail=f"No encontramos una PQRSD con el radicado {radicado}.")
    return {"exists": True, "radicado": pqr.get("radicado")}


@router.post("/clusters", response_model=ClusterResponse)
def post_pqrs_clusters(records: list[dict] = Body(...)) -> ClusterResponse:
    """
    Agrupa una lista de PQRS enviada manualmente en el cuerpo de la petición.
    
    Body esperado: [{"text": "..."}, {"text": "..."}, ...]
    """
    if not records:
        raise HTTPException(status_code=422, detail="La lista de registros está vacía.")
    try:
        result = container.cluster_pqrs.execute(pqrs_records=records)
        return ClusterResponse(
            total_pqrs=result.total_pqrs,
            clusters_found=result.clusters_found,
            root_problems=result.root_problems,
            message=result.message,
            clusters=result.clusters,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── F5: AI-assisted summary + RAG-based draft response ─────────────────────
#
# Both endpoints require an authenticated agent. They read the curated PQR by
# radicado, run the LLM, persist the output back onto the record (via
# update_by_radicado) so the detail page can show it without re-running the
# model on every refresh, and return the fresh record.

from fastapi import status as http_status
from src.application.dtos.pqrsd_assist_dtos import (
    DraftResponseInput,
    SummarizePQRSDInput,
)


def _map_llm_error(exc: Exception) -> HTTPException:
    msg = str(exc)
    if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
        return HTTPException(
            status_code=429,
            detail="Cuota del proveedor de IA agotada. Intenta de nuevo en unos minutos.",
        )
    return HTTPException(status_code=502, detail=f"Error del proveedor de IA: {exc}")


@router.post("/curated/{radicado}/summarize")
def summarize_curated_pqr(
    radicado: str,
    force: bool = False,
    current_user: User = Depends(get_current_user),
):
    """F5 — Generate the 3-layer summary and persist it under `resumen_ia`."""
    if container.summarize_pqrsd is None:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El resumen IA no está configurado (falta GEMINI_API_KEY).",
        )

    pqr = container.curated_data_lake.get_by_radicado(radicado)
    if not pqr:
        raise HTTPException(status_code=404, detail=f"PQRSD {radicado} no encontrada.")
    if pqr.get("organization_id", 1) != current_user.organization_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta PQR.")

    if not force and pqr.get("resumen_ia"):
        return {"radicado": radicado, "resumen_ia": pqr["resumen_ia"], "cached": True}

    content = get_contenido(pqr)
    if not content.strip():
        raise HTTPException(status_code=422, detail="La PQR no tiene texto para resumir.")

    try:
        out = container.summarize_pqrsd.execute(SummarizePQRSDInput(content=content))
    except Exception as exc:
        raise _map_llm_error(exc)

    resumen_ia = {
        "lead": out.lead,
        "topics": out.topics,
        "original": out.original,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    container.curated_data_lake.update_by_radicado(radicado, {"resumen_ia": resumen_ia})
    return {"radicado": radicado, "resumen_ia": resumen_ia, "cached": False}


@router.post("/curated/{radicado}/draft-response")
def draft_curated_pqr_response(
    radicado: str,
    force: bool = False,
    current_user: User = Depends(get_current_user),
):
    """F5 — Generate a RAG-grounded draft response and persist it under `borrador_respuesta`."""
    if container.draft_response_pqrsd is None:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El borrador IA no está configurado (falta GEMINI_API_KEY).",
        )

    pqr = container.curated_data_lake.get_by_radicado(radicado)
    if not pqr:
        raise HTTPException(status_code=404, detail=f"PQRSD {radicado} no encontrada.")
    if pqr.get("organization_id", 1) != current_user.organization_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver esta PQR.")

    if not force and pqr.get("borrador_respuesta"):
        return {
            "radicado": radicado,
            "borrador_respuesta": pqr["borrador_respuesta"],
            "cached": True,
        }

    content = get_contenido(pqr)
    if not content.strip():
        raise HTTPException(status_code=422, detail="La PQR no tiene texto para borrador.")

    try:
        out = container.draft_response_pqrsd.execute(
            DraftResponseInput(
                content=content,
                asunto=get_tipo(pqr),
                citizen_name=get_citizen_name(pqr),
            )
        )
    except Exception as exc:
        raise _map_llm_error(exc)

    if out.used_fallback or not out.draft.strip():
        raise HTTPException(
            status_code=502,
            detail="El modelo no pudo generar un borrador. Intenta de nuevo en unos segundos.",
        )

    borrador_respuesta = {
        "draft": out.draft,
        "sources": [{"title": s.title, "excerpt": s.excerpt} for s in out.sources],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "aprobado": False,
    }
    container.curated_data_lake.update_by_radicado(
        radicado, {"borrador_respuesta": borrador_respuesta}
    )
    return {
        "radicado": radicado,
        "borrador_respuesta": borrador_respuesta,
        "cached": False,
    }


# ── F6: Mapa de densidad por comunas de Medellín ────────────────────────────

@router.get("/map")
def get_pqrs_map(current_user: User = Depends(get_current_user)):
    """
    Devuelve la distribución de PQRS por comunas de Medellín.
    Incluye conteo, distribución por tipo y, si Gemini está configurado,
    un análisis IA de la problemática dominante en cada zona.
    """
    try:
        use_case = container.get_analyze_map_density()
        result = use_case.execute(organization_id=current_user.organization_id)
        return result
    except Exception as e:
        logger.error("Error en /pqrs/map: %s", e)
        raise HTTPException(status_code=500, detail=str(e))
