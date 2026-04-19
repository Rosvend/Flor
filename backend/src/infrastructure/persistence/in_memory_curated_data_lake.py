import uuid

from src.domain.ports.curated_data_lake import CuratedDataLakePort


class InMemoryCuratedDataLake(CuratedDataLakePort):
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    def store(self, records: list[dict]) -> list[str]:
        keys = []
        for record in records:
            key = f"memory/{uuid.uuid4()}"
            self._store[key] = record
            keys.append(key)
        return keys

    def update(self, key: str, record: dict) -> None:
        self._store[key] = record
