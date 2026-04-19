from __future__ import annotations

import json
import unicodedata
from pathlib import Path

from ...domain.entities.department import Department
from ...domain.ports.department_repository_port import DepartmentRepositoryPort
from ...domain.value_objects.department_type import DepartmentType


def _normalize(text: str) -> str:
    stripped = unicodedata.normalize("NFKD", text)
    no_accents = "".join(c for c in stripped if not unicodedata.combining(c))
    return no_accents.strip().lower()


class JsonDepartmentRepository(DepartmentRepositoryPort):
    def __init__(self, seed_path: Path):
        raw = json.loads(seed_path.read_text(encoding="utf-8"))
        self._by_id: dict[str, Department] = {}
        self._alias_index: dict[str, str] = {}
        for item in raw:
            dept = Department(
                id=item["id"],
                name=item["name"],
                type=DepartmentType(item["type"]),
                aliases=tuple(item.get("aliases", ())),
                scope=item.get("scope", ""),
                parent_id=item.get("parent_id"),
                contact=dict(item.get("contact", {})),
            )
            self._by_id[dept.id] = dept
            for alias in (dept.name, *dept.aliases):
                self._alias_index[_normalize(alias)] = dept.id

    def get_by_id(self, id: str) -> Department | None:
        return self._by_id.get(id)

    def list_all(self) -> list[Department]:
        return list(self._by_id.values())

    def find_by_alias(self, alias: str) -> Department | None:
        dept_id = self._alias_index.get(_normalize(alias))
        return self._by_id.get(dept_id) if dept_id else None
