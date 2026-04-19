from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from src.application.dtos.chatbot_dtos import IngestDocumentInput, QueryChatbotInput
from src.infrastructure import container
from src.infrastructure.knowledge_base.document_ingestion_service import (
    UnsupportedFileTypeError,
)

from .dependencies import get_current_user_id

router = APIRouter(prefix="/chatbot", tags=["chatbot"])

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB


class ChatQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)


class ChatSourceResponse(BaseModel):
    title: str
    excerpt: str


class ChatQueryResponse(BaseModel):
    answer: str
    used_fallback: bool
    sources: list[ChatSourceResponse]


class IngestDocumentResponse(BaseModel):
    chunks_indexed: int
    source_path: str


@router.post("/query", response_model=ChatQueryResponse)
def query_chatbot(req: ChatQueryRequest) -> ChatQueryResponse:
    if container.query_flor_chatbot is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El chatbot no está configurado (falta GEMINI_API_KEY).",
        )
    result = container.query_flor_chatbot.execute(QueryChatbotInput(question=req.question))
    return ChatQueryResponse(
        answer=result.answer,
        used_fallback=result.used_fallback,
        sources=[ChatSourceResponse(title=s.title, excerpt=s.excerpt) for s in result.sources],
    )


@router.post(
    "/documents",
    response_model=IngestDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_document(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id),
) -> IngestDocumentResponse:
    if container.ingest_knowledge_base_document is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La ingesta de documentos no está configurada.",
        )
    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="El archivo está vacío.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"El archivo supera el límite de {MAX_UPLOAD_BYTES // (1024 * 1024)} MB.",
        )

    try:
        result = container.ingest_knowledge_base_document.execute(
            IngestDocumentInput(
                filename=file.filename or "upload",
                content=content,
                uploaded_by=user_id,
            )
        )
    except UnsupportedFileTypeError as exc:
        raise HTTPException(status_code=415, detail=str(exc))

    return IngestDocumentResponse(
        chunks_indexed=result.chunks_indexed,
        source_path=result.source_path,
    )
