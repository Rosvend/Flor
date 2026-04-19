from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.application.dtos.pqrs_dtos import ProcessPQRSInput
from src.infrastructure import container

router = APIRouter(prefix="/pqrs", tags=["pqrs"])


# ── Schemas ──────────────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    text: str


class AnalyzeResponse(BaseModel):
    original_text: str
    improved_text: str
    sentiment: str
    is_offensive: bool
    toxicity_warning: Optional[str]
    offensive_words: list[str]


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
    - Texto mejorado (Gemini + Manual V5)
    """
    try:
        process_pqrs = container.get_process_pqrs()
        result = process_pqrs.execute(ProcessPQRSInput(text=request.text))
        return AnalyzeResponse(
            original_text=result.original_text,
            improved_text=result.improved_text,
            sentiment=result.sentiment,
            is_offensive=result.is_offensive,
            toxicity_warning=result.toxicity_warning,
            offensive_words=result.offensive_words,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clusters", response_model=ClusterResponse)
def cluster_pqrs(records: list[dict] = Body(...)) -> ClusterResponse:
    """
    Recibe una lista de PQRS (desde S3 u otra fuente) y agrupa las similares.
    Detecta problemas raíz cuando un grupo supera las 20 PQRS.
    
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
