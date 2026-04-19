from abc import ABC, abstractmethod


class CuratedDataLakePort(ABC):
    @abstractmethod
    def store(self, records: list[dict]) -> list[str]:
        """Persists curated records and returns their storage keys."""
