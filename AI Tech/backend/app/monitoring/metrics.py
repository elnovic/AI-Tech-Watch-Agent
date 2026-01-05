from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.core.models import Query, Response, Feedback, Paper
from app.core.config import settings
from datetime import datetime, timedelta
import logging

class MetricsService:
    """Service pour collecter et analyser les métriques"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_general_metrics(self, db: Session) -> Dict[str, Any]:
        """Récupère les métriques générales de l'application"""
        try:
            # Nombre total de requêtes
            total_queries = db.query(Query).count()
            
            # Nombre total de réponses
            total_responses = db.query(Response).count()
            
            # Nombre total de feedbacks
            total_feedbacks = db.query(Feedback).count()
            
            # Nombre total d'articles
            total_papers = db.query(Paper).count()
            
            # Moyenne des notes de feedback
            avg_rating = 0
            if total_feedbacks > 0:
                feedbacks = db.query(Feedback.rating).all()
                ratings = [f.rating for f in feedbacks if f.rating is not None]
                if ratings:
                    avg_rating = sum(ratings) / len(ratings)
            
            # Requêtes des dernières 24h
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_queries = db.query(Query).filter(Query.timestamp >= yesterday).count()
            
            # Catégories les plus populaires
            popular_categories = self.get_popular_categories(db)
            
            return {
                "total_queries": total_queries,
                "total_responses": total_responses,
                "total_feedbacks": total_feedbacks,
                "total_papers": total_papers,
                "avg_rating": round(avg_rating, 2),
                "recent_queries_24h": recent_queries,
                "popular_categories": popular_categories[:10],  # Les 10 premières
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des métriques générales: {e}")
            return {}
    
    def get_popular_categories(self, db: Session) -> List[Dict[str, Any]]:
        """Récupère les catégories les plus populaires"""
        try:
            # Pour simplifier, on récupère les catégories des articles
            # En réalité, cela pourrait être basé sur les requêtes ou les réponses
            from sqlalchemy import func
            
            # On va compter les occurrences des catégories dans les articles
            # Pour cela, on doit d'abord récupérer tous les articles et leurs catégories
            papers = db.query(Paper).all()
            
            category_count = {}
            for paper in papers:
                if paper.categories:
                    for category in paper.categories:
                        category_count[category] = category_count.get(category, 0) + 1
            
            # Trie les catégories par fréquence
            sorted_categories = sorted(
                category_count.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            return [{"category": cat, "count": count} for cat, count in sorted_categories]
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des catégories populaires: {e}")
            return []
    
    def get_response_time_metrics(self, db: Session) -> Dict[str, Any]:
        """Récupère les métriques de temps de réponse"""
        try:
            # Pour l'instant, on ne stocke pas le temps de réponse dans la base
            # On pourrait ajouter un champ dans la table Response pour cela
            # Pour l'instant, on retourne des valeurs factices
            return {
                "avg_response_time": 2.5,  # secondes
                "min_response_time": 0.5,
                "max_response_time": 10.0,
                "p95_response_time": 5.0,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des métriques de temps de réponse: {e}")
            return {}
    
    def get_user_engagement_metrics(self, db: Session) -> Dict[str, Any]:
        """Récupère les métriques d'engagement des utilisateurs"""
        try:
            # Utilisateurs uniques
            unique_users = db.query(Query.user_id).distinct().filter(Query.user_id.isnot(None)).count()
            
            # Requêtes par utilisateur (moyenne)
            total_queries = db.query(Query).count()
            avg_queries_per_user = 0
            if unique_users > 0:
                avg_queries_per_user = total_queries / unique_users
            
            # Taux de feedback (réponses avec feedback)
            total_responses_with_feedback = db.query(Response).join(Feedback).count()
            total_responses = db.query(Response).count()
            
            feedback_rate = 0
            if total_responses > 0:
                feedback_rate = (total_responses_with_feedback / total_responses) * 100
            
            return {
                "unique_users": unique_users,
                "avg_queries_per_user": round(avg_queries_per_user, 2),
                "feedback_rate_percent": round(feedback_rate, 2),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des métriques d'engagement: {e}")
            return {}
    
    def get_content_metrics(self, db: Session) -> Dict[str, Any]:
        """Récupère les métriques liées au contenu"""
        try:
            # Articles par source
            papers_by_source = db.query(
                Paper.source, 
                func.count(Paper.id)
            ).group_by(Paper.source).all()
            
            # Articles par mois
            from sqlalchemy import extract
            papers_by_month = db.query(
                extract('year', Paper.published).label('year'),
                extract('month', Paper.published).label('month'),
                func.count(Paper.id)
            ).group_by(
                extract('year', Paper.published),
                extract('month', Paper.published)
            ).order_by('year', 'month').all()
            
            return {
                "papers_by_source": [{"source": source, "count": count} for source, count in papers_by_source],
                "papers_by_month": [{"year": int(year), "month": int(month), "count": count} for year, month, count in papers_by_month],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des métriques de contenu: {e}")
            return {}

# Instance globale du service de métriques
metrics_service = MetricsService()