from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base pour les modèles d'utilisateur"""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Modèle pour la création d'un utilisateur"""
    email: EmailStr
    password: str
    full_name: str


class UserUpdate(UserBase):
    """Modèle pour la mise à jour d'un utilisateur"""
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """Modèle pour un utilisateur en base de données"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class User(UserInDBBase):
    """Modèle d'utilisateur retourné aux clients"""
    pass


class UserResponse(BaseModel):
    """Réponse après création ou mise à jour d'un utilisateur"""
    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime 