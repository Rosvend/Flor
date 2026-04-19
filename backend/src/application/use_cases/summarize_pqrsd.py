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
    "  \"lead\": \"<una sola oración en español que diga concretamente qué está pidiendo el ciudadano>\",\n"
    "  \"topics\": [\"<tema breve>\", \"<tema breve>\", ...]\n"
    "}\n\n"
    "Reglas:\n"
    "- La oración de \"lead\" debe ser factual, en voz activa, máximo 30 palabras, sin juicios.\n"
    "- \"topics\" es una lista de 2 a 6 temas cortos (máximo 6 palabras cada uno) que identifican "
    "los ejes temáticos distintos que toca el texto (ej. \"pago indebido\", \"tiempos de respuesta\", "
    "\"infraestructura vial\").\n"
    "- No inventes hechos, montos, leyes ni fechas que no aparezcan en el texto.\n"
    "- No incluyas datos personales del ciudadano en lead o topics.\n"
    "- Si el texto es muy corto o no se entiende, devuelve un JSON con lead=\"No fue posible "
    "identificar una solicitud concreta en el texto.\" y topics=[]."
)


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

        parsed = _parse_json_object(raw)
        if parsed is None:
            return SummarizePQRSDOutput(
                lead="No fue posible identificar una solicitud concreta en el texto.",
                topics=[],
                original=original,
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
