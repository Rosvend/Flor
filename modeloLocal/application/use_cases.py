import os
from ..infrastructure.sentiment_service import SentimentService
from ..infrastructure.correction_service import CorrectionService
from ..infrastructure.toxicity_service import ToxicityService
from ..infrastructure.repository import PQRSRepository

class ProcessPQRSUseCase:
    def __init__(self):
        self.sentiment_service = SentimentService()
        self.toxicity_service = ToxicityService()
        self.correction_service = CorrectionService()
        self.repository = PQRSRepository(os.getenv("DATABASE_URL", "sqlite:///./pqrs.db"))

    def execute(self, text: str):
        # 1. Detectar groserías/toxicidad
        toxicity = self.toxicity_service.analyze(text)
        
        # 2. Analizar sentimiento
        sentiment = self.sentiment_service.analyze(text)
        
        # 3. Corregir redacción
        improved = self.correction_service.improve_text(text)
        
        # 4. Guardar
        result = self.repository.save(
            original=text,
            improved=improved,
            sentiment=sentiment,
            is_offensive=toxicity["is_offensive"],
            toxicity_warning=toxicity["warning"]
        )
        
        return result, toxicity

    def get_all(self):
        return self.repository.get_all()
