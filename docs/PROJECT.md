# Projet — JARVIS

## Résumé

JARVIS est une plateforme locale minimale (frontend statique + backend FastAPI) qui expose un endpoint de chat. Le backend orchestre un **Agent de Base** qui valide l’historique de conversation et délègue la génération de réponse à l’API Mistral **Agent**.

## Structure du dépôt

- `frontend/`
  - `index.html` : UI minimaliste
  - `script.js` : appels HTTP vers le backend (`POST /chat`) + stockage local du `session_id`
  - `style.css` : styles
- `backend/`
  - `app.py` : application FastAPI (CORS + montage du routeur)
  - `api.py` : routes HTTP (actuellement `/` et `/chat`) + gestion des sessions en mémoire
  - `agents/`
    - `agent_registry.py` : singleton d’agent (prépare le multi-agent)
    - `base_agent.py` : validation/normalisation des messages + appel au client IA
  - `ia/`
    - `mistral_client.py` : client bas niveau Mistral (Agent API)
- `requirements.txt` : dépendances Python
- `.env.example` : exemple de variables d’environnement

## Exécution (dev)

### Prérequis

- Python installé
- Une clé Mistral valide
- Un agent Mistral existant (son `agent_id`)

### Installation

```bash
pip install -r requirements.txt
```

### Configuration

Copier `.env.example` en `.env` et renseigner :

- `MISTRAL_API_KEY`
- `JARVIS_BASE_AGENT_ID`
- `USE_MISTRAL_AGENT_API=1`

### Lancer le backend

```bash
uvicorn backend.app:app --reload
```

Backend:

- Healthcheck: `GET http://localhost:8000/`
- Swagger: `http://localhost:8000/docs`

### Lancer le frontend

Le frontend est statique. Ouvre `frontend/index.html` dans un navigateur.

Note: le frontend appelle `http://localhost:8000/chat` (CORS est permissif `*`).

## Architecture logique (flux principal)

- Le frontend envoie `{ message, session_id }` à `POST /chat`.
- Le backend gère un store de sessions en mémoire process (`SESSIONS`) pour conserver l’historique des messages.
- Le backend transmet l’historique (liste de messages `{role, content}`) à l’agent.
- L’agent valide le format runtime et appelle Mistral via `beta.conversations.start(agent_id=..., inputs=...)`.
- Le backend renvoie `{ response, session_id }`.

## Stockage / état

- Session: **en mémoire** (dict `SESSIONS` dans `backend/api.py`).
- Conséquence: l’historique est perdu au redémarrage et n’est pas partagé entre plusieurs process.

## Limites connues (actuelles)

- Pas d’authentification.
- CORS autorise toutes origines.
- Sessions en mémoire uniquement.
- Un seul agent (singleton) même si le design prépare le multi-agent.
