from src.domain.ports.pqrs_analyzer_port import (
    SentimentAnalyzerPort,
    ToxicityDetectorPort,
    TextCorrectorPort,
)
from src.domain.ports.classification_port import ClassificationPort
from src.domain.ports.vision_port import VisionAnalyzerPort
from src.application.dtos.pqrs_dtos import ProcessPQRSInput, ProcessPQRSOutput


class ProcessPQRS:
    """Orquesta el flujo: Visión → Toxicidad → Sentimiento → Corrección → Pre-Clasificación (F2)."""

    def __init__(
        self,
        toxicity_detector: ToxicityDetectorPort,
        sentiment_analyzer: SentimentAnalyzerPort,
        text_corrector: TextCorrectorPort,
        pre_classifier: ClassificationPort = None,
        vision_analyzer: VisionAnalyzerPort = None,
    ) -> None:
        self._toxicity = toxicity_detector
        self._sentiment = sentiment_analyzer
        self._corrector = text_corrector
        self._pre_classifier = pre_classifier
        self._vision = vision_analyzer

    def execute(self, input_dto: ProcessPQRSInput) -> ProcessPQRSOutput:
        # 0. Analizar imágenes (si existen)
        detected_objects = []
        if self._vision and input_dto.images:
            for img_bytes in input_dto.images:
                results = self._vision.analyze(img_bytes)
                # Extraer solo las etiquetas únicas de los objetos detectados
                labels = list(set([r["label"] for r in results]))
                detected_objects.extend(labels)
            detected_objects = list(set(detected_objects)) # Únicos entre todas las imágenes

        # 1. Detectar groserías
        toxicity = self._toxicity.analyze(input_dto.text)

        # 2. Analizar sentimiento
        sentiment = self._sentiment.analyze(input_dto.text)

        # 3. Corregir redacción según Manual V5
        improved = self._corrector.improve_text(input_dto.text)

        # 4. Pre-Clasificación F2 (Componente B)
        tipo_sugerido = None
        secretaria = None
        subsecretaria = None
        prioridad = None
        confidence = None

        if self._pre_classifier:
            # Analyze using the improved text or original? The requirement implies content. Let's use improved for better classification
            # Wait, usually pre-classification uses original or improved. We'll use input_dto.text to be safe and raw.
            classification_result = self._pre_classifier.pre_classify(input_dto.text)
            
            tipo_sugerido = classification_result.tipo
            prioridad = classification_result.priority
            confidence = classification_result.confidence_score
            
            # Triage rule: If confidence < 0.75 -> human triage queue, do not auto-assign
            if confidence >= 0.75:
                secretaria = classification_result.suggested_department
                subsecretaria = classification_result.suggested_subsecretaria
            else:
                secretaria = None
                subsecretaria = None

        return ProcessPQRSOutput(
            original_text=input_dto.text,
            improved_text=improved,
            sentiment=sentiment,
            is_offensive=toxicity["is_offensive"],
            toxicity_warning=toxicity["warning"],
            offensive_words=toxicity.get("offensive_words_found", []),
            tipo_sugerido=tipo_sugerido,
            secretaria_asignada=secretaria,
            subsecretaria_sugerida=subsecretaria,
            prioridad=prioridad,
            confidence_score=confidence,
            detected_objects=detected_objects,
        )
