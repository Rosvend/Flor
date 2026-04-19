"""
Script para crear/actualizar usuario administrador en PostgreSQL.
Ejecutar:  uv run python scripts/seed_admin.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")

from src.infrastructure.persistence.database import get_session, init_db
from src.infrastructure.auth.bcrypt_password_hasher import BcryptPasswordHasher
from sqlalchemy import text

hasher = BcryptPasswordHasher()

# Inicializar tablas
init_db()

# Crear hash REAL de bcrypt
password_hash = hasher.hash("admin123")
print(f"Hash generado: {password_hash}")

with get_session() as session:
    existing = session.execute(
        text("SELECT id, correo_electronico FROM users WHERE correo_electronico = :email"),
        {"email": "admin@flor.com"}
    ).fetchone()
    
    if existing:
        session.execute(
            text("UPDATE users SET password_hash = :hash WHERE correo_electronico = :email"),
            {"hash": password_hash, "email": "admin@flor.com"}
        )
        session.commit()
        print(f"[OK] Usuario admin@flor.com actualizado (id: {existing.id})")
    else:
        session.execute(
            text("""
                INSERT INTO users (nombre, correo_electronico, password_hash, organization_id)
                VALUES (:nombre, :email, :hash, :org_id)
            """),
            {
                "nombre": "Administrador Flor",
                "email": "admin@flor.com",
                "hash": password_hash,
                "org_id": 1,
            }
        )
        session.commit()
        print("[OK] Usuario admin@flor.com creado exitosamente")

# Verificar
with get_session() as session:
    user = session.execute(
        text("SELECT id, nombre, correo_electronico, password_hash, organization_id FROM users WHERE correo_electronico = :email"),
        {"email": "admin@flor.com"}
    ).fetchone()
    
    if user:
        ok = hasher.verify("admin123", user.password_hash)
        print(f"\nVerificacion final:")
        print(f"   ID:    {user.id}")
        print(f"   Nombre: {user.nombre}")
        print(f"   Email:  {user.correo_electronico}")
        print(f"   Org:    {user.organization_id}")
        print(f"   Login funciona:  {'SI' if ok else 'NO - FALLO'}")
    else:
        print("[ERROR] No se encontro el usuario")
