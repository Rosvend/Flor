from transformers import pipeline

class SentimentService:
    def __init__(self):
        self.classifier = pipeline(
            "sentiment-analysis", 
            model="finiteautomata/beto-sentiment-analysis"
        )

    def analyze(self, text: str) -> str:
        try:
            result = self.classifier(text)[0]
            label = result['label']
            score = result['score']
            return f"{label} ({score:.2f})"
        except Exception as e:
            print(f"Error en análisis de sentimiento: {e}")
            return "NEU (Error)"
