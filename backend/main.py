from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

from src.interfaces.http.auth_router import router as auth_router
from src.interfaces.http.ingest_router import router as ingest_router
from src.interfaces.http.ingest_curated_router import router as ingest_curated_router
from src.infrastructure.container import user_repository, password_hasher                                                                                                             
from src.domain.entities.user import User

app = FastAPI(title="PQRS Optimization API", version="0.1.0")

app.include_router(ingest_router, prefix="/api/v1")
app.include_router(ingest_curated_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")


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

