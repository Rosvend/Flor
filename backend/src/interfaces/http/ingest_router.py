from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from src.application.dtos.ingest_dtos import IngestRawMessagesInput
from src.infrastructure import container

router = APIRouter(prefix="/ingest", tags=["ingest"])


class IngestRawResponse(BaseModel):
    count: int
    stored_keys: list[str]


@router.post("/raw", response_model=IngestRawResponse, status_code=201)
def ingest_raw(records: list[dict] = Body(...)) -> IngestRawResponse:
    """
    Receives raw records from any source (Meta API, scraping, etc.)
    and stores them as-is in S3. No transformation, no classification.
    """
    if not records:
        raise HTTPException(status_code=422, detail="records list is empty")

    result = container.ingest_raw_messages.execute(
        IngestRawMessagesInput(records=records)
    )
    return IngestRawResponse(count=result.count, stored_keys=result.stored_keys)
