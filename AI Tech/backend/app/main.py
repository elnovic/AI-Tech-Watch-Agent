from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import papers, queries, monitoring
from app.core.config import settings
from app.core.database import engine, Base
from app.monitoring.arize_config import arize_client
import logging

# Création des tables dans la base de données (uniquement si nécessaire)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logging.warning(
        f"Impossible de créer les tables: {e}. Cela peut être normal en développement.")

app = FastAPI(
    title="AI Tech Watch Agent API",
    description="API pour l'agent de veille technologique IA",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ajuster en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes
app.include_router(papers.router, prefix="/api/v1", tags=["papers"])
app.include_router(queries.router, prefix="/api/v1", tags=["queries"])
app.include_router(monitoring.router, prefix="/api/v1", tags=["monitoring"])


@app.get("/health")
async def health_check():
    """Vérification de l'état de santé de l'API"""
    return {"status": "healthy", "service": "backend"}


@app.on_event("startup")
async def startup_event():
    """Actions à effectuer au démarrage de l'application"""
    logging.info("Démarrage de l'application AI Tech Watch Agent")
    # Initialisation du client Arize
    if arize_client:
        logging.info("Client Arize initialisé avec succès")


@app.on_event("shutdown")
async def shutdown_event():
    """Actions à effectuer à l'arrêt de l'application"""
    logging.info("Arrêt de l'application AI Tech Watch Agent")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
