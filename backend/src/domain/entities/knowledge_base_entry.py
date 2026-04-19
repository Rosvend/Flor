from dataclasses import dataclass, field


@dataclass(frozen=True)
class KnowledgeBaseEntry:
    id: str
    source_path: str
    heading_path: tuple[str, ...]
    content: str
    metadata: dict[str, str] = field(default_factory=dict)
