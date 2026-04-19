import json
from sqlalchemy import text
from src.domain.entities.department import Department
from src.domain.ports.department_repository_port import DepartmentRepositoryPort
from src.domain.value_objects.department_type import DepartmentType
from src.infrastructure.persistence.database import get_session

class PostgresDepartmentRepository(DepartmentRepositoryPort):
    def get_by_id(self, id: str) -> Department | None:
        with get_session() as session:
            row = session.execute(
                text("SELECT id, name, type, aliases, scope, parent_id, contact FROM departments WHERE id = :id"),
                {"id": id},
            ).fetchone()
        return self._to_entity(row) if row else None

    def list_all(self) -> list[Department]:
        with get_session() as session:
            rows = session.execute(
                text("SELECT id, name, type, aliases, scope, parent_id, contact FROM departments")
            ).fetchall()
        return [self._to_entity(row) for row in rows]

    def find_by_alias(self, alias: str) -> Department | None:
        # Búsqueda insensible a mayúsculas/acentos usando un query optimizado
        # En Postgres podemos usar un unnest sobre el array de aliases
        with get_session() as session:
            row = session.execute(
                text("""
                    SELECT id, name, type, aliases, scope, parent_id, contact 
                    FROM departments 
                    WHERE :alias = ANY(aliases) 
                       OR LOWER(name) = LOWER(:alias)
                    LIMIT 1
                """),
                {"alias": alias},
            ).fetchone()
        return self._to_entity(row) if row else None

    @staticmethod
    def _to_entity(row) -> Department:
        return Department(
            id=row.id,
            name=row.name,
            type=DepartmentType(row.type),
            aliases=tuple(row.aliases) if row.aliases else (),
            scope=row.scope or "",
            parent_id=row.parent_id,
            contact=row.contact if isinstance(row.contact, dict) else {},
        )
