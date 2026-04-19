from dataclasses import dataclass

from src.application.dtos.chatbot_dtos import QueryChatbotInput
from src.application.use_cases.query_flor_chatbot import QueryFlorChatbot
from src.domain.entities.knowledge_base_entry import KnowledgeBaseEntry

FALLBACK = "No tengo esa respuesta. Radique un PQRSD."


@dataclass
class StubKb:
    scored: list[tuple[KnowledgeBaseEntry, float]]
    last_filters: dict | None = None

    def upsert(self, entries):  # pragma: no cover
        raise NotImplementedError

    def query(self, text, k=5, filters=None):  # pragma: no cover
        return [e for e, _ in self.scored]

    def query_with_scores(self, text, k=5, filters=None):
        self.last_filters = filters
        return self.scored

    def delete_by_source(self, source_path):  # pragma: no cover
        raise NotImplementedError


class StubGen:
    def __init__(self, reply: str):
        self.reply = reply
        self.last_system: str | None = None
        self.last_user: str | None = None
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


def test_calls_llm_with_empty_context_when_no_results():
    kb = StubKb(scored=[])
    gen = StubGen(reply=FALLBACK)
    uc = QueryFlorChatbot(kb, gen, fallback_message=FALLBACK)

    out = uc.execute(QueryChatbotInput(question="¿cuál es el clima?"))

    assert gen.calls == 1
    assert "sin resultados relevantes" in gen.last_user
    assert out.used_fallback is True
    assert out.answer == FALLBACK
    assert out.sources == []


def test_calls_llm_with_empty_context_when_all_below_min_similarity():
    kb = StubKb(scored=[(_entry("contenido"), 0.40)])
    gen = StubGen(reply=FALLBACK)
    uc = QueryFlorChatbot(kb, gen, fallback_message=FALLBACK, min_similarity=0.55)

    out = uc.execute(QueryChatbotInput(question="¿algo?"))

    assert gen.calls == 1
    assert "sin resultados relevantes" in gen.last_user
    assert out.used_fallback is True
    assert out.sources == []


def test_conversational_reply_without_context_is_not_fallback():
    kb = StubKb(scored=[])
    gen = StubGen(reply="¡Hola! Soy Flor, puedo ayudarte con información sobre la Alcaldía.")
    uc = QueryFlorChatbot(kb, gen, fallback_message=FALLBACK)

    out = uc.execute(QueryChatbotInput(question="hola"))

    assert gen.calls == 1
    assert out.used_fallback is False
    assert out.answer.startswith("¡Hola!")
    assert out.sources == []


def test_returns_grounded_answer_with_sources():
    kb = StubKb(scored=[
        (_entry("Plazo es 15 días hábiles.", heading=("Ley 1755", "Plazos")), 0.92),
        (_entry("Para denuncias por corrupción también 15 días."), 0.88),
    ])
    gen = StubGen(reply="El plazo legal es de 15 días hábiles.")
    uc = QueryFlorChatbot(kb, gen, fallback_message=FALLBACK)

    out = uc.execute(QueryChatbotInput(question="¿Cuántos días?"))

    assert out.used_fallback is False
    assert out.answer == "El plazo legal es de 15 días hábiles."
    assert len(out.sources) == 2
    assert out.sources[0].title == "Ley 1755 > Plazos"
    assert "[Fuente 1]" in gen.last_user
    assert "Pregunta del ciudadano" in gen.last_user
    assert FALLBACK in gen.last_system  # fallback baked into system prompt


def test_marks_fallback_when_model_returns_fallback_literal():
    kb = StubKb(scored=[(_entry("contenido"), 0.95)])
    gen = StubGen(reply=FALLBACK)
    uc = QueryFlorChatbot(kb, gen, fallback_message=FALLBACK)

    out = uc.execute(QueryChatbotInput(question="¿x?"))

    assert out.used_fallback is True
    assert out.answer == FALLBACK


def test_passes_visibility_filter_to_kb():
    kb = StubKb(scored=[(_entry("c"), 0.9)])
    gen = StubGen(reply="ok")
    uc = QueryFlorChatbot(kb, gen, fallback_message=FALLBACK)

    uc.execute(QueryChatbotInput(question="?"))

    assert kb.last_filters == {"visibility": "public"}


def test_empty_question_returns_fallback():
    kb = StubKb(scored=[(_entry("c"), 0.9)])
    gen = StubGen(reply="should-not-call")
    uc = QueryFlorChatbot(kb, gen, fallback_message=FALLBACK)

    out = uc.execute(QueryChatbotInput(question="   "))

    assert out.used_fallback is True
    assert gen.calls == 0
