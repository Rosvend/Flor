from abc import ABC, abstractmethod


class CuratedDataLakePort(ABC):
    @abstractmethod
    def next_radicado(self) -> str:
        """Returns the next sequential radicado (e.g. MDE-00001)."""

    @abstractmethod
    def store(self, records: list[dict]) -> list[str]:
        """Persists records keyed by radicado; returns storage keys."""

    @abstractmethod
    def update_by_radicado(self, radicado: str, record: dict) -> None:
        """Overwrites the record identified by radicado."""

    @abstractmethod
    def get_by_radicado(self, radicado: str) -> dict | None:
        """Returns a single record by its radicado, or None."""

    @abstractmethod
    def get_all(self) -> list[dict]:
        """Returns all curated records."""

    def update(self, key: str, record: dict) -> None:
        """Legacy key-based update — delegates to update_by_radicado."""
        radicado = record.get("radicado")
        if radicado:
            self.update_by_radicado(radicado, record)
