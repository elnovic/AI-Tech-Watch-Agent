from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.core.models import Paper
from app.core.schemas import Paper as PaperSchema, PaperFilter
from app.services.query_service import query_service
from app.data.arxiv_ingestor import ArxivIngestor
from app.data.semantic_scholar import SemanticScholarAPI

router = APIRouter()

@router.get("/papers", response_model=List[PaperSchema])
async def get_papers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère une liste d'articles avec pagination et filtres optionnels"""
    try:
        query = db.query(Paper)
        
        if category:
            query = query.filter(Paper.categories.any(category))
        
        if source:
            query = query.filter(Paper.source == source)
        
        papers = query.offset(skip).limit(limit).all()
        return papers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des articles: {str(e)}")

@router.get("/papers/{paper_id}", response_model=PaperSchema)
async def get_paper(paper_id: int, db: Session = Depends(get_db)):
    """Récupère un article spécifique par son ID"""
    paper = db.query(Paper).filter(Paper.id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return paper

@router.post("/papers/search", response_model=List[PaperSchema])
async def search_papers(filter_params: PaperFilter, db: Session = Depends(get_db)):
    """Recherche d'articles avec des filtres avancés"""
    try:
        query = db.query(Paper)
        
        # Filtre par catégories
        if filter_params.categories:
            for category in filter_params.categories:
                query = query.filter(Paper.categories.any(category))
        
        # Filtre par date
        if filter_params.date_from:
            query = query.filter(Paper.published >= filter_params.date_from)
        
        if filter_params.date_to:
            query = query.filter(Paper.published <= filter_params.date_to)
        
        # Filtre par source
        if filter_params.source:
            query = query.filter(Paper.source == filter_params.source)
        
        # Limite le nombre de résultats
        limit = min(filter_params.max_results or 10, 100)  # Limite max de 100
        papers = query.order_by(Paper.published.desc()).limit(limit).all()
        
        return papers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche d'articles: {str(e)}")

@router.get("/papers/recent", response_model=List[PaperSchema])
async def get_recent_papers(
    limit: int = Query(10, ge=1, le=50),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Récupère les articles récents"""
    from datetime import datetime, timedelta
    
    date_limit = datetime.utcnow() - timedelta(days=days)
    recent_papers = (
        db.query(Paper)
        .filter(Paper.published >= date_limit)
        .order_by(Paper.published.desc())
        .limit(limit)
        .all()
    )
    
    return recent_papers

@router.post("/ingest")
async def ingest_papers(
    query: str = Query(..., description="Requête de recherche pour trouver des articles"),
    max_results: int = Query(10, ge=1, le=50, description="Nombre maximum d'articles à ingérer"),
    source: str = Query("both", description="Source des articles: arxiv, semantic_scholar, or both"),
    db: Session = Depends(get_db)
):
    """Ingeste de nouveaux articles depuis des sources externes"""
    try:
        total_ingested = 0
        
        if source in ["arxiv", "both"]:
            arxiv_ingestor = ArxivIngestor()
            arxiv_count = arxiv_ingestor.ingest_papers(db, query, max_results)
            total_ingested += arxiv_count
        
        if source in ["semantic_scholar", "both"]:
            semantic_scholar_api = SemanticScholarAPI()
            sem_scholar_count = semantic_scholar_api.ingest_papers(db, query, max_results)
            total_ingested += sem_scholar_count
        
        return {
            "message": f"{total_ingested} articles ont été ingérés avec succès",
            "details": {
                "total_ingested": total_ingested,
                "search_query": query,
                "max_results": max_results,
                "source": source
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ingestion des articles: {str(e)}")