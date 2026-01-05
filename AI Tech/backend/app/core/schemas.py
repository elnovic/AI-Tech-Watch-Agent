from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import json

# Modèles Pydantic pour la validation des données

class PaperBase(BaseModel):
    title: str
    abstract: str
    authors: Optional[List[str]] = []
    published: Optional[datetime] = None
    categories: Optional[List[str]] = []
    source: str
    arxiv_id: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None

class PaperCreate(PaperBase):
    pass

class Paper(PaperBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
    
    @validator('authors', pre=True)
    def validate_authors(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v if v is not None else []
    
    @validator('categories', pre=True)
    def validate_categories(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v if v is not None else []

class QueryBase(BaseModel):
    query_text: str
    user_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = {}

class QueryCreate(QueryBase):
    pass

class Query(QueryBase):
    id: int
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ResponseBase(BaseModel):
    query_id: int
    answer_text: str
    papers_used: Optional[List[int]] = []
    metrics: Optional[Dict[str, Any]] = {}

class ResponseCreate(ResponseBase):
    pass

class Response(ResponseBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
    
    @validator('papers_used', pre=True)
    def validate_papers_used(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v if v is not None else []

class FeedbackBase(BaseModel):
    response_id: int
    rating: int  # 1-5
    comment: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Modèles pour les requêtes API

class QueryRequest(BaseModel):
    query_text: str
    user_id: Optional[str] = None
    filters: Optional[Dict[str, Any]] = {}
    max_papers: Optional[int] = 10

class FeedbackRequest(BaseModel):
    response_id: int
    rating: int  # 1-5
    comment: Optional[str] = None

class QueryResponse(BaseModel):
    query_id: int
    answer: str
    papers_used: List[Paper]
    metrics: Dict[str, Any]

class PaperFilter(BaseModel):
    categories: Optional[List[str]] = []
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    source: Optional[str] = None
    max_results: Optional[int] = 10

class MetricsResponse(BaseModel):
    total_queries: int
    avg_response_time: float
    avg_rating: float
    top_categories: List[Dict[str, Any]]
    recent_papers: List[Paper]