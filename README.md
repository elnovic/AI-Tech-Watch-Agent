# AI Tech Watch Agent

An AI research monitoring project designed to collect, organize, and explore recent technical publications and developments.

## Project overview

The repository contains a Python backend, a Streamlit interface, and Docker-based infrastructure. The backend includes components for research ingestion, querying, summarization, and monitoring.

## Main components

- **Backend** — FastAPI application and research services.
- **Research ingestion** — integrations for sources such as arXiv and Semantic Scholar.
- **LLM layer** — AI-assisted processing and summarization.
- **Monitoring** — application and model-related monitoring integrations.
- **Frontend** — Streamlit interface for interacting with research workflows.
- **Infrastructure** — Docker Compose and Nginx configuration.

## Repository layout

```text
AI Tech/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── data/
│   │   ├── llm/
│   │   ├── monitoring/
│   │   └── services/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── streamlit_app.py
│   └── requirements.txt
├── infrastructure/
└── docker-compose.yml
```

## Getting started

Review the backend and frontend dependency files before installing packages. Configure API keys, database credentials, and monitoring credentials through environment variables or local environment files. Never commit secrets.

The project includes Docker configuration under `AI Tech/`; inspect the compose files and required environment variables before starting the full stack.

## Development notes

- Keep backend, frontend, and infrastructure concerns separated.
- Do not commit local databases, Python bytecode, or generated artifacts in future changes.
- Keep credentials out of source control.
- Update the documentation when service names, environment variables, or deployment steps change.

## Project status

This is an evolving AI research monitoring project. The README documents the existing repository layout; deployment and external integrations may require additional configuration.
