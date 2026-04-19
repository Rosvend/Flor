from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from sentence_transformers import SentenceTransformer

from ...domain.entities.knowledge_base_entry import KnowledgeBaseEntry
from ...domain.ports.knowledge_base_port import KnowledgeBasePort

logger = logging.getLogger(__name__)

DEFAULT_COLLECTION = "pqrsd_knowledge_base"
DEFAULT_MODEL = "intfloat/multilingual-e5-base"


class _E5EmbeddingFunction(EmbeddingFunction[Documents]):
    """E5 models expect 'passage: ' on indexed docs and 'query: ' on queries.

    This wraps Chroma's expected interface so the collection's index is built
    with the correct prefix, while _query_embedding() below handles the other
    side."""

    def __init__(self, model_name: str = DEFAULT_MODEL):
        self._model = SentenceTransformer(model_name)

    def __call__(self, input: Documents) -> Embeddings:
        prefixed = [f"passage: {doc}" for doc in input]
        return self._model.encode(prefixed, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self._model.encode(
            [f"query: {text}"], normalize_embeddings=True
        )[0].tolist()


def _to_entry(doc_id: str, content: str, meta: dict) -> KnowledgeBaseEntry:
    heading_path = tuple(
        meta[k] for k in ("h1", "h2", "h3") if meta.get(k)
    )
    clean_meta = {
        k: str(v) for k, v in meta.items() if k not in {"h1", "h2", "h3", "source_path"}
    }
    return KnowledgeBaseEntry(
        id=doc_id,
        source_path=meta.get("source_path", ""),
        heading_path=heading_path,
        content=content,
        metadata=clean_meta,
    )


class ChromaKnowledgeBase(KnowledgeBasePort):
    def __init__(
        self,
        persist_dir: Path,
        collection_name: str = DEFAULT_COLLECTION,
        embedding_model: str = DEFAULT_MODEL,
    ):
        persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(persist_dir))
        self._embedder = _E5EmbeddingFunction(embedding_model)
        self._collection = self._client.get_or_create_collection(
            name=collection_name,
            embedding_function=self._embedder,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert(self, entries: Iterable[KnowledgeBaseEntry]) -> None:
        # Dedupe by id: OCR can produce repeated boilerplate chunks (page headers,
        # empty sections) that hash to the same id. Chroma rejects duplicate ids
        # within a single upsert call.
        by_id: dict[str, KnowledgeBaseEntry] = {}
        for e in entries:
            by_id[e.id] = e
        if not by_id:
            return
        ids = list(by_id.keys())
        docs = [by_id[i].content for i in ids]
        metadatas = []
        for i in ids:
            e = by_id[i]
            m = {
                "source_path": e.source_path,
                **e.metadata,
            }
            for idx, heading in enumerate(e.heading_path, start=1):
                m[f"h{idx}"] = heading
            metadatas.append(m)
        self._collection.upsert(ids=ids, documents=docs, metadatas=metadatas)
        logger.info("Upserted %d chunks", len(ids))

    def query(
        self,
        text: str,
        k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[KnowledgeBaseEntry]:
        query_embedding = self._embedder.embed_query(text)
        res = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=filters or None,
        )
        out: list[KnowledgeBaseEntry] = []
        ids = res.get("ids", [[]])[0]
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        for doc_id, content, meta in zip(ids, docs, metas):
            out.append(_to_entry(doc_id, content, meta or {}))
        return out

    def delete_by_source(self, source_path: str) -> None:
        self._collection.delete(where={"source_path": source_path})

    def reset(self) -> None:
        """Drop and recreate the collection. Used by CLI --rebuild."""
        name = self._collection.name
        self._client.delete_collection(name)
        self._collection = self._client.get_or_create_collection(
            name=name,
            embedding_function=self._embedder,
            metadata={"hnsw:space": "cosine"},
        )
