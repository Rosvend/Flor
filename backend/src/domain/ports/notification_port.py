from abc import ABC, abstractmethod


class NotificationPort(ABC):
    @abstractmethod
    def notify_created(self, record: dict) -> None:
        """Notifies citizen when their PQRSD is opened (estado: abierto)."""

    @abstractmethod
    def notify_resolved(self, record: dict) -> None:
        """Notifies citizen when their PQRSD is resolved (estado: respondido)."""
