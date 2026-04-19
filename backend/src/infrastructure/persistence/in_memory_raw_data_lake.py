import uuid

from src.domain.ports.raw_data_lake import RawDataLakePort


class InMemoryRawDataLake(RawDataLakePort):
    """Local fallback — stores records in memory. Use only for development."""

    def __init__(self) -> None:
        self._store: list[dict] = []

    def store(self, records: list[dict]) -> list[str]:
        keys = []
        for record in records:
            key = f"memory/{uuid.uuid4()}"
            self._store.append({"key": key, **record})
            keys.append(key)
        return keys

    def all(self) -> list[dict]:
        return list(self._store)
