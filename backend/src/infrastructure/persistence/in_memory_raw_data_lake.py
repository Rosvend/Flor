import uuid

from src.domain.ports.raw_data_lake import RawDataLakePort


class InMemoryRawDataLake(RawDataLakePort):
    """Local fallback — stores records in memory. Use only for development."""

    def __init__(self) -> None:
        self._store: dict[str, dict] = {}
        self._binary_store: dict[str, bytes] = {}

    def store(self, records: list[dict]) -> list[str]:
        keys = []
        for record in records:
            key = f"memory/{uuid.uuid4()}"
            self._store[key] = record
            keys.append(key)
        return keys

    def get_all(self) -> dict[str, dict]:
        return dict(self._store)
        
    def delete(self, key: str) -> None:
        if key in self._store:
            del self._store[key]

    def store_binary(self, content: bytes, filename: str) -> str:
        key = f"memory/bin/{uuid.uuid4()}-{filename}"
        self._binary_store[key] = content
        return key
