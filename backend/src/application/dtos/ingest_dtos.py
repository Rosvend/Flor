from dataclasses import dataclass


@dataclass
class IngestRawMessagesInput:
    records: list[dict]


@dataclass
class IngestRawMessagesOutput:
    stored_keys: list[str]
    count: int
