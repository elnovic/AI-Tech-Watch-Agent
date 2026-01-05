import openai
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.monitoring.arize_client import log_to_arize

class OpenAIClient:
    """Client pour interagir avec l'API OpenAI"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.logger = logging.getLogger(__name__)
    
    def generate_summary(self, text: str, max_tokens: int = 300) -> str:
        """Génère un résumé d'un texte"""
        try:
            prompt = f"Résume en français de manière claire et concise le contenu suivant : {text[:3000]}"  # Limite la longueur
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Tu es un expert en résumé académique. Résume en français de manière claire, concise et professionnelle."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            summary = response.choices[0].message['content'].strip()
            
            # Log dans Arize
            log_to_arize(
                prompt=prompt,
                response=summary,
                model=self.model,
                metrics={"tokens_used": response.usage.total_tokens}
            )
            
            return summary
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du résumé: {e}")
            return "Erreur lors de la génération du résumé"
    
    def answer_query(self, query: str, context: str, papers: List[Dict[str, Any]]) -> str:
        """Répond à une requête utilisateur en utilisant le contexte et les articles fournis"""
        try:
            # Crée un contexte détaillé à partir des articles
            context_details = []
            for i, paper in enumerate(papers):
                context_details.append(
                    f"Article {i+1}: {paper.get('title', 'Sans titre')}\n"
                    f"Résumé: {paper.get('abstract', '')[:500]}..."  # Limite la longueur
                )
            
            full_context = "\n\n".join(context_details)
            full_context += f"\n\nQuestion de l'utilisateur: {query}"
            
            prompt = f"""
            En tant qu'expert en veille technologique, réponds de manière détaillée, précise et professionnelle à la question suivante en t'appuyant sur les articles de recherche fournis.
            
            Contexte:
            {full_context}
            
            Réponds en français, avec des citations des articles pertinents, et structure ta réponse de manière claire.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es un agent de veille technologique expert qui répond en français à des questions sur des articles de recherche. Structure ta réponse clairement, cite les articles pertinents et sois précis et professionnel."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.4
            )
            
            answer = response.choices[0].message['content'].strip()
            
            # Log dans Arize
            metrics = {
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "context_length": len(full_context),
                "query_length": len(query),
                "response_length": len(answer)
            }
            
            log_to_arize(
                prompt=prompt,
                response=answer,
                model=self.model,
                metrics=metrics,
                tags={"query_type": "research_answer"}
            )
            
            return answer
        except Exception as e:
            self.logger.error(f"Erreur lors de la réponse à la requête: {e}")
            return "Erreur lors de la génération de la réponse"
    
    def extract_key_insights(self, papers: List[Dict[str, Any]]) -> str:
        """Extrait les points clés et les tendances des articles fournis"""
        try:
            papers_text = []
            for paper in papers:
                papers_text.append(
                    f"Titre: {paper.get('title', 'Sans titre')}\n"
                    f"Résumé: {paper.get('abstract', '')}"
                )
            
            full_text = "\n\n".join(papers_text)
            
            prompt = f"""
            Analyse les articles de recherche suivants et extrait les points clés, les tendances émergentes, 
            les innovations majeures et les directions futures de recherche.
            
            Articles:
            {full_text[:4000]}  # Limite la longueur
            
            Réponds en français de manière structurée avec des sections claires.
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "Tu es un analyste de veille technologique expert. Fournis une analyse structurée en français des tendances et points clés des articles de recherche."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            insights = response.choices[0].message['content'].strip()
            
            # Log dans Arize
            metrics = {
                "tokens_used": response.usage.total_tokens,
                "papers_analyzed": len(papers)
            }
            
            log_to_arize(
                prompt=prompt,
                response=insights,
                model=self.model,
                metrics=metrics,
                tags={"analysis_type": "key_insights"}
            )
            
            return insights
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des points clés: {e}")
            return "Erreur lors de l'extraction des points clés"

# Instance globale du client OpenAI
openai_client = OpenAIClient()