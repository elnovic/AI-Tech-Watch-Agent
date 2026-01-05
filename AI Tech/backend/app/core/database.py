from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

# Création de l'engine SQLAlchemy
if settings.DATABASE_URL.startswith("sqlite"):
    # Pour SQLite, on utilise des chemins de fichiers
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},  # Nécessaire pour SQLite
        pool_pre_ping=True,
        echo=False
    )
else:
    # Pour PostgreSQL, on utilise la configuration normale
    engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # Vérifie la connexion avant chaque requête
        pool_recycle=300,    # Recycle les connexions toutes les 5 minutes
        echo=False           # Désactiver en production
    )

# Session locale
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base pour les modèles
Base = declarative_base()


def get_db():
    """Générateur de session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
