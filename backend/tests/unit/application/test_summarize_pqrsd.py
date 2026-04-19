from src.application.dtos.pqrsd_assist_dtos import SummarizePQRSDInput
from src.application.use_cases.summarize_pqrsd import SummarizePQRSD


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


def test_parses_clean_json_from_model():
    gen = StubGen(reply='{"lead": "Solicita información sobre crédito para panadería.", "topics": ["financiación microempresas", "sector panadero"]}')
    uc = SummarizePQRSD(generation=gen)

    out = uc.execute(SummarizePQRSDInput(content="Me dirijo a la Secretaría..."))

    assert gen.calls == 1
    assert out.lead == "Solicita información sobre crédito para panadería."
    assert out.topics == ["financiación microempresas", "sector panadero"]
    assert out.original == "Me dirijo a la Secretaría..."


def test_strips_markdown_code_fence():
    gen = StubGen(reply='```json\n{"lead": "Pide devolución.", "topics": ["pago indebido"]}\n```')
    uc = SummarizePQRSD(generation=gen)

    out = uc.execute(SummarizePQRSDInput(content="Reclamo formal..."))

    assert out.lead == "Pide devolución."
    assert out.topics == ["pago indebido"]


def test_extracts_json_substring_when_model_wraps_it_in_prose():
    gen = StubGen(reply='Aquí tienes el JSON solicitado: {"lead": "Consulta plazos.", "topics": ["plazos"]} Saludos.')
    uc = SummarizePQRSD(generation=gen)

    out = uc.execute(SummarizePQRSDInput(content="¿Cuándo me responden?"))

    assert out.lead == "Consulta plazos."
    assert out.topics == ["plazos"]


def test_truncates_topics_to_six():
    topics = [f"tema{i}" for i in range(10)]
    import json
    gen = StubGen(reply=json.dumps({"lead": "X", "topics": topics}))
    uc = SummarizePQRSD(generation=gen)

    out = uc.execute(SummarizePQRSDInput(content="contenido"))

    assert len(out.topics) == 6
    assert out.topics == topics[:6]


def test_empty_content_returns_safe_default_without_calling_llm():
    gen = StubGen(reply="should-not-be-called")
    uc = SummarizePQRSD(generation=gen)

    out = uc.execute(SummarizePQRSDInput(content="   "))

    assert gen.calls == 0
    assert "No fue posible" in out.lead
    assert out.topics == []
    assert out.original == ""


def test_unparseable_reply_falls_back_to_safe_default_but_preserves_original():
    gen = StubGen(reply="Lo siento, no puedo hacer eso.")
    uc = SummarizePQRSD(generation=gen)

    out = uc.execute(SummarizePQRSDInput(content="Texto real de la PQR."))

    assert "No fue posible" in out.lead
    assert out.topics == []
    assert out.original == "Texto real de la PQR."


def test_preserves_original_verbatim_as_layer_3():
    original = "Línea 1.\n\nLínea 2 con acentos áéíóú."
    gen = StubGen(reply='{"lead": "Reporta algo.", "topics": []}')
    uc = SummarizePQRSD(generation=gen)

    out = uc.execute(SummarizePQRSDInput(content=original))

    assert out.original == original
