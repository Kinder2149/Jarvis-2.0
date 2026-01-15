# JARVIS

Plateforme locale minimale basée sur un **Agent de Base**,
préparée pour évoluer vers un système multi-agents.

## Architecture

- frontend/ : UI de chat simple
- backend/
  - api : interface HTTP
  - ia : clients IA (Mistral)
  - agents : modèle et implémentations d’agents

## Lancer le backend

```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload