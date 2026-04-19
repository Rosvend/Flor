from abc import ABC, abstractmethod
from typing import Iterable

from ..entities.knowledge_base_entry import KnowledgeBaseEntry


class KnowledgeBasePort(ABC):
    @abstractmethod
    def upsert(self, entries: Iterable[KnowledgeBaseEntry]) -> None: ...

    @abstractmethod
    def query(
        self,
        text: str,
        k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[KnowledgeBaseEntry]: ...

    @abstractmethod
    def delete_by_source(self, source_path: str) -> None: ...
