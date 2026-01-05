import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

# Configuration de la page
st.set_page_config(
    page_title="AI Tech Watch Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre de l'application
st.title("🤖 AI Tech Watch Agent")
st.subheader("Votre agent de veille technologique IA")

# Configuration du backend
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")

# Initialisation de l'état de session
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_id" not in st.session_state:
    st.session_state.user_id = f"user_{hash(str(datetime.now())) % 10000}"

def call_backend_api(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Appelle l'API backend"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur API: {response.status_code} - {response.text}")
            return {}
    except Exception as e:
        st.error(f"Erreur de connexion au backend: {str(e)}")
        return {}

def display_paper(paper: Dict):
    """Affiche les détails d'un article"""
    with st.expander(f"📄 {paper.get('title', 'Titre inconnu')}"):
        st.write(f"**Auteurs:** {', '.join(paper.get('authors', [])) if paper.get('authors') else 'Inconnus'}")
        st.write(f"**Date:** {paper.get('published', 'Inconnue')}")
        st.write(f"**Source:** {paper.get('source', 'Inconnue')}")
        st.write(f"**Catégories:** {', '.join(paper.get('categories', [])) if paper.get('categories') else 'Aucune'}")
        st.write(f"**Résumé:** {paper.get('abstract', 'Résumé non disponible')[:500]}...")
        
        if paper.get('url'):
            st.markdown(f"[Lien vers l'article]({paper.get('url')})")

def main():
    # Barre latérale
    with st.sidebar:
        st.header("🔍 Options de recherche")
        
        # Filtres de recherche
        max_papers = st.slider("Nombre maximum d'articles", 1, 20, 10)
        source_filter = st.selectbox("Source", ["Toutes", "arXiv", "Semantic Scholar"], index=0)
        
        st.divider()
        
        # Informations sur l'application
        st.header("ℹ️ À propos")
        st.write("AI Tech Watch Agent est un agent de veille technologique utilisant l'IA pour analyser et résumer les dernières recherches académiques.")
        
        # Liens utiles
        st.header("🔗 Liens")
        st.markdown("[Documentation API](http://localhost:8000/docs)")
        st.markdown("[GitHub](https://github.com/votre-compte/ai-tech-watch)")
        
        # Statistiques
        if st.button("Mettre à jour les statistiques"):
            with st.spinner("Récupération des statistiques..."):
                stats = call_backend_api("/api/v1/metrics")
                if stats:
                    st.metric("Total requêtes", stats.get("total_queries", 0))
                    st.metric("Note moyenne", f"{stats.get('avg_rating', 0.0):.2f}")
    
    # Colonne principale
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Zone de saisie de la requête
        query = st.text_input(
            "Posez votre question sur les dernières recherches en IA :", 
            placeholder="Ex: Quelles sont les dernières avancées en NLP ?"
        )
        
        if st.button("🔍 Rechercher", type="primary") and query:
            with st.spinner("Recherche en cours..."):
                # Appel à l'API backend
                request_data = {
                    "query_text": query,
                    "user_id": st.session_state.user_id,
                    "max_papers": max_papers
                }
                
                if source_filter != "Toutes":
                    request_data["filters"] = {"source": source_filter}
                
                response = call_backend_api("/api/v1/query", method="POST", data=request_data)
                
                if response:
                    # Affichage de la réponse
                    st.success("Recherche terminée !")
                    st.write("### 📝 Réponse")
                    st.write(response.get("answer", "Aucune réponse disponible"))
                    
                    # Affichage des articles utilisés
                    papers_used = response.get("papers_used", [])
                    if papers_used:
                        st.write(f"### 📚 Articles utilisés ({len(papers_used)})")
                        for paper in papers_used:
                            display_paper(paper)
                    
                    # Stockage de la conversation
                    st.session_state.messages.append({
                        "query": query,
                        "response": response.get("answer", ""),
                        "papers": papers_used,
                        "timestamp": datetime.now().isoformat()
                    })
    
    with col2:
        st.header("📊 Dashboard")
        
        # Affichage des tendances
        with st.expander("📈 Sujets tendance"):
            trends = call_backend_api("/api/v1/trends")
            if trends and "trending_topics" in trends:
                for topic in trends["trending_topics"][:5]:
                    st.write(f"- {topic['topic']} ({topic['count']} mentions)")
        
        # Historique des requêtes
        with st.expander("📋 Historique"):
            if st.session_state.messages:
                for i, msg in enumerate(st.session_state.messages[-5:]):  # Les 5 dernières
                    if st.button(f"Q: {msg['query'][:50]}...", key=f"hist_{i}"):
                        # Affichage de la réponse complète
                        st.write("### Question:")
                        st.write(msg['query'])
                        st.write("### Réponse:")
                        st.write(msg['response'])
                        
                        if msg['papers']:
                            st.write("### Articles:")
                            for paper in msg['papers']:
                                display_paper(paper)
            else:
                st.write("Aucune requête récente")
    
    # Affichage de l'historique complet
    if st.session_state.messages:
        st.divider()
        st.header("📜 Historique complet")
        
        for i, msg in enumerate(st.session_state.messages):
            with st.container():
                st.write(f"**Question {len(st.session_state.messages)-i}:** {msg['query']}")
                st.write(f"**Réponse:** {msg['response']}")
                
                if msg['papers']:
                    with st.expander(f"Articles associés ({len(msg['papers'])})", expanded=False):
                        for paper in msg['papers']:
                            display_paper(paper)
                
                st.divider()

if __name__ == "__main__":
    main()