from fastapi import FastAPI

app = FastAPI(title="PQRS Optimization API", version="0.1.0")


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "pqrs-backend"}
