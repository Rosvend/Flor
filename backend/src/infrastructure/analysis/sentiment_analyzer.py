from transformers import pipeline

from src.domain.ports.pqrs_analyzer_port import SentimentAnalyzerPort


class BetoSentimentAnalyzer(SentimentAnalyzerPort):
    """Análisis de sentimiento en español usando BETO (Hugging Face)."""

    def __init__(self) -> None:
        self._classifier = pipeline(
            "sentiment-analysis",
            model="finiteautomata/beto-sentiment-analysis",
        )

    def analyze(self, text: str) -> str:
        try:
            result = self._classifier(text)[0]
            return f"{result['label']} ({result['score']:.2f})"
        except Exception as e:
            print(f"Error en análisis de sentimiento: {e}")
            return "NEU (Error)"
