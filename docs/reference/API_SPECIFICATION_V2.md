# Spécification API - JARVIS 2.0

**Statut** : REFERENCE  
**Version** : 2.1  
**Date** : 2026-02-12  
**Remplace** : API_SPECIFICATION.md (archivé)

---

## 🌐 Base URL

```
http://localhost:8000
```

---

## 📋 Vue d'Ensemble

JARVIS 2.0 propose deux modes de chat :
- **Chat Simple** : Conversations standalone sans projet
- **Chat Projet** : Conversations liées à un projet avec contexte fichiers

Les deux modes utilisent la même structure de données (conversations + messages).

---

## 📡 Endpoints

### 1. Health Check

**GET** `/`

Vérifie que le backend est opérationnel.

#### Réponse (200)
```json
{
  "status": "Jarvis backend running"
}
```

---

### 2. Liste des Agents

**GET** `/agents`

Liste les agents disponibles avec leurs métadonnées.

#### Réponse (200)
```json
{
  "agents": [
    {
      "id": "BASE",
      "name": "BASE",
      "role": "Assistant générique",
      "description": "Agent neutre servant de modèle pour tous les futurs agents."
    },
    {
      "id": "JARVIS_Maître",
      "name": "JARVIS_Maître",
      "role": "Assistant personnel principal",
      "description": "Assistant IA personnel de Val C. Interface centrale du système JARVIS."
    }
  ]
}
```

---

## 🗨️ Conversations Standalone (Chat Simple)

### 3. Créer Conversation Standalone

**POST** `/api/conversations`

Crée une conversation sans projet (chat simple).

#### Headers
```
Content-Type: application/json
```

#### Body
```json
{
  "agent_id": "BASE",
  "title": "Chat BASE"
}
```

**Paramètres** :
- `agent_id` (string, requis) : `BASE` ou `JARVIS_Maître`
- `title` (string, optionnel) : Titre de la conversation

#### Réponse (200)
```json
{
  "id": "uuid",
  "project_id": null,
  "agent_id": "BASE",
  "title": "Chat BASE",
  "created_at": "2026-02-12T10:00:00",
  "updated_at": "2026-02-12T10:00:00",
  "message_count": 0
}
```

---

### 4. Lister Conversations Standalone

**GET** `/api/conversations`

Liste toutes les conversations standalone (sans projet).

#### Réponse (200)
```json
[
  {
    "id": "uuid",
    "project_id": null,
    "agent_id": "BASE",
    "title": "Chat BASE",
    "created_at": "2026-02-12T10:00:00",
    "updated_at": "2026-02-12T10:05:00",
    "message_count": 5
  }
]
```

---

## 📁 Projets

### 5. Créer Projet

**POST** `/api/projects`

Crée un nouveau projet.

#### Body
```json
{
  "name": "Mon Projet",
  "path": "D:/Coding/MonProjet",
  "description": "Description optionnelle"
}
```

#### Réponse (200)
```json
{
  "id": "uuid",
  "name": "Mon Projet",
  "path": "D:/Coding/MonProjet",
  "description": "Description optionnelle",
  "created_at": "2026-02-12T10:00:00",
  "conversation_count": 0
}
```

#### Erreurs
- **400** : Chemin invalide ou inexistant
- **500** : Erreur serveur

---

### 6. Lister Projets

**GET** `/api/projects`

Liste tous les projets.

#### Réponse (200)
```json
[
  {
    "id": "uuid",
    "name": "Mon Projet",
    "path": "D:/Coding/MonProjet",
    "description": "Description",
    "created_at": "2026-02-12T10:00:00",
    "conversation_count": 3
  }
]
```

---

### 7. Détails Projet

**GET** `/api/projects/{project_id}`

Récupère les détails d'un projet.

#### Réponse (200)
```json
{
  "id": "uuid",
  "name": "Mon Projet",
  "path": "D:/Coding/MonProjet",
  "description": "Description",
  "created_at": "2026-02-12T10:00:00",
  "conversation_count": 3
}
```

#### Erreurs
- **404** : Projet non trouvé

---

### 8. Mettre à Jour Projet

**PUT** `/api/projects/{project_id}`

Met à jour un projet (nom et/ou description).

#### Body
```json
{
  "name": "Nouveau Nom",
  "description": "Nouvelle description"
}
```

#### Réponse (200)
```json
{
  "id": "uuid",
  "name": "Nouveau Nom",
  "path": "D:/Coding/MonProjet",
  "description": "Nouvelle description",
  "created_at": "2026-02-12T10:00:00",
  "conversation_count": 3
}
```

---

### 9. Supprimer Projet

**DELETE** `/api/projects/{project_id}`

Supprime un projet et toutes ses conversations (CASCADE).

#### Réponse (200)
```json
{
  "message": "Project deleted successfully"
}
```

---

## 🗨️ Conversations Projet

### 10. Créer Conversation Projet

**POST** `/api/projects/{project_id}/conversations`

Crée une conversation liée à un projet.

#### Body
```json
{
  "agent_id": "JARVIS_Maître",
  "title": "Conversation 10:30"
}
```

#### Réponse (200)
```json
{
  "id": "uuid",
  "project_id": "project-uuid",
  "agent_id": "JARVIS_Maître",
  "title": "Conversation 10:30",
  "created_at": "2026-02-12T10:30:00",
  "updated_at": "2026-02-12T10:30:00",
  "message_count": 0
}
```

---

### 11. Lister Conversations Projet

**GET** `/api/projects/{project_id}/conversations`

Liste les conversations d'un projet.

#### Réponse (200)
```json
[
  {
    "id": "uuid",
    "project_id": "project-uuid",
    "agent_id": "JARVIS_Maître",
    "title": "Conversation 10:30",
    "created_at": "2026-02-12T10:30:00",
    "updated_at": "2026-02-12T10:35:00",
    "message_count": 8
  }
]
```

---

## 💬 Messages (Commun aux deux modes)

### 12. Détails Conversation

**GET** `/api/conversations/{conversation_id}`

Récupère les détails d'une conversation (standalone ou projet).

#### Réponse (200)
```json
{
  "id": "uuid",
  "project_id": null,
  "agent_id": "BASE",
  "title": "Chat BASE",
  "created_at": "2026-02-12T10:00:00",
  "updated_at": "2026-02-12T10:05:00",
  "message_count": 5
}
```

---

### 13. Supprimer Conversation

**DELETE** `/api/conversations/{conversation_id}`

Supprime une conversation et tous ses messages (CASCADE).

#### Réponse (200)
```json
{
  "message": "Conversation deleted successfully"
}
```

---

### 14. Lister Messages

**GET** `/api/conversations/{conversation_id}/messages`

Récupère l'historique des messages d'une conversation.

#### Query Parameters
- `limit` (int, optionnel, défaut: 100) : Nombre max de messages

#### Réponse (200)
```json
[
  {
    "id": 1,
    "conversation_id": "uuid",
    "role": "user",
    "content": "Bonjour",
    "timestamp": "2026-02-12T10:00:00"
  },
  {
    "id": 2,
    "conversation_id": "uuid",
    "role": "assistant",
    "content": "Bonjour ! Comment puis-je vous aider ?",
    "timestamp": "2026-02-12T10:00:05"
  }
]
```

---

### 15. Envoyer Message

**POST** `/api/conversations/{conversation_id}/messages`

Envoie un message à l'agent IA.

**Comportement** :
- **Conversation standalone** : Pas de contexte projet
- **Conversation projet** : Contexte projet injecté au 1er message

#### Body
```json
{
  "content": "Bonjour, qui es-tu ?"
}
```

#### Réponse (200)
```json
{
  "response": "Bonjour ! Je suis BASE, un agent IA générique...",
  "conversation_id": "uuid",
  "agent_id": "BASE"
}
```

#### Erreurs
- **404** : Conversation non trouvée
- **400** : Message invalide
- **502** : Réponse Mistral mal formatée
- **503** : API Mistral indisponible

---

## 📂 Système de Fichiers (Projets uniquement)

### 16. Arborescence Projet

**GET** `/api/projects/{project_id}/files/tree`

Récupère l'arborescence complète du projet.

#### Query Parameters
- `max_depth` (int, optionnel, défaut: 3) : Profondeur max

#### Réponse (200)
```json
{
  "name": "MonProjet",
  "type": "directory",
  "items": [
    {
      "name": "backend",
      "type": "directory",
      "items": [...]
    },
    {
      "name": "README.md",
      "type": "file",
      "size": 1024,
      "extension": ".md"
    }
  ]
}
```

---

### 17. Lister Fichiers Dossier

**GET** `/api/projects/{project_id}/files/list`

Liste le contenu d'un dossier spécifique.

#### Query Parameters
- `path` (string, optionnel) : Chemin relatif au projet

#### Réponse (200)
```json
{
  "path": "backend",
  "items": [
    {
      "name": "app.py",
      "path": "backend/app.py",
      "type": "file",
      "size": 2048,
      "extension": ".py",
      "modified_at": "2026-02-12T09:00:00"
    }
  ],
  "total_count": 1
}
```

---

### 18. Lire Fichier

**GET** `/api/projects/{project_id}/files/read`

Lit le contenu d'un fichier texte.

#### Query Parameters
- `path` (string, requis) : Chemin relatif au fichier

#### Réponse (200)
```json
{
  "path": "backend/app.py",
  "content": "from fastapi import FastAPI\n...",
  "size": 2048,
  "encoding": "utf-8"
}
```

#### Erreurs
- **403** : Path traversal détecté
- **404** : Fichier non trouvé
- **413** : Fichier trop large (>1MB)
- **415** : Extension non autorisée
- **422** : Encodage impossible (binaire)

---

### 19. Rechercher Fichiers

**GET** `/api/projects/{project_id}/files/search`

Recherche des fichiers par nom/pattern.

#### Query Parameters
- `pattern` (string, requis) : Pattern de recherche
- `max_results` (int, optionnel, défaut: 50) : Nombre max de résultats

#### Réponse (200)
```json
[
  {
    "name": "app.py",
    "path": "backend/app.py",
    "type": "file",
    "size": 2048,
    "extension": ".py",
    "modified_at": "2026-02-12T09:00:00"
  }
]
```

---

## 🔄 Flux Utilisateur

### Chat Simple (index.html)

```
1. GET /agents → Liste agents
2. POST /api/conversations {agent_id} → Créer conversation standalone
3. POST /api/conversations/{id}/messages {content} → Envoyer message
4. Réponse IA (sans contexte projet)
```

### Chat Projet (project.html)

```
1. POST /api/projects {name, path} → Créer projet
2. POST /api/projects/{id}/conversations {agent_id} → Créer conversation
3. POST /api/conversations/{id}/messages {content} → Envoyer message
   → Au 1er message, contexte projet injecté automatiquement
4. Réponse IA (avec contexte projet)
```

---

## 🗄️ Structure Base de Données

### Table: projects
```sql
id TEXT PRIMARY KEY
name TEXT NOT NULL
path TEXT NOT NULL UNIQUE
description TEXT
created_at TIMESTAMP
```

### Table: conversations
```sql
id TEXT PRIMARY KEY
project_id TEXT NULL  -- NULL pour standalone, UUID pour projet
agent_id TEXT NOT NULL
title TEXT
created_at TIMESTAMP
updated_at TIMESTAMP
FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
```

### Table: messages
```sql
id INTEGER PRIMARY KEY AUTOINCREMENT
conversation_id TEXT NOT NULL
role TEXT NOT NULL CHECK(role IN ('user', 'assistant'))
content TEXT NOT NULL
timestamp TIMESTAMP
FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
```

---

## 🔐 Sécurité

### État Actuel
- ✅ CORS restreint à localhost
- ✅ Validation path traversal (fichiers)
- ✅ Limite taille fichiers (1MB)
- ✅ Extensions autorisées (whitelist)
- ❌ Pas d'authentification
- ❌ Pas de rate limiting

### Recommandations Futures
- Authentification (JWT, API Key)
- Rate limiting (par IP)
- Validation taille messages
- Sanitization inputs

---

## 📊 Codes de Statut HTTP

| Code | Signification | Cause |
|------|---------------|-------|
| 200  | OK | Requête traitée avec succès |
| 400  | Bad Request | Données invalides |
| 403  | Forbidden | Path traversal, permission refusée |
| 404  | Not Found | Ressource non trouvée |
| 413  | Payload Too Large | Fichier trop large |
| 415  | Unsupported Media Type | Extension non autorisée |
| 422  | Unprocessable Entity | Encodage impossible |
| 500  | Internal Server Error | Erreur interne |
| 502  | Bad Gateway | Réponse Mistral mal formatée |
| 503  | Service Unavailable | API Mistral indisponible |

---

## 🔮 Évolutions Prévues

1. **Orchestration multi-agents** : Routage intelligent JARVIS → agents spécialisés
2. **Streaming** : Réponses en temps réel (SSE/WebSocket)
3. **Authentification** : JWT pour sécuriser l'API
4. **Rate limiting** : Protection contre abus
5. **Métadonnées** : Tokens utilisés, coûts, temps réponse
6. **Historique avancé** : Recherche, filtres, export

---

## 📝 Changelog

### v2.1 (2026-02-12)
- ✅ Ajout conversations standalone (`project_id: null`)
- ✅ Endpoints `/api/conversations` (POST/GET)
- ✅ Gestion conditionnelle contexte projet
- ✅ Unification chat simple et chat projet
- ✅ Suppression endpoints `/chat` et `/select_agent` (obsolètes)

### v2.0 (2026-02-10)
- Système de projets avec conversations
- Gestion fichiers (tree, list, read, search)
- Injection contexte projet
- Base de données SQLite
