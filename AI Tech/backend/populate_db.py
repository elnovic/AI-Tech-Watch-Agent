import os
import sys
import json
from datetime import datetime
from sqlalchemy.orm import Session

# Add the app directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.core.models import Paper
from app.data.arxiv_ingestor import ingest_arxiv_data
from app.data.semantic_scholar import ingest_semantic_scholar_data

def populate_database():
    """Fonction pour peupler la base de données avec des données initiales"""
    db = SessionLocal()
    
    try:
        print("Début de l'ingestion des données...")
        
        # Ingestion de quelques articles arXiv sur l'IA
        print("Ingestion des articles arXiv...")
        arxiv_count = ingest_arxiv_data("artificial intelligence", max_results=5)
        print(f"{arxiv_count} articles arXiv ajoutés")
        
        # Ingestion de quelques articles Semantic Scholar sur l'IA
        print("Ingestion des articles Semantic Scholar...")
        from app.data.semantic_scholar import SemanticScholarAPI
        api = SemanticScholarAPI()
        sem_count = api.ingest_papers(db, "artificial intelligence", limit=5)
        print(f"{sem_count} articles Semantic Scholar ajoutés")
        
        # Ajout de quelques articles de démonstration si aucune donnée n'a été ajoutée
        if arxiv_count == 0 and sem_count == 0:
            print("Aucun article trouvé en ligne, ajout d'articles de démonstration...")
            demo_papers = [
                {
                    "title": "Transformer Architecture for Modern AI",
                    "abstract": "This paper explores the transformer architecture that has revolutionized modern AI applications...",
                    "authors": ["John Doe", "Jane Smith"],
                    "published": datetime.now(),
                    "categories": ["Machine Learning", "Natural Language Processing"],
                    "source": "Demo",
                    "arxiv_id": "demo001",
                    "doi": "10.1234/demo001",
                    "url": "https://example.com/demo001",
                    "pdf_url": "https://example.com/demo001.pdf"
                },
                {
                    "title": "Advances in Deep Learning 2024",
                    "abstract": "Recent advances in deep learning have shown remarkable results in various domains...",
                    "authors": ["Alice Johnson", "Bob Williams"],
                    "published": datetime.now(),
                    "categories": ["Deep Learning", "Computer Vision"],
                    "source": "Demo",
                    "arxiv_id": "demo002",
                    "doi": "10.1234/demo002",
                    "url": "https://example.com/demo002",
                    "pdf_url": "https://example.com/demo002.pdf"
                },
                {
                    "title": "Large Language Models: Capabilities and Limitations",
                    "abstract": "This survey paper examines the capabilities and limitations of large language models...",
                    "authors": ["Carol Brown", "David Davis"],
                    "published": datetime.now(),
                    "categories": ["Natural Language Processing", "AI Ethics"],
                    "source": "Demo",
                    "arxiv_id": "demo003",
                    "doi": "10.1234/demo003",
                    "url": "https://example.com/demo003",
                    "pdf_url": "https://example.com/demo003.pdf"
                }
            ]
            
            for paper_data in demo_papers:
                # Vérifier si l'article existe déjà
                existing = db.query(Paper).filter(Paper.arxiv_id == paper_data["arxiv_id"]).first()
                if not existing:
                    demo_paper = Paper(
                        title=paper_data["title"],
                        abstract=paper_data["abstract"],
                        authors=json.dumps(paper_data["authors"]),  # Serialize to JSON string
                        published=paper_data["published"],
                        categories=json.dumps(paper_data["categories"]),  # Serialize to JSON string
                        source=paper_data["source"],
                        arxiv_id=paper_data["arxiv_id"],
                        doi=paper_data["doi"],
                        url=paper_data["url"],
                        pdf_url=paper_data["pdf_url"]
                    )
                    db.add(demo_paper)
            
            db.commit()
            print(f"{len(demo_papers)} articles de démonstration ajoutés")
        
        # Afficher le nombre total d'articles dans la base
        total_papers = db.query(Paper).count()
        print(f"Total des articles dans la base: {total_papers}")
        
    except Exception as e:
        print(f"Erreur lors de l'ingestion des données: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_database()