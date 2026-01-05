from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.models import Query, Response, Feedback, Paper
from app.core.schemas import QueryCreate, ResponseCreate, FeedbackCreate, Paper as PaperSchema
from app.services.research_agent import research_agent
from app.monitoring.metrics import metrics_service
from app.monitoring.arize_client import log_to_arize
from app.core.config import settings
import logging
from datetime import datetime, timedelta

class QueryService:
    """Service pour gérer les requêtes et les interactions avec les utilisateurs"""
    
    def __init__(self):
        self.research_agent = research_agent
        self.metrics_service = metrics_service
        self.logger = logging.getLogger(__name__)
    
    def create_query(self, db: Session, query_data: QueryCreate) -> Query:
        """Crée une nouvelle requête dans la base de données"""
        db_query = Query(
            query_text=query_data.query_text,
            user_id=query_data.user_id,
            filters=query_data.filters
        )
        db.add(db_query)
        db.commit()
        db.refresh(db_query)
        return db_query
    
    def get_query_by_id(self, db: Session, query_id: int) -> Optional[Query]:
        """Récupère une requête par son ID"""
        return db.query(Query).filter(Query.id == query_id).first()
    
    def get_recent_queries(self, db: Session, limit: int = 10, user_id: Optional[str] = None) -> List[Query]:
        """Récupère les requêtes récentes"""
        query = db.query(Query).order_by(Query.timestamp.desc()).limit(limit)
        
        if user_id:
            query = query.filter(Query.user_id == user_id)
        
        return query.all()
    
    def process_user_query(self, db: Session, query_text: str, user_id: Optional[str] = None, 
                          filters: Optional[Dict[str, Any]] = None, max_papers: int = 10) -> Dict[str, Any]:
        """Traite une requête utilisateur complète"""
        return self.research_agent.process_query(db, query_text, user_id, filters, max_papers)
    
    def create_response(self, db: Session, response_data: ResponseCreate) -> Response:
        """Crée une réponse dans la base de données"""
        db_response = Response(
            query_id=response_data.query_id,
            answer_text=response_data.answer_text,
            papers_used=response_data.papers_used,
            metrics=response_data.metrics
        )
        db.add(db_response)
        db.commit()
        db.refresh(db_response)
        return db_response
    
    def get_response_by_id(self, db: Session, response_id: int) -> Optional[Response]:
        """Récupère une réponse par son ID"""
        return db.query(Response).filter(Response.id == response_id).first()
    
    def add_feedback(self, db: Session, feedback_data: FeedbackCreate) -> Feedback:
        """Ajoute un feedback pour une réponse"""
        # Vérifie que la réponse existe
        response = db.query(Response).filter(Response.id == feedback_data.response_id).first()
        if not response:
            raise ValueError(f"Réponse avec ID {feedback_data.response_id} non trouvée")
        
        # Crée le feedback
        db_feedback = Feedback(
            response_id=feedback_data.response_id,
            rating=feedback_data.rating,
            comment=feedback_data.comment
        )
        db.add(db_feedback)
        db.commit()
        db.refresh(db_feedback)
        
        # Log le feedback dans Arize
        log_to_arize(
            prompt="User feedback",
            response=f"Rating: {feedback_data.rating}, Comment: {feedback_data.comment}",
            model="feedback_system",
            metrics={"rating": feedback_data.rating},
            tags={"feedback_type": "user_rating"}
        )
        
        return db_feedback
    
    def get_feedback_by_response(self, db: Session, response_id: int) -> List[Feedback]:
        """Récupère tous les feedbacks pour une réponse"""
        return db.query(Feedback).filter(Feedback.response_id == response_id).all()
    
    def get_user_feedback(self, db: Session, user_id: str) -> List[Feedback]:
        """Récupère tous les feedbacks d'un utilisateur"""
        # On ne peut pas directement filtrer par user_id sur Feedback
        # On doit joindre avec Query et Response
        return (
            db.query(Feedback)
            .join(Response, Feedback.response_id == Response.id)
            .join(Query, Response.query_id == Query.id)
            .filter(Query.user_id == user_id)
            .all()
        )
    
    def get_paper_by_id(self, db: Session, paper_id: int) -> Optional[Paper]:
        """Récupère un article par son ID"""
        return db.query(Paper).filter(Paper.id == paper_id).first()
    
    def get_papers_by_ids(self, db: Session, paper_ids: List[int]) -> List[Paper]:
        """Récupère plusieurs articles par leurs IDs"""
        return db.query(Paper).filter(Paper.id.in_(paper_ids)).all()
    
    def get_recent_papers(self, db: Session, limit: int = 10) -> List[Paper]:
        """Récupère les articles récents"""
        return (
            db.query(Paper)
            .order_by(Paper.published.desc())
            .limit(limit)
            .all()
        )
    
    def get_trending_topics(self, db: Session, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère les sujets tendance"""
        return self.research_agent.get_trending_topics(db, days, limit)
    
    def get_user_metrics(self, db: Session, user_id: str) -> Dict[str, Any]:
        """Récupère les métriques spécifiques à un utilisateur"""
        try:
            # Requêtes de l'utilisateur
            user_queries = db.query(Query).filter(Query.user_id == user_id).count()
            
            # Réponses de l'utilisateur
            user_responses = (
                db.query(Response)
                .join(Query, Response.query_id == Query.id)
                .filter(Query.user_id == user_id)
                .count()
            )
            
            # Feedbacks de l'utilisateur
            user_feedbacks = self.get_user_feedback(db, user_id)
            avg_rating = 0
            if user_feedbacks:
                ratings = [f.rating for f in user_feedbacks if f.rating is not None]
                if ratings:
                    avg_rating = sum(ratings) / len(ratings)
            
            return {
                "user_id": user_id,
                "total_queries": user_queries,
                "total_responses": user_responses,
                "total_feedbacks": len(user_feedbacks),
                "avg_rating": round(avg_rating, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des métriques utilisateur: {e}")
            return {}
    
    def get_system_metrics(self, db: Session) -> Dict[str, Any]:
        """Récupère les métriques générales du système"""
        return self.metrics_service.get_general_metrics(db)

# Instance globale du service de requêtes
query_service = QueryService()