from dataclasses import dataclass, field


@dataclass
class QueryChatbotInput:
    question: str


@dataclass
class ChatbotSourceDTO:
    title: str
    excerpt: str


@dataclass
class QueryChatbotOutput:
    answer: str
    used_fallback: bool
    sources: list[ChatbotSourceDTO] = field(default_factory=list)


@dataclass
class IngestDocumentInput:
    filename: str
    content: bytes
    uploaded_by: str


@dataclass
class IngestDocumentOutput:
    chunks_indexed: int
    source_path: str
