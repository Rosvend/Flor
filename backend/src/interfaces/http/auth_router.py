from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.application.dtos.auth_dtos import LoginInput
from src.application.use_cases.login_user import InvalidCredentialsError, LoginUser
from src.infrastructure.auth.jwt_token_generator import InvalidTokenError
from src.infrastructure.container import password_hasher, token_generator, user_repository
from src.interfaces.http.deps import get_current_user, _bearer
from src.domain.entities.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

_bearer = HTTPBearer()


class LoginRequest(BaseModel):
    correo_electronico: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    nombre: str
    organization_id: int


class MeResponse(BaseModel):
    user_id: str
    nombre: str
    correo_electronico: str
    organization_id: int


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    use_case = LoginUser(user_repository, password_hasher, token_generator)
    try:
        result = use_case.execute(LoginInput(
            correo_electronico=req.correo_electronico,
            password=req.password,
        ))
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    return LoginResponse(
        access_token=result.access_token,
        token_type=result.token_type,
        user_id=result.user_id,
        nombre=result.nombre,
        organization_id=result.organization_id,
    )


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)):
    return MeResponse(
        user_id=user.id,
        nombre=user.nombre,
        correo_electronico=user.correo_electronico,
        organization_id=user.organization_id,
    )
