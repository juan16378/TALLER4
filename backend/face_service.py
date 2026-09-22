"""
Servicio de reconocimiento facial.

Implementacion con OpenCV (deteccion Haar Cascade + reconocedor LBPH):
  - No requiere compilar dlib (a diferencia de la libreria `face_recognition`),
    lo que la hace mucho mas portable para instalar en distintos entornos,
    incluyendo funciones serverless.
  - Reconocimiento facial real (no un mock): cada usuario entrena el modelo
    con sus propias fotos de referencia y luego se predice contra ese
    modelo entrenado.

Flujo:
  1. `register_face(user_id, image_bytes)` guarda la foto recortada del
     rostro del usuario y reentrena el modelo global LBPH con todas las
     muestras existentes.
  2. `recognize_face(image_bytes)` detecta el rostro en la imagen recibida
     y lo compara contra el modelo entrenado, devolviendo el usuario mas
     parecido (o "sin coincidencia" si la confianza no supera el umbral).
"""
import json
from typing import Optional

import cv2
import numpy as np

from config import FACE_SIZE, FACES_DIR, LABELS_PATH, LBPH_CONFIDENCE_THRESHOLD, MODEL_PATH

_face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


class NoFaceDetectedError(Exception):
    """No se detecto ningun rostro en la imagen enviada."""


def _ensure_dirs() -> None:
    FACES_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)


def decode_image(image_bytes: bytes) -> np.ndarray:
    """Convierte bytes (jpg/png) en una imagen en escala de grises (numpy array)."""
    array = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(array, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("No se pudo decodificar la imagen recibida")
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def extract_face(gray_image: np.ndarray) -> np.ndarray:
    """
    Detecta el rostro mas grande de la imagen, lo recorta y lo normaliza
    al tamano FACE_SIZE. Lanza NoFaceDetectedError si no encuentra ninguno.
    """
    faces = _face_cascade.detectMultiScale(
        gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60)
    )
    if len(faces) == 0:
        raise NoFaceDetectedError("No se detecto ningun rostro en la imagen")

    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face = gray_image[y : y + h, x : x + w]
    face = cv2.resize(face, FACE_SIZE)
    face = cv2.equalizeHist(face)
    return face


def _load_labels() -> dict:
    if LABELS_PATH.exists():
        return json.loads(LABELS_PATH.read_text())
    return {}


def _save_labels(labels: dict) -> None:
    LABELS_PATH.write_text(json.dumps(labels, indent=2))


def register_face(user_id: int, username: str, image_bytes: bytes) -> int:
    """
    Guarda una nueva muestra de rostro para el usuario y reentrena el
    modelo LBPH con todas las muestras disponibles.
    """
    _ensure_dirs()

    gray = decode_image(image_bytes)
    face = extract_face(gray)

    user_dir = FACES_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    existing = list(user_dir.glob("*.png"))
    sample_path = user_dir / f"{len(existing) + 1}.png"
    cv2.imwrite(str(sample_path), face)

    _retrain_model()
    return len(existing) + 1


def _retrain_model() -> None:
    """Reentrena el reconocedor LBPH con todas las muestras guardadas en disco."""
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    images = []
    labels = []
    label_map: dict[str, int] = {}
    next_label = 0

    for user_dir in sorted(FACES_DIR.glob("*")):
        if not user_dir.is_dir():
            continue
        user_id = user_dir.name
        label_map[str(next_label)] = user_id
        for sample_path in user_dir.glob("*.png"):
            img = cv2.imread(str(sample_path), cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            images.append(img)
            labels.append(next_label)
        next_label += 1

    if not images:
        return

    recognizer.train(images, np.array(labels))
    recognizer.write(str(MODEL_PATH))
    _save_labels(label_map)


def recognize_face(image_bytes: bytes) -> tuple[Optional[str], Optional[float]]:
    """
    Detecta el rostro en la imagen y lo compara contra el modelo entrenado.
    """
    if not MODEL_PATH.exists():
        return None, None

    gray = decode_image(image_bytes)
    face = extract_face(gray)

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(MODEL_PATH))
    label_map = _load_labels()

    label, confidence = recognizer.predict(face)
    if confidence > LBPH_CONFIDENCE_THRESHOLD:
        return None, confidence

    user_id = label_map.get(str(label))
    return user_id, confidence
