from abc import ABC, abstractmethod

from ..entities.department import Department


class DepartmentRepositoryPort(ABC):
    @abstractmethod
    def get_by_id(self, id: str) -> Department | None: ...

    @abstractmethod
    def list_all(self) -> list[Department]: ...

    @abstractmethod
    def find_by_alias(self, alias: str) -> Department | None: ...
