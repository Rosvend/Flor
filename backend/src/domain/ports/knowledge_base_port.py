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
    def query_with_scores(
        self,
        text: str,
        k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[tuple[KnowledgeBaseEntry, float]]:
        """Like query(), but each result is paired with a similarity score in [0, 1]
        (1.0 = identical, 0.0 = orthogonal). Higher is better."""
        ...

    @abstractmethod
    def delete_by_source(self, source_path: str) -> None: ...
