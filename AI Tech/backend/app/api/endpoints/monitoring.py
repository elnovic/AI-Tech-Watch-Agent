from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.monitoring.metrics import metrics_service
from app.core.schemas import MetricsResponse
from typing import Dict, Any

router = APIRouter()

@router.get("/monitoring/health")
async def health_check():
    """Vérification de l'état de santé du service de monitoring"""
    return {"status": "healthy", "service": "monitoring"}

@router.get("/monitoring/metrics", response_model=MetricsResponse)
async def get_monitoring_metrics(db: Session = Depends(get_db)):
    """Récupère les métriques de performance et d'utilisation"""
    try:
        # Récupère les métriques générales
        general_metrics = metrics_service.get_general_metrics(db)
        
        # Récupère les métriques de temps de réponse
        response_time_metrics = metrics_service.get_response_time_metrics(db)
        
        # Récupère les métriques d'engagement
        engagement_metrics = metrics_service.get_user_engagement_metrics(db)
        
        # Récupère les métriques de contenu
        content_metrics = metrics_service.get_content_metrics(db)
        
        # Combine toutes les métriques
        all_metrics = {**general_metrics, **response_time_metrics, **engagement_metrics, **content_metrics}
        
        # Pour correspondre au modèle MetricsResponse, on extrait les champs nécessaires
        recent_papers = db.query(db.query(db).from_statement(db.query(db).select_from(db).limit(5)).subquery()).all()
        
        # Récupère réellement les 5 derniers articles
        from app.core.models import Paper
        recent_papers = db.query(Paper).order_by(Paper.published.desc()).limit(5).all()
        
        # Pour les catégories populaires, on extrait les 5 premières
        top_categories = general_metrics.get("popular_categories", [])[:5]
        
        return MetricsResponse(
            total_queries=general_metrics.get("total_queries", 0),
            avg_response_time=response_time_metrics.get("avg_response_time", 0.0),
            avg_rating=general_metrics.get("avg_rating", 0.0),
            top_categories=top_categories,
            recent_papers=recent_papers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des métriques: {str(e)}")

@router.get("/monitoring/llm-performance")
async def get_llm_performance_metrics(db: Session = Depends(get_db)):
    """Récupère les métriques spécifiques aux performances LLM"""
    try:
        # Pour l'instant, on retourne des métriques basiques
        # Dans une implémentation réelle, on récupérerait des données spécifiques aux appels LLM
        return {
            "llm_calls_count": 0,  # Ce compteur devrait être mis à jour à chaque appel LLM
            "avg_token_usage": 0,
            "avg_response_time": 0,
            "success_rate": 100,
            "error_rate": 0,
            "timestamp": "now"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des métriques LLM: {str(e)}")

@router.get("/monitoring/arize-status")
async def get_arize_status():
    """Vérifie l'état du service Arize"""
    try:
        from app.monitoring.arize_config import arize_client
        
        if arize_client:
            return {
                "status": "connected",
                "message": "Le service Arize est correctement configuré et connecté"
            }
        else:
            return {
                "status": "disconnected",
                "message": "Le service Arize n'est pas configuré ou les clés API sont manquantes"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la vérification du statut Arize: {str(e)}")

@router.get("/monitoring/system-stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """Récupère les statistiques système générales"""
    try:
        # Récupère les métriques générales
        general_metrics = metrics_service.get_general_metrics(db)
        
        # Ajoute des statistiques système supplémentaires
        return {
            "system": {
                "database_status": "connected",
                "arize_status": "connected" if hasattr(metrics_service, 'arize_client') else "not_configured",
                "llm_status": "configured"
            },
            "statistics": {
                "total_papers": general_metrics.get("total_papers", 0),
                "total_queries": general_metrics.get("total_queries", 0),
                "total_responses": general_metrics.get("total_responses", 0),
                "total_feedbacks": general_metrics.get("total_feedbacks", 0),
                "avg_rating": general_metrics.get("avg_rating", 0.0)
            },
            "trends": {
                "recent_queries_24h": general_metrics.get("recent_queries_24h", 0),
                "popular_categories": general_metrics.get("popular_categories", [])[:5]
            },
            "timestamp": general_metrics.get("timestamp", "now")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des statistiques système: {str(e)}")