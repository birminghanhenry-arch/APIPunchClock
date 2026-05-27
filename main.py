"""
main.py — Punto de entrada.
Solo inicializa la app, registra routers y el health check.
Cero lógica aquí.

    uvicorn main:app --reload --port 8765
    http://localhost:8765/docs
"""
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core    import settings
from app.models  import create_tables
from app.routers import router

create_tables()

app = FastAPI(
    title       = settings.APP_TITLE,
    version     = settings.APP_VERSION,
    description = "API de control de asistencia con marcaje por PIN.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
