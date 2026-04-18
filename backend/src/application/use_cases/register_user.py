from uuid import uuid4

from src.application.dtos.auth_dtos import RegisterInput, RegisterOutput
from src.domain.entities.user import User
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.ports.user_repository import UserRepository


class UserAlreadyExistsError(Exception):
    pass


class RegisterUser:
    def __init__(self, user_repo: UserRepository, password_hasher: PasswordHasher) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher

    def execute(self, input: RegisterInput) -> RegisterOutput:
        if self._user_repo.exists_by_email(input.correo_electronico):
            raise UserAlreadyExistsError()

        user = User(
            id=str(uuid4()),
            nombre=input.nombre,
            correo_electronico=input.correo_electronico,
            password_hash=self._password_hasher.hash(input.password),
            organization_id=input.organization_id,
        )
        self._user_repo.save(user)

        return RegisterOutput(
            user_id=user.id,
            nombre=user.nombre,
            correo_electronico=user.correo_electronico,
            organization_id=user.organization_id,
        )
