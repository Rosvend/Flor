from src.application.dtos.chatbot_dtos import IngestDocumentInput
from src.application.use_cases.ingest_knowledge_base_document import (
    IngestKnowledgeBaseDocument,
)


class StubIngestion:
    def __init__(self) -> None:
        self.calls: list[tuple[str, bytes, str]] = []

    def ingest(self, filename: str, content: bytes, uploaded_by: str) -> tuple[int, str]:
        self.calls.append((filename, content, uploaded_by))
        return 7, f"/tmp/{filename}.md"


def test_executes_ingestion_and_maps_output():
    stub = StubIngestion()
    uc = IngestKnowledgeBaseDocument(ingestion=stub)

    out = uc.execute(
        IngestDocumentInput(filename="manual.pdf", content=b"%PDF-1.4...", uploaded_by="u-42")
    )

    assert out.chunks_indexed == 7
    assert out.source_path == "/tmp/manual.pdf.md"
    assert stub.calls == [("manual.pdf", b"%PDF-1.4...", "u-42")]
