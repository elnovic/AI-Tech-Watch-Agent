# AI Tech Watch Agent

Un agent de veille technologique intelligent utilisant l'IA pour surveiller et analyser les dernières recherches académiques en intelligence artificielle.

## 🚀 Fonctionnalités

- **Recherche intelligente** : Accès aux dernières publications arXiv et Semantic Scholar
- **Résumé IA** : Résumés automatiques avec OpenAI GPT-4
- **Interface utilisateur** : Interface Streamlit intuitive
- **Monitoring** : Suivi des performances avec Arize AI
- **API complète** : Points de terminaison REST pour intégration
- **Déploiement Docker** : Conteneurisation complète pour production

## 🛠️ Technologies utilisées

- **Backend** : FastAPI, PostgreSQL, SQLAlchemy
- **Frontend** : Streamlit
- **IA** : OpenAI GPT-4
- **Sources** : arXiv API, Semantic Scholar API
- **Monitoring** : Arize AI
- **Conteneurisation** : Docker, Docker Compose
- **Cache** : Redis

## 📁 Structure du projet

```
ai-tech-watch-production/
├── .vscode/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── endpoints/
│   │   ├── core/
│   │   ├── data/
│   │   ├── llm/
│   │   ├── monitoring/
│   │   ├── services/
│   │   └── utils/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── streamlit_app.py
│   ├── requirements.txt
│   └── Dockerfile
├── infrastructure/
│   ├── docker-compose.yml
│   └── nginx.conf
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Déploiement

### Prérequis

- Docker et Docker Compose
- Clé API OpenAI
- Clé API Arize (optionnelle pour le monitoring)

### Installation locale

1. Clonez le dépôt :

```bash
git clone <repository-url>
cd ai-tech-watch-production
```

2. Créez un fichier `.env` à partir de `.env.example` :

```bash
cp .env.example .env
```

3. Remplissez les variables d'environnement dans le fichier `.env` :

```env
OPENAI_API_KEY=votre_clé_openai
ARIZE_API_KEY=votre_clé_arize
ARIZE_SPACE_KEY=votre_clé_espace_arize
```

4. Lancez l'application avec Docker Compose :

```bash
docker-compose up --build
```

5. L'application sera accessible à l'adresse :
   - Interface utilisateur : http://localhost:8501
   - API documentation : http://localhost:8000/docs

### Déploiement sur Render.com

1. Créez un compte Render.com
2. Connectez votre dépôt GitHub
3. Créez un service Web avec la configuration suivante :
   - Type de service : Web Service
   - Runtime : Docker
   - Dockerfile : `./backend/Dockerfile`
   - Variables d'environnement : Configurez les variables depuis `.env.example`

## 📊 Monitoring avec Arize

L'application est intégrée avec Arize AI pour surveiller :
- La pertinence des réponses
- Les temps de réponse
- La fraîcheur des données
- La clarté des réponses

Les métriques sont automatiquement envoyées à Arize à chaque appel LLM.

## 🎯 Utilisation

1. Accédez à l'interface Streamlit à http://localhost:8501
2. Saisissez votre question sur les dernières recherches en IA
3. L'agent récupère les articles pertinents et génère une réponse avec citations
4. Donnez votre feedback pour améliorer l'agent

## 🔧 API Endpoints

### Recherche
```
POST /api/v1/query
```
Traite une question et retourne une réponse avec articles pertinents

### Feedback
```
POST /api/v1/feedback
```
Enregistre le feedback de l'utilisateur

### Articles récents
```
GET /api/v1/papers/recent
```
Récupère les derniers articles

### Métriques
```
GET /api/v1/metrics
```
Récupère les métriques de performance

## 💰 Modèle économique

- **Freemium** : 100 requêtes/mois gratuites
- **Pro** : 1000 requêtes/mois à 19€
- **Entreprise** : illimité à 99€/mois

## 🚨 Limitations et améliorations futures

- L'application est actuellement en version de démonstration
- Les fonctionnalités de gestion des utilisateurs sont limitées
- Les systèmes de limitation de débit sont basiques
- La mise en cache peut être améliorée

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez forker le dépôt et créer une pull request.

## 📄 Licence

Ce projet est sous licence MIT.