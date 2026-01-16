# API — JARVIS

## Base URL

- `http://localhost:8000`

## Docs auto (FastAPI)

- Swagger UI: `GET /docs`
- OpenAPI JSON: `GET /openapi.json`

## Authentification

Aucune (actuellement).

## Endpoints

### `GET /`

Healthcheck.

- **Réponse 200**
  - Content-Type: `application/json`
  - Body:

```json
{ "status": "Jarvis backend running" }
```

---

### `POST /chat`

Envoie un message utilisateur et récupère la réponse IA. Gère une session conversationnelle via `session_id`.

#### Requête

- **Content-Type**: `application/json`

Body JSON:

- `message` (string, requis)
  - Message utilisateur.
- `session_id` (string, optionnel)
  - Si non fourni, le backend en génère un.
  - Si fourni, le backend récupère l’historique associé en mémoire.

Exemple:

```json
{ "message": "Bonjour", "session_id": "0f3a..." }
```

#### Réponse

- **Réponse 200**

```json
{ "response": "<texte>", "session_id": "<id>" }
```

Notes:

- `session_id` est renvoyé systématiquement.
- Le backend conserve l’historique en mémoire et l’enrichit avec les messages `user`/`assistant`.

#### Exemples

`curl`:

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Bonjour","session_id":null}'
```

#### Codes d’erreur

- **400**: erreur de validation runtime des messages (ex: format invalide)
- **502**: réponse upstream (Mistral) dans un format inattendu
- **503**: fournisseur upstream indisponible
- **500**: erreur interne

---

## Modèles (schémas)

### `ChatRequest`

- `message`: string
- `session_id`: string | null

### `ChatResponse`

- `response`: string
- `session_id`: string

## Sessions

- Stockage: in-memory (process-local)
- Impacts:
  - perte des sessions au redémarrage
  - non compatible multi-process sans stockage partagé
