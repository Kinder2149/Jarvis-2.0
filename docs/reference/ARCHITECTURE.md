# Architecture Technique - JARVIS 2.0

**Statut** : REFERENCE  
**Version** : 3.0  
**Date** : 2026-02-12  
**Dernière mise à jour** : Migration architecture 2 agents distincts

---

## Vue d'Ensemble

JARVIS 2.0 est une application web conversationnelle avec gestion de projets, basée sur une architecture client-serveur.

**Stack Technique** :
- **Backend** : FastAPI (Python) + SQLite (aiosqlite)
- **Frontend** : HTML/CSS/JavaScript vanilla
- **IA** : Mistral AI Agent API (beta.conversations) — 2 agents distincts
- **Gestion d'environnement** : python-dotenv

---

## Architecture Globale

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│  projects.html (gestion projets)                            │
│  project.html  (chat + fichiers + conversations)            │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JSON
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                         BACKEND                             │
│                      (FastAPI/Python)                       │
│                                                             │
│  ┌──────────────┐      ┌───────────────┐                   │
│  │   api.py     │─────▶│ agent_factory │                   │
│  │  (Routes)    │      │ + agent_config│                   │
│  └──────┬───────┘      └──────┬────────┘                   │
│         │                     │                             │
│         ▼                     ▼                             │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │   database   │      │  base_agent  │                    │
│  │   (SQLite)   │      │  (Logique)   │                    │
│  └──────────────┘      └──────┬───────┘                    │
│                               │                             │
│                               ▼                             │
│                        ┌──────────────┐                    │
│                        │mistral_client│                    │
│                        │ (API Wrapper)│                    │
│                        └──────┬───────┘                    │
└───────────────────────────────┼─────────────────────────────┘
                                │ HTTPS
                                ▼
                    ┌────────────────────────┐
                    │   Mistral AI Agent API │
                    │  (beta.conversations)  │
                    └────────────────────────┘
```

---

## Structure des Répertoires

```
Jarvis 2.0/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Classe agent de base
│   │   ├── jarvis_maitre.py       # Agent JARVIS_Maître
│   │   ├── agent_config.py        # Configuration centralisée agents
│   │   └── agent_factory.py       # Factory + cache + injection Agent ID
│   ├── ia/
│   │   ├── __init__.py
│   │   └── mistral_client.py      # Client API Mistral
│   ├── db/
│   │   ├── database.py            # Couche accès SQLite (aiosqlite)
│   │   └── schema.sql             # Schéma DB (projects, conversations, messages)
│   ├── services/
│   │   └── file_service.py        # Lecture fichiers projet (sécurisée)
│   ├── models.py                  # Modèles Pydantic
│   ├── api.py                     # Routes FastAPI
│   └── app.py                     # Point d'entrée FastAPI
├── frontend/
│   ├── projects.html              # Gestion projets
│   ├── project.html               # Vue projet + chat + fichiers
│   ├── index.html                 # OBSOLÈTE
│   ├── script.js
│   └── style.css
├── tests/
│   ├── test_base_agent.py         # 19 tests
│   ├── test_jarvis_maitre.py      # 14 tests
│   ├── test_database.py
│   ├── test_file_service.py
│   └── test_api_integration.py
├── docs/                          # Documentation (reference/work/history/_meta)
├── .env                           # Configuration (non versionné)
├── .env.example                   # Template de configuration
├── .gitignore
└── requirements.txt               # Dépendances Python
```

---

## Composants Backend

### 1. `app.py` - Point d'Entrée FastAPI
- Initialise l'application FastAPI
- Configure CORS (restreint à localhost)
- Enregistre le router API
- Initialise la base de données au démarrage
- Expose un endpoint de health check `/`

### 2. `api.py` - Routes API
- **Endpoints** : CRUD projets, conversations (standalone + projet), messages, fichiers, GET /agents
- **Responsabilités** :
  - Gestion projets et conversations persistées en SQLite
  - Injection contexte projet au 1er message
  - Validation des requêtes
  - Gestion des erreurs (400, 404, 502, 503, 500)
- Voir `API_SPECIFICATION_V2.md` pour la spécification complète

### 3. `agents/agent_config.py` - Configuration Centralisée
- Source unique de vérité pour les agents
- Mapping agent_name → variable `.env` + métadonnées (rôle, permissions, type)

### 4. `agents/agent_factory.py` - Factory avec Cache
- Instanciation des agents avec injection dynamique Agent ID depuis `.env`
- Cache singleton par nom d'agent
- Lève `RuntimeError` si variable `.env` absente

### 5. `agents/base_agent.py` - Agent de Base
- Validation des messages (rôles `user`/`assistant` uniquement, `system` rejeté)
- Délégation à `MistralClient`
- Journalisation JSON Lines (`jarvis_audit.log`)
- Gestion d'état (idle → working → idle/error)

### 6. `ia/mistral_client.py` - Client Mistral
- Communication bas niveau avec Mistral Agent API
- `client.beta.conversations.start(agent_id=..., inputs=...)`
- Exceptions : `MistralUpstreamError`, `MistralResponseFormatError`

### 7. `db/database.py` - Couche Base de Données
- SQLite via aiosqlite (async)
- CRUD projets, conversations, messages
- Schéma défini dans `schema.sql`

### 8. `services/file_service.py` - Service Fichiers
- Lecture sécurisée de fichiers projet (1MB max, extensions whitelist)
- Arborescence, listing, recherche
- Protection path traversal

---

## Configuration

### Variables d'Environnement (`.env`)
```env
MISTRAL_API_KEY=<clé API Mistral>
MISTRAL_MODEL=mistral-small-latest
JARVIS_BASE_AGENT_ID=<ID agent BASE côté Mistral>
JARVIS_MAITRE_AGENT_ID=<ID agent JARVIS_Maître côté Mistral>
USE_MISTRAL_AGENT_API=1
```

**Obligatoires** :
- `MISTRAL_API_KEY`
- `JARVIS_BASE_AGENT_ID` (Agent ID distinct pour BASE)
- `JARVIS_MAITRE_AGENT_ID` (Agent ID distinct pour JARVIS_Maître)
- `USE_MISTRAL_AGENT_API=1` (active le mode Agent API)

---

## Flux de Données

### Envoi de Message
```
1. User Input (Frontend project.html)
   ↓
2. POST /api/conversations/{id}/messages {content}
   ↓
3. api.py récupère conversation + historique depuis SQLite
   ↓
4. agent_factory.get_agent(conversation.agent_id)
   ↓
5. agent.handle(messages, session_id)
   ↓
6. Validation messages (user/assistant uniquement)
   ↓
7. mistral_client.send(messages) → beta.conversations.start()
   ↓
8. Sauvegarde message user + réponse assistant en DB
   ↓
9. Retour JSON {response, conversation_id, agent_id}
   ↓
10. Affichage Frontend
```

---

## Démarrage

### Backend
```bash
cd "d:\Coding\AppWindows\Jarvis 2.0"
python -m uvicorn backend.app:app --reload --port 8000
```

### Frontend
- Projets : `http://localhost:8000/projects.html`
- Projet : `http://localhost:8000/project.html?id=<project_id>`

---

## 🔮 Évolutivité

### Points d'Extension Prévus
1. **Multi-agent** : `agent_config.py` + `agent_factory.py` prêts pour N agents
2. **Orchestration** : champ `type` (worker/orchestrator) déjà en place
3. **Streaming** : réponses actuellement synchrones, streaming possible
4. **Frontend avancé** : framework moderne (React, Vue) envisageable

---

## ⚠️ Limitations Actuelles (Usage Local/Personnel)

- **CORS restreint** : localhost uniquement
- **Pas d'authentification** : usage local uniquement
- **Pas de rate limiting** : acceptable pour usage personnel
- **Pas d'orchestration réelle** : JARVIS_Maître ne route pas encore vers workers
- **Frontend vanilla** : HTML/CSS/JS pur
- **Cache singleton** : modification `.env` nécessite redémarrage serveur
