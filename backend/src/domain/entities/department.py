from dataclasses import dataclass, field

from ..value_objects.department_type import DepartmentType


@dataclass(frozen=True)
class Department:
    id: str
    name: str
    type: DepartmentType
    aliases: tuple[str, ...] = ()
    scope: str = ""
    parent_id: str | None = None
    contact: dict[str, str] = field(default_factory=dict)
