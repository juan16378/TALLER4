"""
Endpoints de autenticacion: registro de usuarios y login con JWT.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import deps
import models_db
import schemas
from database import get_db
from security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models_db.User).filter(models_db.User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

    user = models_db.User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login estilo OAuth2 password flow (compatible con Swagger /docs
    y con formularios application/x-www-form-urlencoded desde Django).
    """
    user = db.query(models_db.User).filter(models_db.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return schemas.Token(access_token=access_token)


@router.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: models_db.User = Depends(deps.get_current_user)):
    return current_user
