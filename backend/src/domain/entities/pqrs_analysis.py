from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class PQRSAnalysis:
    """Resultado del análisis completo de una PQRS."""
    original_text: str
    improved_text: str
    sentiment: str
    is_offensive: bool
    toxicity_warning: Optional[str] = None
    offensive_words: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
