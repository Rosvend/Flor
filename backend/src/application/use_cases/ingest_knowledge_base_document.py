from src.application.dtos.chatbot_dtos import IngestDocumentInput, IngestDocumentOutput
from src.domain.ports.document_ingestion_port import DocumentIngestionPort


class IngestKnowledgeBaseDocument:
    def __init__(self, ingestion: DocumentIngestionPort) -> None:
        self._ingestion = ingestion

    def execute(self, input_dto: IngestDocumentInput) -> IngestDocumentOutput:
        chunks, source_path = self._ingestion.ingest(
            filename=input_dto.filename,
            content=input_dto.content,
            uploaded_by=input_dto.uploaded_by,
        )
        return IngestDocumentOutput(chunks_indexed=chunks, source_path=source_path)
