import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        url = os.environ["DATABASE_URL"]
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def get_session() -> Session:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    return _SessionLocal()


def init_db() -> None:
    """Create tables if they don't exist (idempotent)."""
    ddl = """
    CREATE TABLE IF NOT EXISTS users (
        id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        nombre          TEXT NOT NULL,
        correo_electronico TEXT NOT NULL UNIQUE,
        password_hash   TEXT NOT NULL,
        organization_id INTEGER NOT NULL DEFAULT 1,
        created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS departments (
        id          VARCHAR(100) PRIMARY KEY,
        name        TEXT NOT NULL,
        type        VARCHAR(50), 
        aliases     TEXT[],      
        scope       TEXT,        
        parent_id   VARCHAR(100) REFERENCES departments(id),
        contact     JSONB DEFAULT '{}'::jsonb
    );
    """
    with get_engine().begin() as conn:
        conn.execute(text(ddl))
