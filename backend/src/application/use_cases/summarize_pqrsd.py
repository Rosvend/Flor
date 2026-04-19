import json
import re

from src.application.dtos.pqrsd_assist_dtos import (
    SummarizePQRSDInput,
    SummarizePQRSDOutput,
)
from src.domain.ports.generation_port import GenerationPort


_SYSTEM_PROMPT = (
    "Eres un asistente legal de la Alcaldía de Medellín. Tu tarea es leer una PQRSD "
    "presentada por un ciudadano y producir un resumen estructurado para que el "
    "asesor jurídico tome una decisión rápida.\n\n"
    "Responde ÚNICAMENTE con un objeto JSON válido y sin texto adicional, con esta forma:\n"
    "{\n"
    "  \"lead\": \"<una sola oración en español que diga concretamente qué está pidiendo "
    "o reportando el ciudadano>\",\n"
    "  \"topics\": [\"<tema breve>\", \"<tema breve>\", ...]\n"
    "}\n\n"
    "Reglas:\n"
    "- La oración de \"lead\" debe ser factual, en voz activa, máximo 30 palabras, sin juicios. "
    "Siempre produce una oración útil, incluso si el texto original es breve o informal — "
    "reformúlalo en un español claro y formal, sin añadir hechos inventados.\n"
    "- \"topics\" es una lista de 1 a 6 temas cortos (máximo 6 palabras cada uno) que identifican "
    "los ejes temáticos distintos que toca el texto (ej. \"pago indebido\", \"infraestructura vial\", "
    "\"accidente vial\").\n"
    "- No inventes hechos, montos, leyes ni fechas que no aparezcan en el texto.\n"
    "- No incluyas datos personales del ciudadano (nombres, cédulas, teléfonos, direcciones "
    "exactas) en lead o topics; si el texto menciona una calle o barrio, puedes referirte a "
    "\"una vía\" o \"un sector de la ciudad\" a nivel general.\n"
    "- Solo usa el JSON de respaldo {\"lead\":\"No fue posible identificar una solicitud "
    "concreta en el texto.\",\"topics\":[]} cuando el texto esté vacío, sea ilegible o no "
    "contenga ningún contenido interpretable como PQRSD."
)


class SummaryGenerationError(RuntimeError):
    """The LLM could not produce a usable summary (distinct from an empty input,
    which returns a safe default without raising)."""


class SummarizePQRSD:
    def __init__(self, generation: GenerationPort, max_tokens: int = 400) -> None:
        self._gen = generation
        self._max_tokens = max_tokens

    def execute(self, input_dto: SummarizePQRSDInput) -> SummarizePQRSDOutput:
        original = (input_dto.content or "").strip()
        if not original:
            return SummarizePQRSDOutput(
                lead="No fue posible identificar una solicitud concreta en el texto.",
                topics=[],
                original="",
            )

        user_prompt = f"Texto de la PQRSD:\n\n{original}"
        raw = self._gen.generate(
            system=_SYSTEM_PROMPT,
            user=user_prompt,
            max_tokens=self._max_tokens,
        ).strip()

        # Distinguish three failure modes:
        # 1) LLM returned nothing (429, safety block, or API error swallowed by the
        #    adapter). Raise so the HTTP layer surfaces a 502 instead of masking
        #    this as an "unparseable" PQRSD.
        # 2) LLM returned text but we cannot extract a JSON object. Probably a
        #    malformed reply — same treatment: raise.
        # 3) LLM returned a parseable JSON. Use it.
        if not raw:
            raise SummaryGenerationError(
                "El modelo no devolvió respuesta (probable error del proveedor "
                "o cuota agotada). Intenta de nuevo más tarde."
            )

        parsed = _parse_json_object(raw)
        if parsed is None:
            raise SummaryGenerationError(
                "El modelo devolvió una respuesta que no pudo interpretarse. "
                "Intenta de nuevo."
            )

        lead = str(parsed.get("lead", "")).strip() or (
            "No fue posible identificar una solicitud concreta en el texto."
        )
        raw_topics = parsed.get("topics") or []
        topics = [str(t).strip() for t in raw_topics if str(t).strip()][:6]

        return SummarizePQRSDOutput(lead=lead, topics=topics, original=original)


def _parse_json_object(raw: str) -> dict | None:
    """Best-effort JSON extraction: strip ```json fences, then find the first {...} block."""
    if not raw:
        return None
    cleaned = raw
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```\s*$", cleaned, flags=re.DOTALL)
    if fence:
        cleaned = fence.group(1)
    try:
        obj = json.loads(cleaned)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        obj = json.loads(cleaned[start : end + 1])
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None
