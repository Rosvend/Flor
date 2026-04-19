from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from src.domain.ports.document_ingestion_port import DocumentIngestionPort
from src.domain.ports.knowledge_base_port import KnowledgeBasePort

from .chunker import chunk_markdown
from .pdf_to_markdown import convert as pdf_to_markdown

logger = logging.getLogger(__name__)

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def _safe_filename(name: str) -> str:
    cleaned = _SAFE_NAME.sub("_", name).strip("._-")
    return cleaned or "upload"


class UnsupportedFileTypeError(ValueError):
    pass


class DocumentIngestionService(DocumentIngestionPort):
    """Persists an uploaded file, runs it through the existing PDF→MD→chunk
    pipeline, and upserts the chunks into the knowledge base."""

    def __init__(
        self,
        knowledge_base: KnowledgeBasePort,
        uploads_dir: Path,
        markdown_dir: Path,
    ) -> None:
        self._kb = knowledge_base
        self._uploads_dir = uploads_dir
        self._markdown_dir = markdown_dir
        self._uploads_dir.mkdir(parents=True, exist_ok=True)
        self._markdown_dir.mkdir(parents=True, exist_ok=True)

    def ingest(self, filename: str, content: bytes, uploaded_by: str) -> tuple[int, str]:
        safe_name = _safe_filename(filename)
        suffix = Path(safe_name).suffix.lower()
        if suffix not in {".pdf", ".md"}:
            raise UnsupportedFileTypeError(
                f"Unsupported file type {suffix!r}; only .pdf and .md are accepted."
            )

        upload_path = self._uploads_dir / safe_name
        upload_path.write_bytes(content)

        if suffix == ".pdf":
            md_path = pdf_to_markdown(upload_path, self._markdown_dir, force=True)
        else:
            md_path = self._markdown_dir / f"{upload_path.stem}.md"
            md_path.write_bytes(content)

        extra_meta = {
            "visibility": "public",
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "uploaded_by": uploaded_by,
        }
        entries = chunk_markdown(md_path, source_pdf=safe_name, extra_metadata=extra_meta)
        if not entries:
            logger.warning("No chunks produced from %s", safe_name)
            return 0, str(md_path)

        self._kb.upsert(entries)
        logger.info("Indexed %d chunks from %s (uploaded by %s)", len(entries), safe_name, uploaded_by)
        return len(entries), str(md_path)
