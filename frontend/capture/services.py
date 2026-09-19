"""
Cliente HTTP hacia los endpoints de reconocimiento facial del backend FastAPI.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)
TIMEOUT = 15  # el analisis de imagen puede tardar un poco mas que un login


class FastAPIError(Exception):
    pass


def register_face(image_base64: str, token: str) -> dict:
    try:
        resp = requests.post(
            f"{settings.FASTAPI_BASE_URL}/face/register",
            json={"image_base64": image_base64},
            headers={"Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        logger.warning("Fallo al contactar FastAPI /face/register: %s", exc)
        raise FastAPIError("No se pudo contactar el servicio de reconocimiento facial") from exc

    data = resp.json()
    if resp.status_code >= 400:
        raise FastAPIError(data.get("detail", "No se pudo registrar el rostro"))
    return data


def recognize_face(image_base64: str) -> dict:
    try:
        resp = requests.post(
            f"{settings.FASTAPI_BASE_URL}/face/recognize",
            json={"image_base64": image_base64},
            timeout=TIMEOUT,
        )
    except requests.RequestException as exc:
        logger.warning("Fallo al contactar FastAPI /face/recognize: %s", exc)
        raise FastAPIError("No se pudo contactar el servicio de reconocimiento facial") from exc

    data = resp.json()
    if resp.status_code >= 400:
        raise FastAPIError(data.get("detail", "No se pudo procesar la imagen"))
    return data
