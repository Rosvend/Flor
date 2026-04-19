from abc import ABC, abstractmethod
from typing import List, Dict, Any

class EmailMessage(ABC):
    id: str
    sender: str
    subject: str
    body: str
    timestamp: str

class EmailConnectorPort(ABC):
    @abstractmethod
    def authenticate(self) -> None:
        """Autentica con el servicio de correo."""
        pass

    @abstractmethod
    def fetch_unread_messages(self, query: str = "is:unread") -> List[Dict[str, Any]]:
        """Recupera mensajes no leídos que coincidan con el criterio."""
        pass

    @abstractmethod
    def mark_as_read(self, message_id: str) -> None:
        """Marca un mensaje como procesado/leído."""
        pass
