from dataclasses import dataclass


@dataclass
class LoginInput:
    correo_electronico: str
    password: str


@dataclass
class LoginOutput:
    access_token: str
    token_type: str
    user_id: str
    nombre: str
    organization_id: int


@dataclass
class RegisterInput:
    nombre: str
    correo_electronico: str
    password: str
    organization_id: int


@dataclass
class RegisterOutput:
    user_id: str
    nombre: str
    correo_electronico: str
    organization_id: int
