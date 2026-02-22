# Contexte Projet JARVIS 2.0 - Pour IA Externe

**Statut** : META  
**Version** : 2.0  
**Date** : 2026-02-12  
**Objectif** : Fournir à une IA externe toutes les informations nécessaires pour comprendre et améliorer le projet

---

## 📋 Résumé Exécutif

**JARVIS 2.0** est une application web conversationnelle avec gestion de projets, permettant de dialoguer avec des agents IA basés sur Mistral AI.

**État actuel** : Fonctionnel — 2 agents distincts, persistance SQLite, système de projets  
**Phase** : Post-migration architecture 2 agents  
**Prochaine étape** : Orchestration multi-agents

---

## 🎯 Objectif du Projet

Créer un assistant IA personnel orchestrant des agents spécialisés pour gérer les projets de Val C. selon une méthodologie stricte : Audit → Plan → Validation → Exécution → Documentation.

---

## 🏗️ Architecture Technique

### Stack
- **Backend** : FastAPI (Python) + SQLite (aiosqlite)
- **Frontend** : HTML/CSS/JavaScript vanilla
- **IA** : Mistral AI Agent API (beta.conversations) — 2 Agent IDs distincts
- **Dépendances** : fastapi, uvicorn, python-dotenv, mistralai, aiosqlite

### Structure des Répertoires
```
Jarvis 2.0/
├── backend/
│   ├── agents/
│   │   ├── base_agent.py          # Classe agent de base
│   │   ├── jarvis_maitre.py       # Agent JARVIS_Maître
│   │   ├── agent_config.py        # Configuration centralisée agents
│   │   └── agent_factory.py       # Factory + cache + injection Agent ID
│   ├── ia/
│   │   └── mistral_client.py      # Client API Mistral
│   ├── db/
│   │   ├── database.py            # Couche accès SQLite
│   │   └── schema.sql             # Schéma DB
│   ├── services/
│   │   └── file_service.py        # Lecture fichiers projet
│   ├── models.py                  # Modèles Pydantic
│   ├── api.py                     # Routes FastAPI
│   └── app.py                     # Point d'entrée
├── frontend/
│   ├── projects.html              # Gestion projets
│   ├── project.html               # Vue projet + chat + fichiers
│   └── ...
├── tests/                         # 33 tests (19 BASE + 14 JARVIS_Maître)
├── docs/                          # Documentation (reference/work/history/_meta)
├── .env                           # Configuration (non versionné)
├── .env.example                   # Template config
└── requirements.txt               # Dépendances Python
```

### Composants Clés

#### Backend
1. **`app.py`** : Point d'entrée FastAPI, CORS localhost, health check, init DB
2. **`api.py`** : CRUD projets, conversations, messages, fichiers, GET /agents
3. **`agent_config.py`** : Source unique de vérité (mapping agent → env_var + métadonnées)
4. **`agent_factory.py`** : Instanciation agents avec injection dynamique Agent ID
5. **`base_agent.py`** : Validation messages (user/assistant uniquement), journalisation JSON Lines
6. **`mistral_client.py`** : Wrapper `beta.conversations.start(agent_id=...)`
7. **`database.py`** : SQLite async (projets, conversations, messages)

---

## 🔄 Flux de Données

```
User Input → POST /api/conversations/{id}/messages
→ api.py → agent_factory.get_agent() → agent.handle()
→ mistral_client.send() → Mistral API → Réponse
→ Sauvegarde DB → Retour JSON → Frontend
```

---

## 🔐 Configuration

### Variables d'Environnement (`.env`)
```env
MISTRAL_API_KEY=<clé API Mistral>
MISTRAL_MODEL=mistral-small-latest
JARVIS_BASE_AGENT_ID=<ID agent BASE côté Mistral>
JARVIS_MAITRE_AGENT_ID=<ID agent JARVIS_Maître côté Mistral>
USE_MISTRAL_AGENT_API=1
```

**Principe** : Chaque agent a son propre Agent ID Mistral. Les instructions sont configurées côté Mistral (cloud), pas dans le backend.

---

## 📡 API Endpoints (résumé)

- `GET /` — Health check
- `GET /agents` — Liste agents disponibles
- `POST /api/projects` — Créer projet
- `GET /api/projects` — Lister projets
- `POST /api/conversations` — Créer conversation standalone
- `POST /api/projects/{id}/conversations` — Créer conversation projet
- `POST /api/conversations/{id}/messages` — Envoyer message
- `GET /api/conversations/{id}/messages` — Historique messages
- `GET /api/projects/{id}/files/tree|list|read|search` — Fichiers projet

Voir `reference/API_SPECIFICATION_V2.md` pour la spécification complète.

---

## 🚀 Démarrage

```bash
cd "d:\Coding\AppWindows\Jarvis 2.0"
python -m uvicorn backend.app:app --reload --port 8000
```

- Projets : `http://localhost:8000/projects.html`
- Projet : `http://localhost:8000/project.html?id=<project_id>`

---

## ✅ Ce Qui Fonctionne

- ✅ 2 agents IA distincts (BASE worker, JARVIS_Maître orchestrator)
- ✅ Persistance SQLite (projets, conversations, messages)
- ✅ Chat avec contexte projet (arborescence injectée au 1er message)
- ✅ Lecture fichiers projet sécurisée (1MB max, whitelist extensions)
- ✅ Validation stricte messages (rôle system rejeté)
- ✅ Journalisation JSON Lines (jarvis_audit.log)
- ✅ 33 tests passent
- ✅ Configuration centralisée (agent_config.py)
- ✅ Architecture prête pour orchestrateur/worker

---

## ⚠️ Limitations Actuelles

- **Pas d'authentification** : usage local uniquement
- **Pas de rate limiting** : acceptable pour usage personnel
- **Pas d'orchestration réelle** : JARVIS_Maître ne route pas encore vers workers
- **Frontend vanilla** : HTML/CSS/JS pur
- **Pas de streaming** : réponses synchrones
- **Cache singleton** : modification `.env` nécessite redémarrage

---

## 🔮 Prochaines Étapes

1. **Orchestration** : Routage JARVIS_Maître → agents spécialisés
2. **Agents spécialisés** : AUDITEUR, EXÉCUTANT, TESTEUR, etc.
3. **Streaming** : Réponses en temps réel
4. **Frontend moderne** : Migration React/Vue envisageable

---

## 💡 Conseils pour l'IA Externe

1. **Lire d'abord** : `docs/_meta/INDEX.md` puis `docs/reference/ARCHITECTURE.md`
2. **Comprendre le flux** : Tracer une requête de bout en bout
3. **Respecter l'existant** : Ne pas tout réécrire, améliorer progressivement
4. **Documenter les changements** : Mettre à jour `CHANGELOG.md`

---

**Fin du document de contexte**

Ce document doit être mis à jour à chaque évolution majeure du projet.
