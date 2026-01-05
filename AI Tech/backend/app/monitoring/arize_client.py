from typing import Dict, Any, Optional
from app.monitoring.arize_config import arize_client
from app.core.config import settings
import logging
import time
from datetime import datetime

class ArizeMonitor:
    """Classe pour logguer les interactions LLM dans Arize"""
    
    def __init__(self):
        self.client = arize_client
        self.logger = logging.getLogger(__name__)
    
    def log_to_arize(
        self,
        prompt: str,
        response: str,
        model: str,
        metrics: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
        prediction_id: Optional[str] = None
    ) -> bool:
        """Log les interactions LLM dans Arize"""
        if not self.client:
            self.logger.warning("Client Arize non disponible, impossible de logguer")
            return False
        
        try:
            # Génère un ID de prédiction si non fourni
            if not prediction_id:
                prediction_id = f"prediction_{int(time.time())}_{hash(prompt) % 10000}"
            
            # Prépare les features pour Arize
            features = {
                "model": model,
                "prompt_length": len(prompt),
                "response_length": len(response),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Ajoute les métriques si fournies
            if metrics:
                features.update(metrics)
            
            # Ajoute les tags si fournis
            if tags:
                features.update(tags)
            
            # Envoie les données à Arize
            response = self.client.log(
                prediction_id=prediction_id,
                features=features,
                prompt=prompt,
                response=response
            )
            
            if response.status_code == 200:
                self.logger.info(f"Log Arize réussi pour prediction_id: {prediction_id}")
                return True
            else:
                self.logger.error(f"Échec du log Arize: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors du log Arize: {e}")
            return False
    
    def log_evaluation(
        self,
        prediction_id: str,
        actual_label: str,
        model_version: str,
        tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """Log une évaluation pour le monitoring de la qualité"""
        if not self.client:
            self.logger.warning("Client Arize non disponible, impossible de logguer l'évaluation")
            return False
        
        try:
            features = {
                "model_version": model_version,
                "evaluation_timestamp": datetime.utcnow().isoformat()
            }
            
            if tags:
                features.update(tags)
            
            response = self.client.log(
                prediction_id=prediction_id,
                features=features,
                actual_label=actual_label
            )
            
            if response.status_code == 200:
                self.logger.info(f"Évaluation Arize logguée pour prediction_id: {prediction_id}")
                return True
            else:
                self.logger.error(f"Échec du log d'évaluation Arize: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors du log d'évaluation Arize: {e}")
            return False
    
    def log_feedback(
        self,
        response_id: str,
        rating: int,
        comment: Optional[str] = None
    ) -> bool:
        """Log le feedback utilisateur pour le monitoring de la qualité"""
        if not self.client:
            self.logger.warning("Client Arize non disponible, impossible de logguer le feedback")
            return False
        
        try:
            features = {
                "rating": rating,
                "feedback_timestamp": datetime.utcnow().isoformat()
            }
            
            if comment:
                features["comment"] = comment
            
            response = self.client.log(
                prediction_id=f"feedback_{response_id}",
                features=features,
                actual_label=str(rating)
            )
            
            if response.status_code == 200:
                self.logger.info(f"Feedback Arize loggué pour response_id: {response_id}")
                return True
            else:
                self.logger.error(f"Échec du log de feedback Arize: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Erreur lors du log de feedback Arize: {e}")
            return False

# Instance globale du moniteur Arize
arize_monitor = ArizeMonitor()

# Fonction utilitaire pour logguer dans Arize
def log_to_arize(
    prompt: str,
    response: str,
    model: str,
    metrics: Optional[Dict[str, Any]] = None,
    tags: Optional[Dict[str, str]] = None,
    prediction_id: Optional[str] = None
) -> bool:
    """Fonction utilitaire pour logguer dans Arize"""
    return arize_monitor.log_to_arize(prompt, response, model, metrics, tags, prediction_id)