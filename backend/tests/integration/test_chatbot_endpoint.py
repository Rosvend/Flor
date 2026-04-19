from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from src.application.use_cases.query_flor_chatbot import QueryFlorChatbot
from src.domain.entities.knowledge_base_entry import KnowledgeBaseEntry

FALLBACK = "No tengo esa respuesta. Radique un PQRSD."


@dataclass
class StubKb:
    scored: list[tuple[KnowledgeBaseEntry, float]]

    def upsert(self, entries):  # pragma: no cover
        raise NotImplementedError

    def query(self, text, k=5, filters=None):  # pragma: no cover
        return [e for e, _ in self.scored]

    def query_with_scores(self, text, k=5, filters=None):
        return self.scored

    def delete_by_source(self, source_path):  # pragma: no cover
        raise NotImplementedError


class StubGen:
    def __init__(self, reply: str):
        self.reply = reply

    def generate(self, system: str, user: str, max_tokens: int = 512) -> str:
        return self.reply


class StubIngestion:
    def ingest(self, filename, content, uploaded_by):
        return 3, f"/tmp/{filename}.md"


@pytest.fixture
def client():
    # Wire stubs into the container BEFORE importing the FastAPI app.
    from src.infrastructure import container

    container.query_flor_chatbot = QueryFlorChatbot(
        knowledge_base=StubKb(scored=[
            (KnowledgeBaseEntry(
                id="1", source_path="s.md", heading_path=("Tema",),
                content="contenido relevante", metadata={},
            ), 0.9),
        ]),
        generation=StubGen("respuesta basada en el contexto"),
        fallback_message=FALLBACK,
    )
    from src.application.use_cases.ingest_knowledge_base_document import (
        IngestKnowledgeBaseDocument,
    )
    container.ingest_knowledge_base_document = IngestKnowledgeBaseDocument(
        ingestion=StubIngestion(),
    )

    from main import app
    return TestClient(app)


def test_query_returns_grounded_answer(client):
    res = client.post("/api/v1/chatbot/query", json={"question": "¿algo?"})
    assert res.status_code == 200
    body = res.json()
    assert body["used_fallback"] is False
    assert body["answer"] == "respuesta basada en el contexto"
    assert len(body["sources"]) == 1


def test_query_validates_empty_question(client):
    res = client.post("/api/v1/chatbot/query", json={"question": ""})
    assert res.status_code == 422  # Pydantic min_length


def test_query_returns_503_when_chatbot_unconfigured(client):
    from src.infrastructure import container
    saved = container.query_flor_chatbot
    container.query_flor_chatbot = None
    try:
        res = client.post("/api/v1/chatbot/query", json={"question": "hola"})
        assert res.status_code == 503
    finally:
        container.query_flor_chatbot = saved


def test_documents_requires_auth(client):
    res = client.post(
        "/api/v1/chatbot/documents",
        files={"file": ("note.md", b"# Hola\nContenido", "text/markdown")},
    )
    assert res.status_code == 403  # HTTPBearer rejects missing creds with 403


def test_documents_indexes_with_valid_token(client):
    from src.infrastructure import container
    token = container.token_generator.generate({"sub": "user-1"})

    res = client.post(
        "/api/v1/chatbot/documents",
        files={"file": ("note.md", b"# Hola\nContenido", "text/markdown")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["chunks_indexed"] == 3
    assert body["source_path"].endswith(".md")


def test_documents_rejects_invalid_token(client):
    res = client.post(
        "/api/v1/chatbot/documents",
        files={"file": ("note.md", b"x", "text/markdown")},
        headers={"Authorization": "Bearer not-a-real-jwt"},
    )
    assert res.status_code == 401
