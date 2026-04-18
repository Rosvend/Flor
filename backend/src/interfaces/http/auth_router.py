from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.application.dtos.auth_dtos import LoginInput, RegisterInput
from src.application.use_cases.login_user import InvalidCredentialsError, LoginUser
from src.application.use_cases.register_user import RegisterUser, UserAlreadyExistsError
from src.infrastructure.auth.jwt_token_generator import InvalidTokenError
from src.infrastructure.container import password_hasher, token_generator, user_repository

router = APIRouter(prefix="/auth", tags=["auth"])

_bearer = HTTPBearer()


class LoginRequest(BaseModel):
    correo_electronico: str
    password: str


class RegisterRequest(BaseModel):
    nombre: str
    correo_electronico: str
    password: str
    organization_id: int


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    nombre: str
    organization_id: int


class RegisterResponse(BaseModel):
    user_id: str
    nombre: str
    correo_electronico: str
    organization_id: int


class MeResponse(BaseModel):
    user_id: str
    nombre: str
    correo_electronico: str
    organization_id: int


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest):
    use_case = RegisterUser(user_repository, password_hasher)
    try:
        result = use_case.execute(RegisterInput(
            nombre=req.nombre,
            correo_electronico=req.correo_electronico,
            password=req.password,
            organization_id=req.organization_id,
        ))
    except UserAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya está registrado")
    return RegisterResponse(
        user_id=result.user_id,
        nombre=result.nombre,
        correo_electronico=result.correo_electronico,
        organization_id=result.organization_id,
    )


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
def me(credentials: HTTPAuthorizationCredentials = Depends(_bearer)):
    try:
        payload = token_generator.decode(credentials.credentials)
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")

    user = user_repository.find_by_id(payload["sub"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    return MeResponse(
        user_id=user.id,
        nombre=user.nombre,
        correo_electronico=user.correo_electronico,
        organization_id=user.organization_id,
    )
