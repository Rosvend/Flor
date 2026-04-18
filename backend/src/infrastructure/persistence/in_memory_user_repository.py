from src.domain.entities.user import User


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._store: dict[str, User] = {}

    def find_by_email(self, email: str) -> User | None:
        for user in self._store.values():
            if user.correo_electronico == email:
                return user
        return None

    def find_by_id(self, user_id: str) -> User | None:
        return self._store.get(user_id)

    def save(self, user: User) -> None:
        self._store[user.id] = user

    def exists_by_email(self, email: str) -> bool:
        return self.find_by_email(email) is not None
