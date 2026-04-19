import os

from google import genai

from src.domain.ports.pqrs_analyzer_port import TextCorrectorPort
from src.infrastructure.analysis.prompts import REDACTION_SYSTEM_PROMPT


class GeminiTextCorrector(TextCorrectorPort):
    """Corrección de redacción PQRSD usando Gemini API (Manual V5)."""

    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada en .env")
        self._client = genai.Client(api_key=api_key)
        self._model = self._find_model()

    def _find_model(self) -> str:
        preferred = ["gemini-1.5-flash"]
        try:
            available = [
                m.name.replace("models/", "")
                for m in self._client.models.list()
            ]
            for name in preferred:
                if name in available:
                    return name
            return available[0]
        except Exception:
            return "gemini-1.5-flash"

    def improve_text(self, text: str) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=text,
            config={"system_instruction": REDACTION_SYSTEM_PROMPT},
        )
        return response.text.strip()
