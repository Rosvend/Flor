from dataclasses import dataclass


@dataclass
class IngestCuratedMessagesInput:
    records: list[dict]


@dataclass
class IngestCuratedMessagesOutput:
    stored_keys: list[str]
    count: int
