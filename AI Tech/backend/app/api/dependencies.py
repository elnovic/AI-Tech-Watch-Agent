from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.core.config import settings
import jwt
import logging

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[str]:
    """Extrait l'ID utilisateur à partir du token d'authentification"""
    try:
        # Pour une implémentation complète, on vérifierait le token JWT
        # Pour cette version de démonstration, on retourne simplement un ID utilisateur factice
        token = credentials.credentials
        
        # Dans une vraie implémentation, on décoderait le token JWT
        # payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        # user_id = payload.get("sub")
        
        # Pour cette démo, on retourne un ID utilisateur basé sur le token
        return f"user_{hash(token) % 10000}" if token else None
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Impossible de valider les identifiants",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logging.error(f"Erreur lors de l'extraction de l'utilisateur: {e}")
        return None

def rate_limit_check(user_id: str) -> bool:
    """Vérifie si l'utilisateur a dépassé sa limite de requêtes"""
    # Cette fonction serait implémentée avec Redis pour le rate limiting
    # Pour cette démo, on retourne toujours True (pas de limite)
    return True

def validate_api_key(api_key: Optional[str] = None) -> bool:
    """Valide la clé API si requise"""
    # Pour cette démo, on n'applique pas de validation stricte
    # Dans une vraie application, on vérifierait la clé API dans une base de données
    return True

# Dépendance pour les endpoints qui nécessitent une authentification
async def get_authenticated_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    user_id = get_current_user(credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentification requise",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id