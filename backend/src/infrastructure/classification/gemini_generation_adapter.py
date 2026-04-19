from __future__ import annotations

import logging
import os

from google import genai
from google.genai import types

from src.domain.ports.generation_port import GenerationPort

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiGenerationAdapter(GenerationPort):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float = 0.2,
    ) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to backend/.env to enable the chatbot."
            )
        self._client = genai.Client(api_key=key)
        self._model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        self._temperature = temperature

    def generate(self, system: str, user: str, max_tokens: int = 512) -> str:
        config_kwargs: dict = {
            "system_instruction": system,
            "temperature": self._temperature,
            "max_output_tokens": max_tokens,
        }
        # thinking_config is only supported on the Gemini 2.5 series. Sending it
        # to gemini-2.0-*, gemini-1.5-*, or other models raises a 400. Gate it.
        if self._model.startswith("gemini-2.5"):
            config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)

        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=user,
                config=types.GenerateContentConfig(**config_kwargs),
            )
        except Exception as exc:
            logger.exception("Gemini generation failed: %s", exc)
            return ""
        return (response.text or "").strip()
