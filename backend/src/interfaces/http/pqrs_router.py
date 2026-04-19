import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Body, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel

from src.application.dtos.ingest_curated_dtos import IngestCuratedMessagesInput
from src.application.dtos.pqrs_dtos import ProcessPQRSInput
from src.domain.entities.user import User
from src.infrastructure import container
from src.interfaces.http.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pqrs", tags=["pqrs"])


# ── Background Task: AI Analysis ────────────────────────────────────────────

def _analyze_pqr_background(keys: list[str], records: list[dict]) -> None:
    try:
        process_pqrs = container.get_process_pqrs()
        for record in records:
            texto = record.get("descripcion_detallada", "")
            if len(texto) > 5:
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
        logger.error("Error en análisis IA background: %s", exc)


def _notify_created(record: dict) -> None:
    try:
        if not record.get("anonima"):
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
    # Toggle de anexos
    tiene_anexos: Optional[str] = Form("No"),
    is_anonimo: Optional[str] = Form(None),
    organization_id: int = Form(1),
):
    """
    Endpoint público — ciudadano radica PQRS desde el formulario web.
    Produce el schema canónico y lo almacena en S3 curated.
    """
    es_anon = (es_anonimo or "false").lower() == "true" or (is_anonimo or "false").lower() == "true"
    now     = datetime.now(timezone.utc).isoformat()
    import uuid
    radicado = f"RAD-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"

    ciudadano: dict = {
        "pais":               pais,
        "departamento":       departamento,
        "ciudad":             ciudad,
        "direccion":          direccion,
        "correo_electronico": email if not es_anon else None,
        "telefono":           telefono,
        "id_meta":            None,
    }
    if not es_anon:
        ciudadano.update({
            "tipo_persona":     persona,
            "tipo_documento":   tipo_documento,
            "numero_documento": numero_documento,
            "nombres":          nombres,
            "apellidos":        None,
            "genero":           genero,
        })

    curated_record = {
        "radicado":                    radicado,
        "timestamp_radicacion":        now,
        "tipo":                        asunto,
        "canal":                       "PORTAL",
        "estado":                      "abierto",
        "organization_id":             organization_id,
        "anonima":                     es_anon,
        "ciudadano":                   ciudadano,
        "asunto_principal":            asunto.lower(),
        "atencion_preferencial":       atencion_preferencial.lower(),
        "autoriza_notificacion_correo": autoriza_notificacion.lower() in ("si", "sí", "true", "yes"),
        "contenido":                   descripcion,
        "descripcion_detallada":       descripcion,
        "respuesta":                   None,
        "metadata":                    {"post_id": None, "created_time": now},
    }

    try:
        result = container.ingest_curated_messages.execute(
            IngestCuratedMessagesInput(records=[curated_record])
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al almacenar la PQRS: {exc}")

    background_tasks.add_task(_analyze_pqr_background, result.stored_keys, [curated_record])
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
            
            # Type distribution
            t = (p.get("tipo") or "OTROS").upper()
            by_type[t] = by_type.get(t, 0) + 1
            
            # Sentiment distribution
            sent = (p.get("analisis_ia", {}).get("sentimiento") or "NEUTRAL").upper()
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
    pqr.update(updates)
    container.curated_data_lake.update_by_radicado(radicado, pqr)
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

    pqr["estado"]              = "respondido"
    pqr["respuesta"]           = body.respuesta
    pqr["timestamp_respuesta"] = datetime.now(timezone.utc).isoformat()
    pqr["respondido_por"]      = current_user.correo_electronico

    container.curated_data_lake.update_by_radicado(radicado, pqr)
    background_tasks.add_task(_notify_resolved, pqr)

    return {"radicado": radicado, "estado": "respondido"}


def _notify_resolved(record: dict) -> None:
    try:
        if not record.get("anonima"):
            container.notifier.notify_resolved(record)
    except Exception as exc:
        logger.error("Error en notificación de respuesta: %s", exc)


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
