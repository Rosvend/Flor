from abc import ABC, abstractmethod


class RawDataLakePort(ABC):
    @abstractmethod
    def store(self, records: list[dict]) -> list[str]:
        """Persists raw records and returns their storage keys."""

    @abstractmethod
    def get_all(self) -> dict[str, dict]:
        """Retrieves all stored raw records."""

    @abstractmethod
    def delete(self, key: str) -> None:
        """Deletes a raw record by its storage key."""
