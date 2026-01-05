import logging
import sys
from datetime import datetime
from typing import Optional

class LoggerSetup:
    """Configuration du logger pour l'application"""
    
    def __init__(self, name: str = __name__, level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Évite les gestionnaires en double
        if not self.logger.handlers:
            # Gestionnaire pour la console
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            
            # Format des messages
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            
            # Ajoute le gestionnaire au logger
            self.logger.addHandler(console_handler)
    
    def get_logger(self):
        """Retourne l'instance du logger"""
        return self.logger

def get_logger(name: str = __name__) -> logging.Logger:
    """Fonction utilitaire pour obtenir un logger"""
    setup = LoggerSetup(name)
    return setup.get_logger()

# Logger global pour l'application
app_logger = get_logger("ai-tech-watch")

def log_info(message: str, extra: Optional[dict] = None):
    """Fonction utilitaire pour logguer un message d'information"""
    app_logger.info(message, extra=extra)

def log_error(message: str, extra: Optional[dict] = None):
    """Fonction utilitaire pour logguer un message d'erreur"""
    app_logger.error(message, extra=extra)

def log_warning(message: str, extra: Optional[dict] = None):
    """Fonction utilitaire pour logguer un message d'avertissement"""
    app_logger.warning(message, extra=extra)

def log_debug(message: str, extra: Optional[dict] = None):
    """Fonction utilitaire pour logguer un message de débogage"""
    app_logger.debug(message, extra=extra)