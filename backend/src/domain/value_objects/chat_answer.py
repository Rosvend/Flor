from dataclasses import dataclass, field


@dataclass(frozen=True)
class ChatSource:
    title: str
    excerpt: str


@dataclass(frozen=True)
class ChatAnswer:
    text: str
    used_fallback: bool
    sources: list[ChatSource] = field(default_factory=list)
