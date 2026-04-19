from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from src.domain.entities.department import Department
from src.domain.value_objects.department_type import DepartmentType
from src.infrastructure.knowledge_base.json_department_repository import (
    JsonDepartmentRepository,
)

SEED_PATH = (
    Path(__file__).resolve().parents[3]
    / "src"
    / "infrastructure"
    / "knowledge_base"
    / "data"
    / "departments.json"
)


@pytest.fixture(scope="module")
def repo() -> JsonDepartmentRepository:
    return JsonDepartmentRepository(SEED_PATH)


def test_department_is_frozen():
    d = Department(
        id="x",
        name="X",
        type=DepartmentType.SECRETARIA,
    )
    with pytest.raises(FrozenInstanceError):
        d.name = "Y"  # type: ignore[misc]


def test_seed_has_26_top_level_departments(repo: JsonDepartmentRepository):
    top_level = [d for d in repo.list_all() if d.parent_id is None]
    assert len(top_level) == 26


def test_desarrollo_economico_has_subsecretarias(repo: JsonDepartmentRepository):
    parent = repo.get_by_id("secretaria_desarrollo_economico")
    assert parent is not None
    children = [
        d for d in repo.list_all()
        if d.parent_id == "secretaria_desarrollo_economico"
    ]
    assert len(children) >= 2
    assert all(c.type == DepartmentType.SUBSECRETARIA for c in children)


def test_get_by_id_unknown_returns_none(repo: JsonDepartmentRepository):
    assert repo.get_by_id("does_not_exist") is None


def test_find_by_alias_is_case_and_accent_insensitive(
    repo: JsonDepartmentRepository,
):
    hit = repo.find_by_alias("DESARROLLO ECONÓMICO")
    assert hit is not None
    assert hit.id == "secretaria_desarrollo_economico"

    assert repo.find_by_alias("desarrollo economico") is not None
    assert repo.find_by_alias("Secretaría de Desarrollo Económico") is not None


def test_find_by_alias_unknown_returns_none(repo: JsonDepartmentRepository):
    assert repo.find_by_alias("ministerio de magia") is None


def test_all_parent_ids_resolve(repo: JsonDepartmentRepository):
    ids = {d.id for d in repo.list_all()}
    for d in repo.list_all():
        if d.parent_id is not None:
            assert d.parent_id in ids, f"{d.id} points to missing parent {d.parent_id}"
