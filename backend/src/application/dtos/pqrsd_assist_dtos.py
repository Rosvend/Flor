from dataclasses import dataclass, field


@dataclass
class SummarizePQRSDInput:
    content: str


@dataclass
class SummarizePQRSDOutput:
    lead: str
    topics: list[str]
    original: str


@dataclass
class DraftResponseInput:
    content: str
    asunto: str | None = None
    citizen_name: str | None = None


@dataclass
class DraftSourceDTO:
    title: str
    excerpt: str


@dataclass
class DraftResponseOutput:
    draft: str
    sources: list[DraftSourceDTO] = field(default_factory=list)
    used_fallback: bool = False
