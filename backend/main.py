from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.interfaces.http.auth_router import router as auth_router
from src.interfaces.http.ingest_router import router as ingest_router
from src.interfaces.http.ingest_curated_router import router as ingest_curated_router
from src.interfaces.http.pqrs_router import router as pqrs_router
from src.infrastructure.container import user_repository, password_hasher                                                                                                             
from src.domain.entities.user import User

app = FastAPI(title="PQRS Optimization API", version="0.1.0")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://flor.vercel.app",
    "https://flor.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest_router, prefix="/api/v1")
app.include_router(ingest_curated_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(pqrs_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "pqrs-backend"}

_test_user = User(                                                                                                                                                                    
    id="1",
    nombre="Admin Test",                                                                                                                                                              
    correo_electronico="admin@test.com",
    password_hash=password_hasher.hash("admin123"),                                                                                                                                   
    organization_id=1,
)                                                                                                                                                                                     
user_repository.save(_test_user)

