from src.domain.ports.raw_data_lake import RawDataLakePort
from src.application.dtos.ingest_dtos import IngestRawMessagesInput, IngestRawMessagesOutput


class IngestRawMessages:
    def __init__(self, data_lake: RawDataLakePort) -> None:
        self._data_lake = data_lake

    def execute(self, input_dto: IngestRawMessagesInput) -> IngestRawMessagesOutput:
        keys = self._data_lake.store(input_dto.records)
        return IngestRawMessagesOutput(stored_keys=keys, count=len(keys))
