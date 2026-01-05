from pydantic import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Configuration de l'application"""
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/aitechwatch")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "sk-...-votre-clé...")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Arize
    ARIZE_API_KEY: str = os.getenv("ARIZE_API_KEY", "arize-api-key")
    ARIZE_SPACE_KEY: str = os.getenv("ARIZE_SPACE_KEY", "arize-space-key")
    
    # Application
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Tech Watch Agent"
    VERSION: str = "1.0.0"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100  # requêtes par heure par utilisateur
    RATE_LIMIT_WINDOW: int = 3600  # en secondes
    
    # Cache
    CACHE_EXPIRE_SECONDS: int = 3600  # 1 heure
    
    class Config:
        env_file = ".env"

settings = Settings()