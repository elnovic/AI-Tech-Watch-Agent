import arxiv
import logging
import json
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.models import Paper
from app.core.schemas import PaperCreate
from app.core.database import SessionLocal

class ArxivIngestor:
    """Classe pour ingérer des articles depuis arXiv"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def search_papers(self, query: str, max_results: int = 10) -> List[arxiv.Result]:
        """Recherche des articles sur arXiv"""
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            return list(search.results())
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche arXiv: {e}")
            return []
    
    def paper_to_db_format(self, arxiv_paper: arxiv.Result) -> PaperCreate:
        """Convertit un résultat arXiv au format de la base de données"""
        return PaperCreate(
            title=arxiv_paper.title,
            abstract=arxiv_paper.summary,
            authors=[author.name for author in arxiv_paper.authors],  # Will be serialized to JSON in the model
            published=arxiv_paper.published,
            categories=[c.term for c in arxiv_paper.categories],  # Will be serialized to JSON in the model
            source="arXiv",
            arxiv_id=arxiv_paper.entry_id.split("/")[-1] if arxiv_paper.entry_id else None,
            doi=arxiv_paper.doi,
            url=arxiv_paper.entry_id,
            pdf_url=arxiv_paper.pdf_url
        )
    
    def ingest_papers(self, db: Session, query: str, max_results: int = 10) -> int:
        """Ingeste des articles arXiv dans la base de données"""
        arxiv_papers = self.search_papers(query, max_results)
        ingested_count = 0
        
        for arxiv_paper in arxiv_papers:
            # Vérifie si l'article existe déjà
            existing_paper = db.query(Paper).filter(Paper.arxiv_id == arxiv_paper.entry_id.split("/")[-1]).first()
            
            if not existing_paper:
                # Convertit et sauvegarde le nouvel article
                paper_data = self.paper_to_db_format(arxiv_paper)
                
                # Crée l'objet Paper à partir des données, en sérialisant les listes en JSON
                db_paper = Paper(
                    title=paper_data.title,
                    abstract=paper_data.abstract,
                    authors=json.dumps(paper_data.authors),  # Serialize to JSON string
                    published=paper_data.published,
                    categories=json.dumps(paper_data.categories),  # Serialize to JSON string
                    source=paper_data.source,
                    arxiv_id=paper_data.arxiv_id,
                    doi=paper_data.doi,
                    url=paper_data.url,
                    pdf_url=paper_data.pdf_url
                )
                
                db.add(db_paper)
                try:
                    db.commit()
                    ingested_count += 1
                except Exception as e:
                    db.rollback()
                    self.logger.error(f"Erreur lors de l'ajout de l'article: {e}")
            else:
                self.logger.info(f"L'article {arxiv_paper.title} existe déjà dans la base")
        
        return ingested_count
    
    def ingest_recent_papers(self, db: Session, days: int = 7, max_results: int = 50) -> int:
        """Ingeste les articles récents publiés dans les derniers jours"""
        # Calcul de la date de début
        start_date = datetime.now() - timedelta(days=days)
        date_query = f"submittedDate:[{start_date.strftime('%Y%m%d')} TO {datetime.now().strftime('%Y%m%d')}]"
        
        return self.ingest_papers(db, date_query, max_results)

# Fonction utilitaire pour l'ingestion
def ingest_arxiv_data(query: str = "machine learning", max_results: int = 10):
    """Fonction utilitaire pour ingérer des données arXiv"""
    ingestor = ArxivIngestor()
    
    db = SessionLocal()
    try:
        count = ingestor.ingest_papers(db, query, max_results)
        print(f"{count} articles arXiv ajoutés à la base de données")
        return count
    finally:
        db.close()