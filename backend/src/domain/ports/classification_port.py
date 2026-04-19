from abc import ABC, abstractmethod
from typing import Optional
from pydantic import BaseModel, Field


class ClassificationResult(BaseModel):
    tipo: str = Field(..., description="Tipo de PQRS (Petición, Queja, Reclamo, Sugerencia o Denuncia)")
    suggested_department: str = Field(..., description="Nombre de la Secretaría o dependencia sugerida")
    suggested_subsecretaria: Optional[str] = Field(None, description="Subsecretaría específica si aplica (ej. Creación y Fortalecimiento Empresarial para Desarrollo Económico)")
    priority: str = Field(..., description="Prioridad asignada (Alta, Media, Baja)")
    confidence_score: float = Field(..., description="Nivel de confianza en la clasificación entre 0.0 y 1.0")


class ClassificationPort(ABC):
    @abstractmethod
    def pre_classify(self, text: str) -> ClassificationResult:
        """
        Realiza la pre-clasificación de F2 (Componente B):
        Determina tipo, dependencia, subsecretaría (si aplica), prioridad y score de confianza.
        """
        pass

    @abstractmethod
    def is_pqrs(self, text: str) -> bool:
        """Determina si un texto crudo es una PQRSD o spam/conversación."""
        pass
