from abc import ABC, abstractmethod


class DocumentIngestionPort(ABC):
    @abstractmethod
    def ingest(self, filename: str, content: bytes, uploaded_by: str) -> tuple[int, str]:
        """Persist the upload, convert to chunks, and store in the knowledge base.

        Returns (chunks_indexed, source_path)."""
        ...
