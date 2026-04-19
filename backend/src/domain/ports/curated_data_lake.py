from abc import ABC, abstractmethod


class CuratedDataLakePort(ABC):
    @abstractmethod
    def store(self, records: list[dict]) -> list[str]:
        """Persists curated records and returns their storage keys."""

    @abstractmethod
    def update(self, key: str, record: dict) -> None:
        """Updates an existing record at the given key."""
