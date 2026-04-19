"""Seed the demo user: demo@flor.local / Flor123!"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../.env"))

from src.infrastructure.persistence.database import init_db
from src.infrastructure.persistence.postgres_user_repository import PostgresUserRepository
from src.infrastructure.auth.bcrypt_password_hasher import BcryptPasswordHasher
from src.domain.entities.user import User

init_db()

repo = PostgresUserRepository()
hasher = BcryptPasswordHasher()

DEMO_EMAIL = "demo@flor.local"
DEMO_PASSWORD = "Flor123!"

if repo.exists_by_email(DEMO_EMAIL):
    print(f"Usuario {DEMO_EMAIL} ya existe — nada que hacer.")
else:
    demo_user = User(
        id=str(uuid.uuid4()),
        nombre="Demo Alcaldía",
        correo_electronico=DEMO_EMAIL,
        password_hash=hasher.hash(DEMO_PASSWORD),
        organization_id=1,
    )
    repo.save(demo_user)
    print(f"Usuario demo creado: {DEMO_EMAIL} / {DEMO_PASSWORD}")
