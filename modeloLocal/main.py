import os
from fastapi import FastAPI
from dotenv import load_dotenv

# Cargar configuración ANTES de importar módulos que dependen de las variables de entorno
load_dotenv()

from .presentation.api import router

app = FastAPI(
    title="PQRSD Assistant - Strict Clean Architecture",
    description="Sistema organizado por capas (Domain, Application, Infrastructure, Presentation)"
)

# Incluir rutas de la capa de presentación
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
