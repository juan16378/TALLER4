"""
Configuración centralizada del backend FastAPI.

Todos los valores sensibles se leen de variables de entorno para poder
desplegar de forma segura en Vercel (Project Settings -> Environment
Variables) sin hardcodear secretos en el código.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# --- Seguridad / JWT -------------------------------------------------------
SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esta-clave-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# --- Base de datos -----------------------------------------------------------
# SQLite por defecto (ideal para desarrollo local y para el taller).
# En Vercel el sistema de archivos es de solo lectura salvo /tmp, por lo que
# ahí se usa una ruta en /tmp (efímera) o, idealmente, una base de datos
# externa (Postgres, Turso, etc.) configurada vía DATABASE_URL.
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'app.db'}")

# --- Reconocimiento facial ---------------------------------------------------
# Carpeta donde se guardan las fotos de referencia y el modelo LBPH entrenado.
FACES_DIR = Path(os.getenv("FACES_DIR", BASE_DIR / "data" / "faces"))
MODEL_PATH = Path(os.getenv("MODEL_PATH", BASE_DIR / "models_store" / "lbph_model.yml"))
LABELS_PATH = Path(os.getenv("LABELS_PATH", BASE_DIR / "models_store" / "labels.json"))

# Tamaño al que se normaliza cada rostro recortado antes de entrenar/predecir.
FACE_SIZE = (200, 200)

# Umbral de confianza LBPH (distancia). Cuanto MÁS BAJO, más parecido.
# Valores típicos: <60 buena coincidencia, 60-90 dudosa, >90 se rechaza.
LBPH_CONFIDENCE_THRESHOLD = float(os.getenv("LBPH_CONFIDENCE_THRESHOLD", "80"))

# --- CORS ---------------------------------------------------------------
# Orígenes permitidos para que el frontend Django pueda consumir la API.
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
