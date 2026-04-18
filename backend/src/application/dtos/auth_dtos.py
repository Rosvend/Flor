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
