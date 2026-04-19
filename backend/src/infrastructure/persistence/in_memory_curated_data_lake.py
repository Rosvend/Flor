from src.domain.ports.curated_data_lake import CuratedDataLakePort


class InMemoryCuratedDataLake(CuratedDataLakePort):
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}  # radicado -> record
        self._counter = 0

    def next_radicado(self) -> str:
        import uuid
        from datetime import datetime, timezone
        date = datetime.now(timezone.utc).strftime("%Y%m%d")
        suffix = uuid.uuid4().hex[:8].upper()
        return f"RAD-{date}-{suffix}"

    def store(self, records: list[dict]) -> list[str]:
        keys = []
        for record in records:
            radicado = record.get("radicado") or self.next_radicado()
            record["radicado"] = radicado
            self._store[radicado] = record
            keys.append(radicado)
        return keys

    def update_by_radicado(self, radicado: str, updates: dict) -> dict | None:
        """Merge-update: merges `updates` into the existing record so pipeline
        stages can add fields incrementally (analisis_ia, resumen_ia, etc.)
        without overwriting the entire document."""
        existing = self._store.get(radicado)
        if existing is None:
            # Fallback: treat as full replacement if record doesn't exist yet
            self._store[radicado] = updates
            return updates
        existing.update(updates)
        self._store[radicado] = existing
        return existing

    def get_by_radicado(self, radicado: str) -> dict | None:
        return self._store.get(radicado)

    def get_all(self) -> list[dict]:
        return list(self._store.values())
