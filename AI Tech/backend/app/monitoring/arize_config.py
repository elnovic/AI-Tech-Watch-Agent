import os
from app.core.config import settings
import logging

class ArizeConfig:
    """Configuration pour Arize AI"""
    
    def __init__(self):
        self.api_key = settings.ARIZE_API_KEY
        self.space_key = settings.ARIZE_SPACE_KEY
        self.space_name = "ai-tech-watch-agent"
        self.logger = logging.getLogger(__name__)
        
        # Initialisation du client Arize
        try:
            from arize.api import Client
            self.client = Client(
                api_key=self.api_key,
                space_key=self.space_key
            )
            self.logger.info("Client Arize initialisé avec succès")
        except ImportError:
            self.logger.warning("Le module Arize n'est pas installé. Les fonctionnalités de monitoring Arize seront désactivées.")
            self.client = None
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation du client Arize: {e}")
            self.client = None

# Instance globale de la configuration Arize
arize_config = ArizeConfig()
arize_client = arize_config.client