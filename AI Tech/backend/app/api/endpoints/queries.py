from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.schemas import QueryRequest, QueryResponse, FeedbackRequest, MetricsResponse
from app.services.query_service import query_service
from app.monitoring.metrics import metrics_service
from app.core.models import Query as QueryModel, Response as ResponseModel, Feedback as FeedbackModel

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def process_query(query_request: QueryRequest, db: Session = Depends(get_db)):
    """Traite une requête utilisateur et retourne une réponse avec les articles pertinents"""
    try:
        result = query_service.process_user_query(
            db=db,
            query_text=query_request.query_text,
            user_id=query_request.user_id,
            filters=query_request.filters,
            max_papers=query_request.max_papers
        )
        
        if result["query_id"] is None:
            raise HTTPException(status_code=500, detail="Erreur lors du traitement de la requête")
        
        return QueryResponse(
            query_id=result["query_id"],
            answer=result["answer"],
            papers_used=result["papers_used"],
            metrics=result["metrics"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement de la requête: {str(e)}")

@router.post("/feedback")
async def add_feedback(feedback_request: FeedbackRequest, db: Session = Depends(get_db)):
    """Ajoute un feedback pour une réponse"""
    try:
        from app.core.schemas import FeedbackCreate
        
        feedback_data = FeedbackCreate(
            response_id=feedback_request.response_id,
            rating=feedback_request.rating,
            comment=feedback_request.comment
        )
        
        feedback = query_service.add_feedback(db, feedback_data)
        
        return {
            "message": "Feedback ajouté avec succès",
            "feedback_id": feedback.id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ajout du feedback: {str(e)}")

@router.get("/queries/recent")
async def get_recent_queries(
    user_id: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Récupère les requêtes récentes"""
    try:
        queries = query_service.get_recent_queries(db, limit, user_id)
        
        return {
            "queries": [
                {
                    "id": query.id,
                    "query_text": query.query_text,
                    "user_id": query.user_id,
                    "timestamp": query.timestamp,
                    "created_at": query.created_at
                }
                for query in queries
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des requêtes: {str(e)}")

@router.get("/responses/{response_id}")
async def get_response(response_id: int, db: Session = Depends(get_db)):
    """Récupère une réponse spécifique par son ID"""
    try:
        response = query_service.get_response_by_id(db, response_id)
        if not response:
            raise HTTPException(status_code=404, detail="Réponse non trouvée")
        
        return {
            "id": response.id,
            "query_id": response.query_id,
            "answer_text": response.answer_text,
            "papers_used": response.papers_used,
            "metrics": response.metrics,
            "created_at": response.created_at
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la réponse: {str(e)}")

@router.get("/trends")
async def get_trending_topics(
    days: int = Query(7, ge=1, le=30, description="Nombre de jours à considérer"),
    limit: int = Query(10, ge=1, le=50, description="Nombre maximum de sujets à retourner"),
    db: Session = Depends(get_db)
):
    """Récupère les sujets tendance"""
    try:
        trending_topics = query_service.get_trending_topics(db, days, limit)
        
        return {
            "trending_topics": trending_topics,
            "period_days": days,
            "timestamp": "now"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des tendances: {str(e)}")

@router.get("/user/metrics")
async def get_user_metrics(
    user_id: str = Query(..., description="ID de l'utilisateur"),
    db: Session = Depends(get_db)
):
    """Récupère les métriques spécifiques à un utilisateur"""
    try:
        user_metrics = query_service.get_user_metrics(db, user_id)
        
        return user_metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des métriques utilisateur: {str(e)}")

@router.get("/metrics", response_model=MetricsResponse)
async def get_system_metrics(db: Session = Depends(get_db)):
    """Récupère les métriques générales du système"""
    try:
        system_metrics = metrics_service.get_general_metrics(db)
        
        # Récupère également quelques articles récents pour le retour
        recent_papers = query_service.get_recent_papers(db, limit=5)
        
        # Pour les catégories populaires, on les extrait des métriques
        top_categories = system_metrics.get("popular_categories", [])[:5]
        
        return MetricsResponse(
            total_queries=system_metrics.get("total_queries", 0),
            avg_response_time=system_metrics.get("avg_response_time", 0.0),
            avg_rating=system_metrics.get("avg_rating", 0.0),
            top_categories=top_categories,
            recent_papers=recent_papers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des métriques: {str(e)}")