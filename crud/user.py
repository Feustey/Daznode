from typing import Optional
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Fonction temporaire pour la démo: cherche un utilisateur par email
    À remplacer par une requête à la base de données
    """
    # Pour la démo, nous retournons un utilisateur fictif si l'email correspond
    if email == "admin@daznode.com":
        return User(
            id=1,
            email="admin@daznode.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password"
            full_name="Admin Daznode",
            is_active=True,
            is_superuser=True
        )
    return None


def create_user(db: Session, obj_in: UserCreate) -> User:
    """
    Fonction temporaire pour la démo: crée un nouvel utilisateur
    À remplacer par une requête d'insertion dans la base de données
    """
    # Pour la démo, nous retournons simplement un utilisateur fictif avec les données fournies
    return User(
        id=2,  # ID fictif
        email=obj_in.email,
        hashed_password=get_password_hash(obj_in.password),
        full_name=obj_in.full_name,
        is_active=True,
        is_superuser=False
    ) 