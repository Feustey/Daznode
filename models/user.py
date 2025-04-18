from datetime import datetime
from typing import List, Optional


class User:
    """Classe utilisateur temporaire pour le développement
    À remplacer par un modèle SQLAlchemy lorsque la base de données sera configurée
    """
    
    def __init__(
        self,
        id: int,
        email: str,
        hashed_password: str,
        full_name: Optional[str] = None,
        is_active: bool = True,
        is_superuser: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now() 