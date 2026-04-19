from abc import ABC, abstractmethod


class PQRSClassifierPort(ABC):
    @abstractmethod
    def classify(self, text: str) -> str:
        """
        Clasifica el texto de una PQRSD en una de las categorías principales:
        Petición, Queja, Reclamo, Sugerencia o Denuncia.
        """
