"""
Punto de entrada de la API FastAPI.

Ejecutar en desarrollo:
    uvicorn main:app --reload --port 8001
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import ALLOWED_ORIGINS
from database import init_db
from routers import auth

app = FastAPI(title="API de Reconocimiento Facial")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "facial-recognition-api"}
