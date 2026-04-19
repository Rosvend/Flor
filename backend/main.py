from dotenv import load_dotenv
load_dotenv()

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

from src.interfaces.http.auth_router import router as auth_router
from src.interfaces.http.chatbot_router import router as chatbot_router
from src.interfaces.http.ingest_router import router as ingest_router
from src.interfaces.http.ingest_curated_router import router as ingest_curated_router
from src.interfaces.http.pqrs_router import router as pqrs_router
from src.infrastructure.container import user_repository, password_hasher
from src.domain.entities.user import User

app = FastAPI(title="PQRS Optimization API", version="0.1.0")

_cors_origins = [
    o.strip() for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,https://flor.vercel.app",
    ).split(",") if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router, prefix="/api/v1")
app.include_router(ingest_curated_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(pqrs_router, prefix="/api/v1")
app.include_router(chatbot_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "pqrs-backend"}

