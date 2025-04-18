from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Any

from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.config import settings
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.api.deps import get_db
from app.crud.user import create_user, get_user_by_email

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register_user(*, user_in: UserCreate, db=Depends(get_db)) -> Any:
    """
    Créer un nouvel utilisateur.
    """
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà.",
        )
    
    user = create_user(db, obj_in=user_in)
    return user


@router.post("/login", response_model=Token)
def login_access_token(
    db=Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Authentification OAuth2 compatible pour obtenir un jeton JWT.
    """
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    } 