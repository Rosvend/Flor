from src.application.dtos.auth_dtos import LoginInput, LoginOutput
from src.domain.ports.password_hasher import PasswordHasher
from src.domain.ports.token_generator import TokenGenerator
from src.domain.ports.user_repository import UserRepository


class InvalidCredentialsError(Exception):
    pass


class LoginUser:
    def __init__(
        self,
        user_repo: UserRepository,
        password_hasher: PasswordHasher,
        token_gen: TokenGenerator,
    ) -> None:
        self._user_repo = user_repo
        self._password_hasher = password_hasher
        self._token_gen = token_gen

    def execute(self, input: LoginInput) -> LoginOutput:
        user = self._user_repo.find_by_email(input.correo_electronico)
        if user is None:
            raise InvalidCredentialsError()
        if not self._password_hasher.verify(input.password, user.password_hash):
            raise InvalidCredentialsError()

        token = self._token_gen.generate({
            "sub": user.id,
            "correo_electronico": user.correo_electronico,
            "organization_id": user.organization_id,
        })

        return LoginOutput(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            nombre=user.nombre,
            organization_id=user.organization_id,
        )
