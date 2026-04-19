from dataclasses import dataclass

from src.application.dtos.pqrsd_assist_dtos import DraftResponseInput
from src.application.use_cases.draft_response_pqrsd import DraftResponsePQRSD
from src.domain.entities.knowledge_base_entry import KnowledgeBaseEntry


@dataclass
class StubKb:
    scored: list[tuple[KnowledgeBaseEntry, float]]
    last_filters: dict | None = None
    last_query: str | None = None

    def upsert(self, entries):  # pragma: no cover
        raise NotImplementedError

    def query(self, text, k=5, filters=None):  # pragma: no cover
        return [e for e, _ in self.scored]

    def query_with_scores(self, text, k=5, filters=None):
        self.last_query = text
        self.last_filters = filters
        return self.scored

    def delete_by_source(self, source_path):  # pragma: no cover
        raise NotImplementedError


class StubGen:
    def __init__(self, reply: str):
        self.reply = reply
        self.last_user: str | None = None
        self.last_system: str | None = None
        self.calls = 0

    def generate(self, system: str, user: str, max_tokens: int = 512) -> str:
        self.calls += 1
        self.last_system = system
        self.last_user = user
        return self.reply


def _entry(content: str, heading=("Sección",)) -> KnowledgeBaseEntry:
    return KnowledgeBaseEntry(
        id="x", source_path="src.md", heading_path=heading, content=content, metadata={}
    )


def test_happy_path_produces_draft_with_sources():
    kb = StubKb(scored=[
        (_entry("El plazo es 15 días hábiles.", heading=("Ley 1755", "Plazos")), 0.91),
        (_entry("Las peticiones deben ser respondidas formalmente."), 0.88),
    ])
    gen = StubGen(reply="Apreciado ciudadano,\n\nEn respuesta a su solicitud...\n\nAlcaldía de Medellín.")
    uc = DraftResponsePQRSD(knowledge_base=kb, generation=gen, min_similarity=0.55)

    out = uc.execute(DraftResponseInput(content="Solicito información.", asunto="peticion"))

    assert gen.calls == 1
    assert out.used_fallback is False
    assert "Apreciado ciudadano" in out.draft
    assert len(out.sources) == 2
    assert out.sources[0].title == "Ley 1755 > Plazos"
    assert "[Fuente 1]" in gen.last_user
    assert "Asunto/Tipo: peticion" in gen.last_user
    assert "Redacta el borrador" in gen.last_user


def test_calls_llm_with_empty_context_when_no_chunks_pass_threshold():
    kb = StubKb(scored=[(_entry("irrelevante"), 0.40)])
    gen = StubGen(reply="Borrador genérico aprobable por el asesor.")
    uc = DraftResponsePQRSD(knowledge_base=kb, generation=gen, min_similarity=0.55)

    out = uc.execute(DraftResponseInput(content="texto"))

    assert gen.calls == 1
    assert "(sin resultados relevantes)" in gen.last_user
    assert out.used_fallback is False
    assert out.sources == []


def test_empty_content_returns_fallback_without_calling_llm():
    kb = StubKb(scored=[])
    gen = StubGen(reply="should-not-be-called")
    uc = DraftResponsePQRSD(knowledge_base=kb, generation=gen)

    out = uc.execute(DraftResponseInput(content="   "))

    assert gen.calls == 0
    assert out.used_fallback is True
    assert out.draft == ""


def test_model_empty_reply_marks_fallback():
    kb = StubKb(scored=[(_entry("algo relevante"), 0.92)])
    gen = StubGen(reply="")
    uc = DraftResponsePQRSD(knowledge_base=kb, generation=gen)

    out = uc.execute(DraftResponseInput(content="texto real"))

    assert gen.calls == 1
    assert out.used_fallback is True
    assert out.draft == ""


def test_passes_visibility_filter_to_kb():
    kb = StubKb(scored=[(_entry("x"), 0.9)])
    gen = StubGen(reply="ok")
    uc = DraftResponsePQRSD(knowledge_base=kb, generation=gen)

    uc.execute(DraftResponseInput(content="texto"))

    assert kb.last_filters == {"visibility": "public"}


def test_includes_citizen_name_when_provided():
    kb = StubKb(scored=[])
    gen = StubGen(reply="Respuesta con nombre.")
    uc = DraftResponsePQRSD(knowledge_base=kb, generation=gen)

    uc.execute(DraftResponseInput(content="texto", citizen_name="Ana Pérez"))

    assert "Ciudadano: Ana Pérez" in gen.last_user
