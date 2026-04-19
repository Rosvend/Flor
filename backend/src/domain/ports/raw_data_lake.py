from abc import ABC, abstractmethod


class RawDataLakePort(ABC):
    @abstractmethod
    def store(self, records: list[dict]) -> list[str]:
        """Persists raw records and returns their storage keys."""

    @abstractmethod
    def get_all(self) -> list[dict]:
        """Retrieves all stored raw records."""
