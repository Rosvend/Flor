from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PQRSEntity:
    id: Optional[int]
    original_text: str
    improved_text: str
    sentiment: Optional[str]
    timestamp: datetime
