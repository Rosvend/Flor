from __future__ import annotations

import hashlib
from pathlib import Path

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

from ...domain.entities.knowledge_base_entry import KnowledgeBaseEntry

HEADERS_TO_SPLIT_ON = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]
OVERSIZED_CHUNK_CHARS = 1200
RECURSIVE_CHUNK_SIZE = 1000
RECURSIVE_CHUNK_OVERLAP = 150


def _stable_id(*parts: str) -> str:
    h = hashlib.sha256("||".join(parts).encode("utf-8")).hexdigest()
    return h[:16]


def _heading_path(meta: dict[str, str]) -> tuple[str, ...]:
    return tuple(meta[key] for key in ("h1", "h2", "h3") if meta.get(key))


def _with_breadcrumb(heading_path: tuple[str, ...], body: str) -> str:
    if not heading_path:
        return body
    return f"{' > '.join(heading_path)}\n\n{body}"


def chunk_markdown(
    md_path: Path,
    source_pdf: str,
    extra_metadata: dict[str, str] | None = None,
) -> list[KnowledgeBaseEntry]:
    """Split a markdown file into heading-aware chunks.

    Headings carry the semantic boundaries; oversized sections are split further
    via a character-based recursive splitter."""
    text = md_path.read_text(encoding="utf-8")
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,
    )
    sections = header_splitter.split_text(text)

    recursive = RecursiveCharacterTextSplitter(
        chunk_size=RECURSIVE_CHUNK_SIZE,
        chunk_overlap=RECURSIVE_CHUNK_OVERLAP,
    )

    source_path = str(md_path)
    base_meta = {"source_pdf": source_pdf, **(extra_metadata or {})}
    entries: list[KnowledgeBaseEntry] = []

    for section in sections:
        heading_path = _heading_path(section.metadata)
        body = section.page_content.strip()
        if not body:
            continue
        pieces = (
            recursive.split_text(body)
            if len(body) > OVERSIZED_CHUNK_CHARS
            else [body]
        )
        for piece in pieces:
            piece = piece.strip()
            if not piece:
                continue
            content = _with_breadcrumb(heading_path, piece)
            entry_id = _stable_id(source_path, " > ".join(heading_path), piece)
            entries.append(
                KnowledgeBaseEntry(
                    id=entry_id,
                    source_path=source_path,
                    heading_path=heading_path,
                    content=content,
                    metadata=base_meta,
                )
            )
    return entries
