from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Crée un moteur SQLAlchemy
engine = None
if settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        echo=True
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # Pour le développement sans base de données
    SessionLocal = sessionmaker()


# Base pour les modèles SQLAlchemy
Base = declarative_base() 