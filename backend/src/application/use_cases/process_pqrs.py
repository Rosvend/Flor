from src.domain.ports.pqrs_analyzer_port import (
    SentimentAnalyzerPort,
    ToxicityDetectorPort,
    TextCorrectorPort,
)
from src.domain.ports.pqrs_classifier_port import PQRSClassifierPort
from src.domain.ports.department_router_port import DepartmentRouterPort
from src.application.dtos.pqrs_dtos import ProcessPQRSInput, ProcessPQRSOutput


class ProcessPQRS:
    """Orquesta el flujo: Toxicidad → Sentimiento → Corrección → Clasificación → Enrutamiento."""

    def __init__(
        self,
        toxicity_detector: ToxicityDetectorPort,
        sentiment_analyzer: SentimentAnalyzerPort,
        text_corrector: TextCorrectorPort,
        classifier: PQRSClassifierPort = None,
        router: DepartmentRouterPort = None,
    ) -> None:
        self._toxicity = toxicity_detector
        self._sentiment = sentiment_analyzer
        self._corrector = text_corrector
        self._classifier = classifier
        self._router = router

    def execute(self, input_dto: ProcessPQRSInput) -> ProcessPQRSOutput:
        # 1. Detectar groserías
        toxicity = self._toxicity.analyze(input_dto.text)

        # 2. Analizar sentimiento
        sentiment = self._sentiment.analyze(input_dto.text)

        # 3. Corregir redacción según Manual V5
        improved = self._corrector.improve_text(input_dto.text)

        # 4. Clasificación Zero-Shot
        tipo_sugerido = None
        if self._classifier:
            tipo_sugerido = self._classifier.classify(input_dto.text)

        # 5. Enrutamiento Semántico
        secretaria = None
        if self._router:
            dept = self._router.route(input_dto.text)
            if dept:
                secretaria = dept.name

        return ProcessPQRSOutput(
            original_text=input_dto.text,
            improved_text=improved,
            sentiment=sentiment,
            is_offensive=toxicity["is_offensive"],
            toxicity_warning=toxicity["warning"],
            offensive_words=toxicity.get("offensive_words_found", []),
            tipo_sugerido=tipo_sugerido,
            secretaria_asignada=secretaria,
        )
