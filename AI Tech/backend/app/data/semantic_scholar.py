import requests
import logging
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.models import Paper
from app.core.schemas import PaperCreate

class SemanticScholarAPI:
    """Classe pour interagir avec l'API Semantic Scholar"""
    
    def __init__(self):
        self.base_url = "https://api.semanticscholar.org/v1"
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
    
    def search_papers(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Recherche des articles sur Semantic Scholar"""
        try:
            url = f"{self.base_url}/paper/search"
            params = {
                "query": query,
                "limit": limit
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            self.logger.error(f"Erreur lors de la recherche Semantic Scholar: {e}")
            return []
    
    def get_paper_details(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un article spécifique"""
        try:
            url = f"{self.base_url}/paper/{paper_id}"
            response = self.session.get(url)
            response.raise_for_status()
            
            return response.json()
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des détails de l'article {paper_id}: {e}")
            return None
    
    def paper_to_db_format(self, paper_data: Dict[str, Any]) -> Optional[PaperCreate]:
        """Convertit un résultat Semantic Scholar au format de la base de données"""
        try:
            # Extraction des auteurs
            authors = [author.get("name", "") for author in paper_data.get("authors", [])]
            
            # Extraction des catégories/fields
            categories = [field.get("name", "") for field in paper_data.get("fieldsOfStudy", []) if field]
            
            # Extraction de la date de publication
            publication_date_str = paper_data.get("publicationDate")
            published = None
            if publication_date_str:
                try:
                    published = datetime.fromisoformat(publication_date_str.replace("Z", "+00:00"))
                except ValueError:
                    # Si la date n'est pas au bon format, on essaie un autre format
                    try:
                        published = datetime.strptime(publication_date_str, "%Y-%m-%d")
                    except ValueError:
                        published = datetime.now()
            
            return PaperCreate(
                title=paper_data.get("title", ""),
                abstract=paper_data.get("abstract", ""),
                authors=authors,
                published=published,
                categories=categories,
                source="Semantic Scholar",
                arxiv_id=paper_data.get("arxivId"),
                doi=paper_data.get("doi"),
                url=paper_data.get("url"),
                pdf_url=paper_data.get("pdfUrl") if "pdfUrl" in paper_data else None
            )
        except Exception as e:
            self.logger.error(f"Erreur lors de la conversion des données: {e}")
            return None
    
    def ingest_papers(self, db: Session, query: str, limit: int = 10) -> int:
        """Ingeste des articles Semantic Scholar dans la base de données"""
        papers_data = self.search_papers(query, limit)
        ingested_count = 0
        
        for paper_data in papers_data:
            # Vérifie si l'article existe déjà (par DOI ou arXiv ID)
            doi = paper_data.get("doi")
            arxiv_id = paper_data.get("arxivId")
            
            existing_paper = None
            if doi:
                existing_paper = db.query(Paper).filter(Paper.doi == doi).first()
            elif arxiv_id:
                existing_paper = db.query(Paper).filter(Paper.arxiv_id == arxiv_id).first()
            
            if not existing_paper:
                # Convertit et sauvegarde le nouvel article
                paper_db_format = self.paper_to_db_format(paper_data)
                
                if paper_db_format:
                    db_paper = Paper(
                        title=paper_db_format.title,
                        abstract=paper_db_format.abstract,
                        authors=json.dumps(paper_db_format.authors),  # Serialize to JSON string
                        published=paper_db_format.published,
                        categories=json.dumps(paper_db_format.categories),  # Serialize to JSON string
                        source=paper_db_format.source,
                        arxiv_id=paper_db_format.arxiv_id,
                        doi=paper_db_format.doi,
                        url=paper_db_format.url,
                        pdf_url=paper_db_format.pdf_url
                    )
                    
                    db.add(db_paper)
                    try:
                        db.commit()
                        ingested_count += 1
                    except Exception as e:
                        db.rollback()
                        self.logger.error(f"Erreur lors de l'ajout de l'article: {e}")
            else:
                self.logger.info(f"L'article {paper_data.get('title', 'Unknown')} existe déjà dans la base")
        
        return ingested_count

# Fonction utilitaire pour l'ingestion
def ingest_semantic_scholar_data(query: str = "machine learning", limit: int = 10):
    """Fonction utilitaire pour ingérer des données Semantic Scholar"""
    api = SemanticScholarAPI()
    
    # On utilisera une session de base de données externe dans la vraie implémentation
    # Pour l'instant, on retourne simplement les données
    papers = api.search_papers(query, limit)
    print(f"{len(papers)} articles Semantic Scholar trouvés")
    return papers