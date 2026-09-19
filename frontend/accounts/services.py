"""
Cliente HTTP hacia el backend FastAPI para las operaciones de cuenta.

Django mantiene su propia sesion (django.contrib.auth) para proteger las
vistas del sitio, y ademas sincroniza cada usuario con el backend FastAPI
para poder usar sus endpoints de reconocimiento facial (que requieren un
JWT propio). El token de FastAPI se guarda en `request.session`.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TIMEOUT = 8  # segundos


class FastAPIError(Exception):
    """Error de comunicacion o de negocio al hablar con el backend FastAPI."""


def register_user(username: str, email: str, password: str) -> dict:
    try:
        resp = requests.post(
            f"{settings.FASTAPI_BASE_URL}/auth/register",
            json={"username": username, "email": email or None, "password": password},
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        logger.warning("No se pudo contactar al backend FastAPI: %s", exc)
        raise FastAPIError("El servicio de reconocimiento facial no esta disponible ahora mismo") from exc

    data = resp.json()
    if resp.status_code >= 400:
        raise FastAPIError(data.get("detail", "No se pudo registrar el usuario en la API"))
    return data


def login_user(username: str, password: str) -> str:
    """Devuelve el access_token JWT del backend FastAPI."""
    try:
        resp = requests.post(
            f"{settings.FASTAPI_BASE_URL}/auth/login",
            data={"username": username, "password": password},
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        logger.warning("No se pudo contactar al backend FastAPI: %s", exc)
        raise FastAPIError("El servicio de reconocimiento facial no esta disponible ahora mismo") from exc

    data = resp.json()
    if resp.status_code >= 400:
        raise FastAPIError(data.get("detail", "No se pudo iniciar sesion en la API"))
    return data["access_token"]
