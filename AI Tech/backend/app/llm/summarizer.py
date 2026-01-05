from typing import List, Dict, Any
from app.llm.openai_client import openai_client
from app.core.models import Paper
from app.core.schemas import Paper as PaperSchema

class Summarizer:
    """Classe pour résumer des articles et générer des insights"""
    
    def __init__(self):
        self.client = openai_client
    
    def summarize_paper(self, paper: Paper) -> str:
        """Résume un article de recherche"""
        text_to_summarize = f"{paper.title}\n\n{paper.abstract}"
        return self.client.generate_summary(text_to_summarize)
    
    def summarize_papers(self, papers: List[Paper]) -> str:
        """Résume plusieurs articles de recherche"""
        if not papers:
            return "Aucun article à résumer."
        
        combined_text = ""
        for paper in papers:
            combined_text += f"Titre: {paper.title}\n"
            combined_text += f"Résumé: {paper.abstract}\n\n"
        
        # Limite la longueur pour éviter les problèmes de token
        if len(combined_text) > 3000:
            combined_text = combined_text[:3000] + "... (texte tronqué)"
        
        return self.client.generate_summary(combined_text, max_tokens=500)
    
    def generate_insights(self, papers: List[Paper]) -> str:
        """Génère des insights à partir de plusieurs articles"""
        if not papers:
            return "Aucun article pour générer des insights."
        
        # Convertit les articles en dictionnaires
        papers_dicts = []
        for paper in papers:
            papers_dicts.append({
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": paper.authors,
                "categories": paper.categories,
                "published": paper.published.isoformat() if paper.published else None
            })
        
        return self.client.extract_key_insights(papers_dicts)
    
    def answer_with_context(self, query: str, papers: List[Paper]) -> str:
        """Répond à une question en utilisant le contexte des articles"""
        if not papers:
            return "Aucun article de recherche disponible pour répondre à cette question."
        
        # Convertit les articles en dictionnaires
        papers_dicts = []
        for paper in papers:
            papers_dicts.append({
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": paper.authors,
                "categories": paper.categories
            })
        
        # Crée un contexte à partir des articles
        context = f"Voici {len(papers)} articles de recherche pertinents pour votre question."
        
        return self.client.answer_query(query, context, papers_dicts)

# Instance globale du summarizer
summarizer = Summarizer()