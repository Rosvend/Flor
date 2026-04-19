from src.domain.ports.curated_data_lake import CuratedDataLakePort
from src.application.dtos.ingest_curated_dtos import IngestCuratedMessagesInput, IngestCuratedMessagesOutput


class IngestCuratedMessages:
    def __init__(self, data_lake: CuratedDataLakePort) -> None:
        self._data_lake = data_lake

    def execute(self, input_dto: IngestCuratedMessagesInput) -> IngestCuratedMessagesOutput:
        keys = self._data_lake.store(input_dto.records)
        return IngestCuratedMessagesOutput(stored_keys=keys, count=len(keys))
