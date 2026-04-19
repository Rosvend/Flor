import logging
import os

from google import genai

from src.domain.ports.pqrs_analyzer_port import TextCorrectorPort
from src.infrastructure.analysis.prompts import REDACTION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-2.5-flash-lite"


class GeminiTextCorrector(TextCorrectorPort):
    """Corrección de redacción PQRSD usando Gemini API (Manual V5)."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada en .env")
        self._client = genai.Client(api_key=api_key)
        # Honor the same GEMINI_MODEL env var used by the other Gemini adapters
        # so operators can swap models (quota rotation) from one place.
        self._model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

    def improve_text(self, text: str) -> str:
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=text,
                config={"system_instruction": REDACTION_SYSTEM_PROMPT},
            )
            return (response.text or "").strip() or text
        except Exception as exc:
            # Graceful degradation: if Gemini is unavailable (429, safety block,
            # etc.) we return the original text so the rest of the analysis
            # pipeline (sentiment, classification, routing) still runs and
            # analisis_ia gets populated.
            logger.warning("Text correction failed, falling back to original text: %s", exc)
            return text
