import os
from google import genai
from .prompts import REDACTION_SYSTEM_PROMPT

class CorrectionService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no configurada")
        self.client = genai.Client(api_key=api_key)
        self.model_name = self._find_available_model()

    def _find_available_model(self):
        preferred_models = ['gemini-1.5-flash', 'gemini-pro']
        try:
            available = [m.name.replace("models/", "") for m in self.client.models.list()]
            for model in preferred_models:
                if model in available:
                    return model
            return available[0]
        except:
            return 'gemini-1.5-flash'

    def improve_text(self, text: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=text,
            config={'system_instruction': REDACTION_SYSTEM_PROMPT}
        )
        return response.text.strip()
