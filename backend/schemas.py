"""
Esquemas Pydantic: validacion de entrada/salida de la API.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: Optional[EmailStr] = None
    has_face_registered: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class ImagePayload(BaseModel):
    """
    Imagen capturada desde la camara del navegador (getUserMedia + canvas),
    enviada como Data URL base64: "data:image/jpeg;base64,/9j/4AAQ...".
    """

    image_base64: str


class FaceRegisterResponse(BaseModel):
    detail: str
    total_samples: int


class RecognitionResult(BaseModel):
    matched: bool
    username: Optional[str] = None
    confidence: Optional[float] = None
    message: str
