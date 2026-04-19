from src.domain.ports.pqrs_analyzer_port import (
    SentimentAnalyzerPort,
    ToxicityDetectorPort,
    TextCorrectorPort,
)
from src.application.dtos.pqrs_dtos import ProcessPQRSInput, ProcessPQRSOutput


class ProcessPQRS:
    """Orquesta el flujo: Toxicidad → Sentimiento → Corrección."""

    def __init__(
        self,
        toxicity_detector: ToxicityDetectorPort,
        sentiment_analyzer: SentimentAnalyzerPort,
        text_corrector: TextCorrectorPort,
    ) -> None:
        self._toxicity = toxicity_detector
        self._sentiment = sentiment_analyzer
        self._corrector = text_corrector

    def execute(self, input_dto: ProcessPQRSInput) -> ProcessPQRSOutput:
        # 1. Detectar groserías
        toxicity = self._toxicity.analyze(input_dto.text)

        # 2. Analizar sentimiento
        sentiment = self._sentiment.analyze(input_dto.text)

        # 3. Corregir redacción según Manual V5
        improved = self._corrector.improve_text(input_dto.text)

        return ProcessPQRSOutput(
            original_text=input_dto.text,
            improved_text=improved,
            sentiment=sentiment,
            is_offensive=toxicity["is_offensive"],
            toxicity_warning=toxicity["warning"],
            offensive_words=toxicity.get("offensive_words_found", []),
        )
