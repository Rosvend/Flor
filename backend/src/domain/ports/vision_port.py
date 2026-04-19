from abc import ABC, abstractmethod
from typing import List, Dict, Any

class VisionAnalyzerPort(ABC):
    @abstractmethod
    def analyze(self, image_bytes: bytes) -> List[Dict[str, Any]]:
        """
        Analiza una imagen y devuelve una lista de objetos detectados.
        Cada objeto debe contener: 'label', 'confidence' y opcionalmente 'box'.
        """
        pass
