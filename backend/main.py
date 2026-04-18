from fastapi import FastAPI

from src.interfaces.http.ingest_router import router as ingest_router

app = FastAPI(title="PQRS Optimization API", version="0.1.0")

app.include_router(ingest_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "pqrs-backend"}
