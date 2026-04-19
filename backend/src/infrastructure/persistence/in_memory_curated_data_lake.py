import uuid

from src.domain.ports.curated_data_lake import CuratedDataLakePort


class InMemoryCuratedDataLake(CuratedDataLakePort):
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}
        self._counter = 0

    def store(self, records: list[dict]) -> list[str]:
        keys = []
        for record in records:
            if "id" not in record or record["id"] is None:
                self._counter += 1
                record["id"] = self._counter
            key = f"memory/{uuid.uuid4()}"
            self._store[key] = record
            keys.append(key)
        return keys

    def update(self, key: str, record: dict) -> None:
        self._store[key] = record
