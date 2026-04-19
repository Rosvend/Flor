from __future__ import annotations
import logging
import os
import json

from google import genai
from google.genai import types

from src.domain.ports.classification_port import ClassificationPort, ClassificationResult

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gemini-2.5-flash"


class GeminiClassificationAdapter(ClassificationPort):
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        temperature: float = 0.1,
    ) -> None:
        key = api_key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to backend/.env to enable pre-classification."
            )
        self._client = genai.Client(api_key=key)
        self._model = model or os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
        self._temperature = temperature

        # System prompt for structured pre-classification
        self._system_prompt = """
        Eres un clasificador experto de PQRSD (Petición, Queja, Reclamo, Sugerencia, Denuncia) para la Alcaldía de Medellín.
        Tu tarea es analizar el texto de la solicitud ciudadana y extraer los siguientes datos en formato JSON estricto:

        1. tipo: Debe ser uno de ["Petición", "Queja", "Reclamo", "Sugerencia", "Denuncia"].
        2. suggested_department: La dependencia de la alcaldía más competente entre las 26 secretarías. 
           (Ejemplos: "Secretaría de Movilidad", "Secretaría de Infraestructura Física", "Secretaría de Seguridad", "Secretaría de Desarrollo Económico", "Secretaría de Salud", "Secretaría de Educación", "Secretaría de Medio Ambiente", etc.).
        3. suggested_subsecretaria: SI el suggested_department es "Secretaría de Desarrollo Económico", DEBES proponer la subsecretaría interna apropiada (ej. "Creación y Fortalecimiento Empresarial", "Banco Distrital", "Turismo", etc.). De lo contrario, retorna null.
        4. priority: Asigna la prioridad ["Alta", "Media", "Baja"] según la urgencia de la solicitud.
        5. confidence_score: Un número float entre 0.0 y 1.0 indicando tu confianza en esta clasificación (0.75 a 1.0 = Alta confianza). Si el texto es muy ambiguo o confuso, asigna menos de 0.75.
        
        Debes retornar estrictamente un objeto JSON que coincida con este esquema, sin texto adicional.
        """

    def pre_classify(self, text: str) -> ClassificationResult:
        if not text or len(text.strip()) < 10:
            # Fallback para textos muy cortos
            return ClassificationResult(
                tipo="Petición",
                suggested_department="Indeterminado",
                suggested_subsecretaria=None,
                priority="Baja",
                confidence_score=0.1
            )
        
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=self._system_prompt,
                    temperature=self._temperature,
                    response_mime_type="application/json",
                    response_schema={
                        "type": "OBJECT",
                        "properties": {
                            "tipo": {"type": "STRING", "enum": ["Petición", "Queja", "Reclamo", "Sugerencia", "Denuncia"]},
                            "suggested_department": {"type": "STRING"},
                            "suggested_subsecretaria": {"type": "STRING", "nullable": True},
                            "priority": {"type": "STRING", "enum": ["Alta", "Media", "Baja"]},
                            "confidence_score": {"type": "NUMBER"}
                        },
                        "required": ["tipo", "suggested_department", "priority", "confidence_score"]
                    },
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
            
            result_json = json.loads(response.text)
            return ClassificationResult(**result_json)
            
        except Exception as exc:
            logger.exception("Gemini pre-classification failed: %s", exc)
            # Default fallback on failure
            return ClassificationResult(
                tipo="Petición",
                suggested_department="Indeterminado",
                suggested_subsecretaria=None,
                priority="Baja",
                confidence_score=0.0
            )

    def is_pqrs(self, text: str) -> bool:
        if not text or len(text.strip()) < 10:
            return False
            
        prompt = """
        Analiza si el siguiente texto es una solicitud formal ciudadana (Petición, Queja, Reclamo, Sugerencia o Denuncia).
        Si es un saludo, spam, insulto sin contexto, o texto irrelevante, responde EXACTAMENTE con "NO".
        Si es una solicitud, queja o reporte ciudadano real (incluso si es informal o corto como "hay un hueco en mi calle"), responde EXACTAMENTE con "SI".
        """
        
        try:
            response = self._client.models.generate_content(
                model=self._model,
                contents=[prompt, text],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            )
            return "SI" in (response.text or "").upper()
        except Exception:
            return False
