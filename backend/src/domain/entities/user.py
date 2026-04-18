from dataclasses import dataclass


@dataclass
class User:
    id: str
    nombre: str
    correo_electronico: str
    password_hash: str
    organization_id: int
