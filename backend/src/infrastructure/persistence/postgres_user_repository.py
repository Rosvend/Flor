from sqlalchemy import text

from src.domain.entities.user import User
from src.infrastructure.persistence.database import get_session


class PostgresUserRepository:
    def find_by_email(self, email: str) -> User | None:
        with get_session() as session:
            row = session.execute(
                text("SELECT id, nombre, correo_electronico, password_hash, organization_id FROM users WHERE correo_electronico = :email"),
                {"email": email},
            ).fetchone()
        return self._to_entity(row) if row else None

    def find_by_id(self, user_id: str) -> User | None:
        with get_session() as session:
            row = session.execute(
                text("SELECT id, nombre, correo_electronico, password_hash, organization_id FROM users WHERE id = :id"),
                {"id": user_id},
            ).fetchone()
        return self._to_entity(row) if row else None

    def save(self, user: User) -> None:
        with get_session() as session:
            session.execute(
                text("""
                    INSERT INTO users (id, nombre, correo_electronico, password_hash, organization_id)
                    VALUES (:id, :nombre, :correo, :hash, :org_id)
                    ON CONFLICT (correo_electronico) DO UPDATE
                    SET nombre = EXCLUDED.nombre,
                        password_hash = EXCLUDED.password_hash,
                        organization_id = EXCLUDED.organization_id
                """),
                {
                    "id": user.id,
                    "nombre": user.nombre,
                    "correo": user.correo_electronico,
                    "hash": user.password_hash,
                    "org_id": user.organization_id,
                },
            )
            session.commit()

    def exists_by_email(self, email: str) -> bool:
        return self.find_by_email(email) is not None

    @staticmethod
    def _to_entity(row) -> User:
        return User(
            id=str(row.id),
            nombre=row.nombre,
            correo_electronico=row.correo_electronico,
            password_hash=row.password_hash,
            organization_id=row.organization_id,
        )
