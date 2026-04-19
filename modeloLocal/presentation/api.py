from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ..application.use_cases import ProcessPQRSUseCase
from ..application.cluster_use_case import ClusterPQRSUseCase

router = APIRouter()
process_use_case = ProcessPQRSUseCase()
cluster_use_case = ClusterPQRSUseCase()

class PQRSRequest(BaseModel):
    text: str

class PQRSResponse(BaseModel):
    id: int
    original_text: str
    improved_text: str
    sentiment: str
    is_offensive: bool
    toxicity_warning: Optional[str]

class ClusterItem(BaseModel):
    cluster_size: int
    is_root_problem: bool
    priority: str
    sample_text: str
    pqrs_ids: List[int]
    keywords: List[str]

class ClusterResponse(BaseModel):
    total_pqrs: int
    clusters_found: int
    root_problems: int
    message: str
    clusters: List[ClusterItem]

@router.post("/process_pqrs", response_model=PQRSResponse)
def process_pqrs(request: PQRSRequest):
    try:
        result, toxicity = process_use_case.execute(request.text)
        return PQRSResponse(
            id=result.id,
            original_text=result.original_text,
            improved_text=result.improved_text,
            sentiment=result.sentiment,
            is_offensive=toxicity["is_offensive"],
            toxicity_warning=toxicity["warning"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pqrs", response_model=List[PQRSResponse])
def list_pqrs():
    items = process_use_case.get_all()
    return [
        PQRSResponse(
            id=i.id,
            original_text=i.original_text,
            improved_text=i.improved_text,
            sentiment=i.sentiment,
            is_offensive=bool(i.is_offensive),
            toxicity_warning=i.toxicity_warning
        ) for i in items
    ]

@router.get("/pqrs/clusters", response_model=ClusterResponse)
def get_clusters():
    """Analiza todas las PQRS almacenadas, agrupa las similares y detecta problemas raíz (>20 PQRS parecidas)."""
    try:
        result = cluster_use_case.execute()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
