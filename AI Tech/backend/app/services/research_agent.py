from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.models import Paper, Query, Response
from app.core.schemas import Paper as PaperSchema
from app.data.arxiv_ingestor import ArxivIngestor
from app.data.semantic_scholar import SemanticScholarAPI
from app.llm.summarizer import summarizer
from app.monitoring.arize_client import log_to_arize
from app.core.config import settings
import logging
import json
from datetime import datetime, timedelta

class ResearchAgent:
    """Agent de recherche IA pour la veille technologique"""
    
    def __init__(self):
        self.arxiv_ingestor = ArxivIngestor()
        self.semantic_scholar_api = SemanticScholarAPI()
        self.summarizer = summarizer
        self.logger = logging.getLogger(__name__)
    
    def search_papers(self, db: Session, query: str, max_results: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Paper]:
        """Recherche des articles pertinents dans la base de données"""
        try:
            # Construction de la requête de recherche
            db_query = db.query(Paper)
            
            # Appliquer les filtres si fournis
            if filters:
                if "categories" in filters and filters["categories"]:
                    # Filtrer par catégories (recherche dans la chaîne JSON)
                    categories = filters["categories"]
                    # Pour la recherche dans le champ JSON, on utilise LIKE
                    for cat in categories:
                        db_query = db_query.filter(Paper.categories.like(f'%{cat}%'))
                
                if "date_from" in filters:
                    date_from = filters["date_from"]
                    if isinstance(date_from, str):
                        date_from = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
                    db_query = db_query.filter(Paper.published >= date_from)
                
                if "date_to" in filters:
                    date_to = filters["date_to"]
                    if isinstance(date_to, str):
                        date_to = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
                    db_query = db_query.filter(Paper.published <= date_to)
                
                if "source" in filters:
                    db_query = db_query.filter(Paper.source == filters["source"])
            
            # Trier par date de publication (les plus récents en premier)
            db_query = db_query.order_by(Paper.published.desc())
            
            # Limiter le nombre de résultats
            papers = db_query.limit(max_results).all()
            
            return papers
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche d'articles: {e}")
            return []
    
    def ingest_new_papers(self, db: Session, query: str, max_results: int = 10) -> int:
        """Ingeste de nouveaux articles depuis les sources externes"""
        total_ingested = 0
        
        # Ingestion depuis arXiv
        try:
            arxiv_count = self.arxiv_ingestor.ingest_papers(db, query, max_results)
            total_ingested += arxiv_count
            self.logger.info(f"{arxiv_count} articles arXiv ingérés")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ingestion arXiv: {e}")
        
        # Ingestion depuis Semantic Scholar
        try:
            sem_scholar_count = self.semantic_scholar_api.ingest_papers(db, query, max_results)
            total_ingested += sem_scholar_count
            self.logger.info(f"{sem_scholar_count} articles Semantic Scholar ingérés")
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ingestion Semantic Scholar: {e}")
        
        return total_ingested
    
    def process_query(self, db: Session, query_text: str, user_id: Optional[str] = None, 
                     filters: Optional[Dict[str, Any]] = None, max_papers: int = 10) -> Dict[str, Any]:
        """Traite une requête utilisateur et retourne une réponse"""
        try:
            # Enregistre la requête dans la base
            db_query = Query(
                query_text=query_text,
                user_id=user_id,
                filters=filters or {}
            )
            db.add(db_query)
            db.commit()
            db.refresh(db_query)
            
            # Recherche des articles pertinents
            papers = self.search_papers(db, query_text, max_papers, filters)
            
            if not papers:
                # Si aucun article trouvé dans la base, on tente d'ingérer de nouveaux articles
                self.logger.info(f"Aucun article trouvé pour la requête '{query_text}', tentative d'ingestion...")
                self.ingest_new_papers(db, query_text, max_papers)
                
                # Nouvelle recherche après ingestion
                papers = self.search_papers(db, query_text, max_papers, filters)
            
            # Génère une réponse en utilisant les articles trouvés
            if papers:
                answer = self.summarizer.answer_with_context(query_text, papers)
                
                # Crée une réponse dans la base
                response = Response(
                    query_id=db_query.id,
                    answer_text=answer,
                    papers_used=json.dumps([paper.id for paper in papers]),  # Convert to JSON string
                    metrics={"papers_used": len(papers)}
                )
                db.add(response)
                db.commit()
                
                # Log dans Arize
                log_to_arize(
                    prompt=query_text,
                    response=answer,
                    model=settings.OPENAI_MODEL,
                    metrics={
                        "papers_used": len(papers),
                        "query_length": len(query_text),
                        "response_length": len(answer)
                    },
                    tags={"query_type": "research_query", "user_id": user_id or "anonymous"}
                )
                
                return {
                    "query_id": db_query.id,
                    "answer": answer,
                    "papers_used": [PaperSchema.from_orm(paper) for paper in papers],
                    "metrics": {"papers_found": len(papers)}
                }
            else:
                # Aucun article trouvé même après ingestion
                answer = "Aucun article de recherche pertinent trouvé pour votre requête. Veuillez reformuler ou essayer des termes de recherche différents."
                
                response = Response(
                    query_id=db_query.id,
                    answer_text=answer,
                    papers_used=json.dumps([]),  # Convert to JSON string
                    metrics={"papers_found": 0}
                )
                db.add(response)
                db.commit()
                
                # Log dans Arize
                log_to_arize(
                    prompt=query_text,
                    response=answer,
                    model=settings.OPENAI_MODEL,
                    metrics={"papers_found": 0},
                    tags={"query_type": "no_results", "user_id": user_id or "anonymous"}
                )
                
                return {
                    "query_id": db_query.id,
                    "answer": answer,
                    "papers_used": [],
                    "metrics": {"papers_found": 0}
                }
                
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de la requête: {e}")
            return {
                "query_id": None,
                "answer": "Erreur lors du traitement de votre requête. Veuillez réessayer plus tard.",
                "papers_used": [],
                "metrics": {"error": str(e)}
            }
    
    def get_trending_topics(self, db: Session, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """Récupère les sujets tendance basés sur les requêtes récentes"""
        try:
            # On récupère les requêtes des derniers jours
            start_date = datetime.utcnow() - timedelta(days=days)
            recent_queries = db.query(Query).filter(Query.timestamp >= start_date).all()
            
            # Extraction des mots clés des requêtes
            keywords_count = {}
            for query in recent_queries:
                # Simple extraction de mots clés (dans une vraie implémentation, on utiliserait NLP)
                words = query.query_text.lower().split()
                for word in words:
                    # Filtre les mots courts et les mots courants
                    if len(word) > 3 and word not in ["the", "and", "for", "with", "from", "that", "have", "this", "will", "from", "with"]:
                        keywords_count[word] = keywords_count.get(word, 0) + 1
            
            # Trie les mots clés par fréquence
            sorted_keywords = sorted(
                keywords_count.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Retourne les mots clés les plus fréquents
            trending_topics = []
            for keyword, count in sorted_keywords[:limit]:
                trending_topics.append({
                    "topic": keyword,
                    "count": count,
                    "trend": "up"  # Pourrait être calculé en comparant avec la période précédente
                })
            
            return trending_topics
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des sujets tendance: {e}")
            return []

# Instance globale de l'agent de recherche
research_agent = ResearchAgent()