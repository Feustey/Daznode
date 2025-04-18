from pydantic import BaseModel


class Token(BaseModel):
    """Modèle de jeton d'accès"""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Charge utile du jeton JWT"""
    sub: str = None 