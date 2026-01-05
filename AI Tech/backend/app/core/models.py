from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
import json

class Paper(Base):
    """Modèle pour les articles de recherche"""
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    abstract = Column(Text, nullable=False)
    authors = Column(String, nullable=True)  # Store as JSON string for compatibility
    published = Column(DateTime, default=func.now(), nullable=False)
    categories = Column(String, nullable=True)  # Store as JSON string for compatibility
    source = Column(String, nullable=False)  # arXiv, Semantic Scholar, etc.
    arxiv_id = Column(String, unique=True, index=True)  # Identifiant unique
    doi = Column(String, nullable=True)  # DOI si disponible
    url = Column(String, nullable=True)  # Lien vers l'article
    pdf_url = Column(String, nullable=True)  # Lien vers le PDF
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Remove the responses relationship to avoid circular reference issues
    # responses = relationship("Response", back_populates="paper")

    @property
    def authors_list(self):
        """Helper to get authors as a list"""
        if self.authors:
            try:
                return json.loads(self.authors)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @property
    def categories_list(self):
        """Helper to get categories as a list"""
        if self.categories:
            try:
                return json.loads(self.categories)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    # For compatibility with Pydantic when using orm_mode
    def __setattr__(self, name, value):
        if name in ['authors', 'categories'] and isinstance(value, list):
            # Serialize list to JSON string when setting
            super().__setattr__(name, json.dumps(value))
        else:
            super().__setattr__(name, value)

class Query(Base):
    """Modèle pour les requêtes des utilisateurs"""
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    user_id = Column(String, index=True, nullable=True)  # ID utilisateur (facultatif pour les invités)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    filters = Column(JSON, nullable=True)  # Filtres appliqués à la recherche
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relation avec les réponses
    responses = relationship("Response", back_populates="query")

class Response(Base):
    """Modèle pour les réponses générées par l'IA"""
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    papers_used = Column(String, nullable=True)  # Store as JSON string for compatibility (IDs des articles utilisés)
    metrics = Column(JSON, nullable=True)  # Métriques d'évaluation (Arize)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    query = relationship("Query", back_populates="responses")
    # Remove the paper relationship to avoid circular reference issues
    # paper = relationship("Paper", foreign_keys="Response.id", viewonly=True)

    @property
    def papers_used_list(self):
        """Helper to get papers used as a list"""
        if self.papers_used:
            try:
                return json.loads(self.papers_used)
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    # For compatibility with Pydantic when using orm_mode
    def __setattr__(self, name, value):
        if name == 'papers_used' and isinstance(value, list):
            # Serialize list to JSON string when setting
            super().__setattr__(name, json.dumps(value))
        else:
            super().__setattr__(name, value)

class Feedback(Base):
    """Modèle pour les retours des utilisateurs"""
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("responses.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # Note de 1 à 5
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relation
    response = relationship("Response")