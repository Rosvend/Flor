from transformers import pipeline

from src.domain.ports.pqrs_classifier_port import PQRSClassifierPort


class HuggingFaceZeroShotClassifier(PQRSClassifierPort):
    def __init__(self, model_name: str = "Recognai/bert-base-spanish-wwm-cased-xnli") -> None:
        # Usamos un modelo en español para mejor precisión y menor peso
        self._classifier = pipeline(
            "zero-shot-classification",
            model=model_name,
        )
        self._categories = ["petición", "queja", "reclamo", "sugerencia", "denuncia"]

    def classify(self, text: str) -> str:
        # Si el texto es muy corto, devolvemos un valor por defecto o peticion
        if not text or len(text.strip()) < 10:
            return "petición"
            
        try:
            # truncate text to avoid max length errors
            truncated_text = text[:1000]
            result = self._classifier(
                truncated_text,
                candidate_labels=self._categories,
                hypothesis_template="Este texto es una {}."
            )
            # El primer elemento en labels es el que tiene mayor score
            return result["labels"][0]
        except Exception as e:
            print(f"Error clasificando PQRS: {e}")
            return "petición"

    def is_pqrs(self, text: str) -> bool:
        if not text or len(text.strip()) < 10:
            return False
            
        try:
            truncated_text = text[:1000]
            categories = ["Petición ciudadana", "Queja o reclamo", "Denuncia", "Saludo o conversación casual", "Spam o irrelevante"]
            result = self._classifier(
                truncated_text,
                candidate_labels=categories,
                hypothesis_template="Este texto es sobre {}."
            )
            top_label = result["labels"][0]
            # Consideramos que es una PQRSD si el modelo le da mayor probabilidad a las primeras 3
            if top_label in ["Petición ciudadana", "Queja o reclamo", "Denuncia"]:
                return True
            return False
        except Exception as e:
            print(f"Error detectando si es PQRS: {e}")
            return False
