from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from typing import Generator, Optional

from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.session import SessionLocal
from app.models.user import User
from app.schemas.token import TokenPayload

# Point de terminaison pour l'authentification
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator:
    """
    Dépendance pour obtenir une session de base de données
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Dépendance pour obtenir l'utilisateur actuellement authentifié
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Informations d'authentification invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenPayload(sub=user_id)
    except JWTError:
        raise credentials_exception
    
    # Cette fonction doit être remplacée par l'implémentation de la base de données
    # Pour le moment, nous utilisons un mock pour le développement
    user = get_mock_user(db, token_data.sub)
    
    if user is None:
        raise credentials_exception
    
    return user


def get_mock_user(db: Session, user_id: str) -> User:
    """
    Fonction temporaire pour le développement: retourne un utilisateur fictif
    À remplacer par une requête à la base de données
    """
    # Mock d'un utilisateur pour le développement
    mock_user = User(
        id=1,
        email="admin@daznode.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
        full_name="Admin Daznode",
        is_active=True,
        is_superuser=True
    )
    
    return mock_user 