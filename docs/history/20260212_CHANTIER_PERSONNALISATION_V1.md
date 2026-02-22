# CHANTIER — Personnalisation JARVIS v1

**Statut** : WORK  
**Date** : 2026-02-12  
**Objectif** : Transformer JARVIS v1 selon les décisions consolidées  
**Référence** : `JARVIS_Base_Document_Complet.md` (v2.0)

---

## ÉTAT ACTUEL DU PROJET — AUDIT TECHNIQUE

### Architecture Backend

```
backend/
├── app.py                    # FastAPI + CORS + lifespan (init DB) + mount frontend
├── api.py                    # Toutes les routes (334 lignes)
├── agents/
│   ├── agent_config.py       # AGENT_CONFIGS dict + get_agent_config() + list_available_agents()
│   ├── agent_factory.py      # get_agent() + _AGENTS_CACHE + clear_cache()
│   ├── base_agent.py         # BaseAgent class (handle, log, validate)
│   └── jarvis_maitre.py      # JarvisMaitre(BaseAgent) — juste __init__ override
├── ia/
│   └── mistral_client.py     # MistralClient — beta.conversations.start()
├── db/
│   ├── schema.sql            # 3 tables : projects, conversations, messages
│   └── database.py           # Database class async (aiosqlite)
├── models/
│   ├── __init__.py            # Exports Pydantic models
│   ├── project.py             # Project, ProjectCreate, ProjectUpdate
│   ├── conversation.py        # Conversation, ConversationCreate, Message, ChatMessage
│   └── file.py                # FileInfo, DirectoryListing, FileContent
└── services/
    ├── __init__.py
    ├── file_service.py        # FileService (read, list, tree, search)
    ├── file_cache.py          # FileTreeCache
    └── project_context.py     # build_project_context_message()
```

### Routes API (api.py)

| Méthode | Route | Fonction | Usage |
|---|---|---|---|
| POST | `/api/projects` | `create_project` | Créer projet |
| GET | `/api/projects` | `list_projects` | Lister projets |
| GET | `/api/projects/{id}` | `get_project` | Détail projet |
| PUT | `/api/projects/{id}` | `update_project` | MAJ projet |
| DELETE | `/api/projects/{id}` | `delete_project` | Supprimer projet |
| POST | `/api/conversations` | `create_standalone_conversation` | Conv standalone (chat simple) |
| GET | `/api/conversations` | `list_standalone_conversations` | Lister conv standalone |
| POST | `/api/projects/{id}/conversations` | `create_conversation` | Conv liée projet |
| GET | `/api/projects/{id}/conversations` | `list_conversations` | Lister conv projet |
| GET | `/api/conversations/{id}` | `get_conversation` | Détail conv |
| DELETE | `/api/conversations/{id}` | `delete_conversation` | Supprimer conv |
| GET | `/api/conversations/{id}/messages` | `get_messages` | Historique messages |
| POST | `/api/conversations/{id}/messages` | `send_message` | Envoyer message → agent |
| GET | `/api/projects/{id}/files/tree` | `get_file_tree` | Arborescence |
| GET | `/api/projects/{id}/files/list` | `list_files` | Listing répertoire |
| GET | `/api/projects/{id}/files/read` | `read_file` | Lire fichier |
| GET | `/api/projects/{id}/files/search` | `search_files` | Rechercher fichiers |
| GET | `/agents` | `get_agents` | Liste agents dispo |

### Schéma DB (schema.sql)

```sql
projects (id TEXT PK, name TEXT, path TEXT UNIQUE, description TEXT, created_at TIMESTAMP)
conversations (id TEXT PK, project_id TEXT FK NULL, agent_id TEXT, title TEXT, created_at, updated_at)
messages (id INTEGER PK AUTO, conversation_id TEXT FK, role TEXT CHECK(user|assistant), content TEXT, timestamp)
```

Point clé : `conversations.project_id` est **nullable** → c'est ce qui distingue chat simple (NULL) de mode projet (non-NULL).

### Méthodes Database (database.py)

| Méthode | Signature |
|---|---|
| `initialize()` | Init schema |
| `create_project(name, path, description)` | → dict |
| `get_project(project_id)` | → dict ou None |
| `list_projects()` | → list[dict] |
| `update_project(project_id, name, description)` | → bool |
| `delete_project(project_id)` | → bool |
| `create_conversation(agent_id, project_id=None, title=None)` | → dict |
| `get_conversation(conversation_id)` | → dict ou None |
| `list_conversations(project_id=None)` | → list[dict] |
| `delete_conversation(conversation_id)` | → bool |
| `update_conversation_timestamp(conversation_id)` | Auto |
| `update_conversation_title(conversation_id, title)` | |
| `add_message(conversation_id, role, content)` | → dict |
| `get_messages(conversation_id, limit=100)` | → list[dict] |
| `get_conversation_history(conversation_id)` | → list[{role, content}] |

### Agent System

**BaseAgent.__init__** : `(agent_id, name, role, description, permissions)`
- Crée `MistralClient(agent_id=agent_id)`
- Attributs : `self.id`, `self.name`, `self.role`, `self.description`, `self.permissions`, `self.state`
- `self.log_file = Path("jarvis_audit.log")`

**BaseAgent.handle(messages, session_id)** :
1. Valide messages (list de dict, role in user|assistant, content non vide)
2. Log `handle_request`
3. `self.client.send(validated_messages)` → appel Mistral
4. Log `handle_response`
5. Return response string

**MistralClient.send(messages)** :
```python
response = self.client.beta.conversations.start(
    agent_id=self.agent_id,
    inputs=messages,
    # PAS de temperature, PAS de max_tokens
)
```

**AGENT_CONFIGS** :
```python
"BASE": { env_var: "JARVIS_BASE_AGENT_ID", type: "worker", permissions: [read, write] }
"JARVIS_Maître": { env_var: "JARVIS_MAITRE_AGENT_ID", type: "orchestrator", permissions: [read, write, orchestrate] }
```

**agent_factory.get_agent(agent_name)** : Cache + instanciation selon nom.

### Flux send_message (api.py L191-241) — POINT CRITIQUE

```
1. Récupère conversation (get_conversation)
2. Récupère historique (get_conversation_history)
3. SI conversation.project_id ET len(messages)==0 :
   → Récupère projet
   → Récupère/cache file_tree
   → build_project_context_message(project, file_tree)
   → Préfixe msg.content avec le contexte
4. Ajoute message user en DB
5. get_agent(conversation.agent_id) → instance agent
6. agent.handle(messages, session_id=conversation_id)
7. Ajoute réponse assistant en DB
8. Return response
```

Point clé : Le contexte projet est injecté **uniquement au 1er message** (len(messages)==0). Il est préfixé au contenu du message user, pas envoyé séparément.

### build_project_context_message (project_context.py)

Génère un bloc markdown :
```
## CONTEXTE PROJET ACTIF
Vous travaillez sur le projet : **{name}**
Chemin : `{path}`
### Capacités disponibles
### Structure du projet (aperçu limité)
{arborescence formatée}
### Instructions
```

Pas de mention du mode, pas de mention de la méthodologie, pas d'indication de comportement attendu.

### Frontend SPA

**Architecture** : SPA hash-based (`#/route`)

| Route | Vue | Fichier |
|---|---|---|
| `#/` | Home (cards navigation) | `views/home.js` |
| `#/chat` | Chat Simple (standalone) | `views/chat-simple.js` |
| `#/projects` | Liste projets | `views/projects-list.js` |
| `#/projects/:id` | Détail projet (3 colonnes) | `views/project-detail.js` |

**State Manager** (`core/state.js`) :
- `currentAgent` : persisté en localStorage, défaut `"BASE"`
- `currentConversation`, `currentProject`, `agents`, etc.

**Chat Simple** (`views/chat-simple.js`) :
- Sélecteur d'agent → crée conversation standalone via `POST /api/conversations`
- `mode: 'simple'` passé au composant Chat

**Project Detail** (`views/project-detail.js`) :
- 3 colonnes : conversations | chat | fichiers
- Crée conversation via `POST /api/projects/{id}/conversations`
- `mode: 'project'` passé au composant Chat
- Sélection fichier → injection contenu dans input chat

Point clé : Le frontend passe déjà `mode: 'simple'` ou `mode: 'project'` au composant Chat. Mais ce mode n'est **pas transmis au backend**.

### Fichiers obsolètes identifiés

- `frontend/index-old.html`, `project-old.html`, `projects-old.html` — anciens fichiers
- `frontend/script-old.js`, `style-old.css` — anciens fichiers
- `frontend/js/chat-handler.js` — ancien handler (utilise `document.getElementById` direct, pas SPA)
- `frontend/js/conversation-manager.js` — ancien manager (utilise `projects.html` redirect, pas SPA)
- `frontend/js/projects-manager.js` — à vérifier si utilisé par la SPA

### Tests

| Fichier | Nb tests | Couverture |
|---|---|---|
| `test_base_agent.py` | 19 | Validation, état, logs, session_id |
| `test_jarvis_maitre.py` | 14 | Contrat, permissions, héritage |
| `test_database.py` | ~15 | CRUD projets, conversations, messages |
| `test_file_service.py` | ~10 | Lecture, arborescence, sécurité |
| `test_api_integration.py` | ~15 | Endpoints API intégration |

---

## MISSIONS

---

### MISSION 1 — Prompt Cloud Mistral pour Jarvis_maitre

**Priorité** : 🔴 CRITIQUE — Prérequis pour tout le reste  
**Effort** : Faible  
**Dépendances** : Aucune  
**Fichiers impactés** : Aucun (configuration côté Mistral Cloud)

**Objectif** : Rédiger et configurer les instructions de l'agent Mistral `JARVIS_MAITRE_AGENT_ID` (`ag_019c514a04a874159a21135b856a40e3`) pour qu'il se comporte comme défini dans le document de vision.

**À faire** :
- [ ] Récupérer les instructions actuelles de l'agent Mistral (Val C. doit les fournir)
- [ ] Rédiger un prompt système complet intégrant :
  - Identité : directeur technique personnel de Val C.
  - Langue : français
  - Ton : clair, structuré, sans jargon inutile
  - Rôle : garde-fou méthodologique, challengeur stratégique
  - Méthodologie : Audit → Plan → Validation → Exécution → Test → Documentation
  - Discipline : jamais de décision autonome, toujours proposer et attendre validation
  - Séparation réflexion / production
  - Capacité à refuser d'exécuter si plan flou
  - Format réponses : structurées (titres, listes, sections)
- [ ] Coller le prompt dans la plateforme Mistral AI
- [ ] Tester avec des conversations de validation

**Mémo** : Le prompt cloud est le SEUL endroit qui définit le comportement. Le code local ne contient aucune instruction comportementale.

**Validation** : Conversation test en mode chat simple + mode projet, vérifier que le comportement correspond.

---

### MISSION 2 — Paramètres techniques agent (temperature, max_tokens)

**Priorité** : 🔴 CRITIQUE  
**Effort** : Faible  
**Dépendances** : Aucune  
**Fichiers impactés** :
- `backend/agents/agent_config.py` — ajouter champs `temperature`, `max_tokens`
- `backend/ia/mistral_client.py` — passer paramètres à `beta.conversations.start()`
- `backend/agents/base_agent.py` — propager paramètres au MistralClient
- `backend/agents/agent_factory.py` — passer paramètres à l'instanciation
- `backend/agents/jarvis_maitre.py` — accepter paramètres
- `tests/test_base_agent.py` — tests paramètres
- `tests/test_jarvis_maitre.py` — tests paramètres

**À faire** :
- [ ] Ajouter dans `AGENT_CONFIGS` :
  ```
  "JARVIS_Maître": { ..., "temperature": 0.3, "max_tokens": 4096 }
  "BASE": { ..., "temperature": 0.7, "max_tokens": 4096 }
  ```
- [ ] Modifier `MistralClient.__init__` pour accepter `temperature` et `max_tokens`
- [ ] Modifier `MistralClient.send` :
  ```python
  response = self.client.beta.conversations.start(
      agent_id=self.agent_id,
      inputs=messages,
      temperature=self.temperature,    # NOUVEAU
      max_tokens=self.max_tokens,      # NOUVEAU
  )
  ```
- [ ] Modifier `BaseAgent.__init__` pour accepter et propager `temperature`, `max_tokens`
- [ ] Modifier `agent_factory.get_agent` pour passer ces paramètres depuis config
- [ ] Modifier `JarvisMaitre.__init__` pour accepter ces paramètres
- [ ] Ajouter tests unitaires

**Mémo** : Vérifier la doc Mistral `beta.conversations.start()` pour confirmer que `temperature` et `max_tokens` sont des paramètres acceptés. Si non disponibles, adapter.

**Validation** : Tests unitaires + test manuel (vérifier que temperature basse = réponses plus déterministes).

---

### MISSION 3 — Détection et injection du mode Chat / Projet

**Priorité** : 🟡 IMPORTANT  
**Effort** : Faible  
**Dépendances** : Mission 1 (le prompt cloud doit savoir interpréter le mode)  
**Fichiers impactés** :
- `backend/services/project_context.py` — enrichir le contexte injecté
- `backend/api.py` — modifier `send_message` (L191-241)

**Objectif** : Que Jarvis_maitre sache dans quel mode il opère et adapte son comportement.

**État actuel** :
- Le backend sait si `conversation.project_id` est NULL (chat simple) ou non (projet)
- Le frontend passe `mode: 'simple'` ou `mode: 'project'` au composant Chat mais NE le transmet PAS au backend
- `build_project_context_message` ne mentionne pas le mode ni la méthodologie

**À faire** :
- [ ] Modifier `build_project_context_message` pour ajouter des instructions de mode :
  ```
  ## MODE PROJET ACTIF
  Méthodologie obligatoire : Audit → Plan → Validation → Exécution → Test → Documentation
  Séparation stricte Réflexion / Production
  Challenge systématique
  Validation obligatoire avant production
  ```
- [ ] Modifier `send_message` dans `api.py` pour injecter un contexte mode même en chat simple (au 1er message) :
  ```
  ## MODE CHAT SIMPLE
  Réponses fluides, pas de méthodologie imposée.
  ```
- [ ] Point d'injection : `api.py` L200-217 — c'est là que le contexte est construit et préfixé

**Mémo** :
- Route concernée : `POST /api/conversations/{id}/messages` → fonction `send_message`
- Le contexte est préfixé au `msg.content` (L217) : `msg.content = f"{context_content}\n\n---\n\n{msg.content}"`
- Pour le chat simple, il faut ajouter une branche `else` après le `if conversation["project_id"]`

**Validation** : Test manuel — envoyer un message en chat simple et en mode projet, vérifier que l'agent adapte son comportement.

---

### MISSION 4 — Séparation Réflexion / Production dans l'interface

**Priorité** : 🟡 IMPORTANT  
**Effort** : Moyen  
**Dépendances** : Missions 1 + 3  
**Fichiers impactés** :
- Frontend : composant Chat, `project-detail.js`
- Potentiellement : `schema.sql`, `database.py`, `api.py` (si on persiste la phase)

**Objectif** : Que l'interface distingue visuellement les phases réflexion et production en mode projet.

**Approche proposée (à valider)** :

Option A — Côté prompt uniquement (effort minimal) :
- Jarvis_maitre structure ses réponses avec des marqueurs : `[RÉFLEXION]` et `[PRODUCTION]`
- Le frontend détecte ces marqueurs et applique un style différent
- Pas de modification DB

Option B — Avec persistance (effort moyen) :
- Ajouter colonne `phase TEXT DEFAULT 'reflexion'` dans `conversations`
- Endpoint pour changer de phase
- Frontend affiche un indicateur de phase + bouton de transition

**À faire (Option A, recommandée pour v1)** :
- [ ] Intégrer dans le prompt cloud : structurer les réponses avec marqueurs de phase
- [ ] Modifier le composant Chat frontend pour détecter et styliser les marqueurs
- [ ] Fichiers frontend à modifier : `js/components/chat.js` (rendu des messages)

**À faire (Option B, pour plus tard)** :
- [ ] Ajouter `phase` dans `conversations` (schema.sql)
- [ ] Ajouter méthode `update_conversation_phase` dans database.py
- [ ] Ajouter endpoint `PUT /api/conversations/{id}/phase`
- [ ] Frontend : indicateur + bouton transition

**Validation** : Test visuel — les réponses en mode projet doivent clairement distinguer réflexion et production.

---

### MISSION 5 — Orchestration simple (Jarvis_maitre → BASE)

**Priorité** : 🟡 IMPORTANT  
**Effort** : Moyen-élevé  
**Dépendances** : Missions 1 + 2  
**Fichiers impactés** :
- `backend/agents/jarvis_maitre.py` — ajouter méthode d'orchestration
- `backend/agents/agent_factory.py` — accès à BASE depuis Jarvis_maitre
- `backend/api.py` — modifier flux `send_message` ou créer service
- Nouveau fichier potentiel : `backend/services/orchestration.py`

**Objectif** : Permettre à Jarvis_maitre de solliciter BASE pour validation complémentaire.

**État actuel** :
- Chaque conversation est liée à UN agent (`conversation.agent_id`)
- `agent.handle()` fait un seul appel Mistral et retourne
- Pas de mécanisme pour qu'un agent appelle un autre

**Approche proposée** :
- Créer un service d'orchestration simple
- Jarvis_maitre peut demander une "second opinion" à BASE
- Le résultat est intégré dans la réponse finale

**À faire** :
- [ ] Créer `backend/services/orchestration.py` :
  ```
  class SimpleOrchestrator:
      def request_validation(agent_from, agent_to, context, question) -> str
  ```
- [ ] Modifier `JarvisMaitre` pour avoir accès à l'orchestrateur
- [ ] Définir le protocole : comment Jarvis_maitre décide de solliciter BASE
  - Option : via un marqueur dans la réponse (ex: `[DEMANDE_VALIDATION: ...]`)
  - Option : via le prompt cloud qui structure la demande
- [ ] Modifier `send_message` dans `api.py` pour détecter et traiter les demandes d'orchestration
- [ ] Journaliser les interactions inter-agents dans `jarvis_audit.log`

**Mémo** :
- `agent_factory.get_agent("BASE")` donne accès à l'instance BASE
- `base_agent.handle(messages)` est le point d'entrée
- Le session_id de la conversation doit être propagé pour traçabilité
- Attention : chaque appel Mistral consomme des tokens → limiter les allers-retours

**Risques** :
- Boucle infinie si mal configuré
- Latence doublée (2 appels Mistral au lieu de 1)
- Complexité du contexte partagé

**Validation** : Test en mode projet — Jarvis_maitre sollicite BASE et intègre sa réponse.

---

### MISSION 6 — Système de mémoire

**Priorité** : 🟢 UTILE  
**Effort** : Élevé  
**Dépendances** : Mission 3 (mode projet)  
**Fichiers impactés** :
- `backend/db/schema.sql` — nouvelles tables
- `backend/db/database.py` — nouvelles méthodes
- `backend/api.py` — nouveaux endpoints
- `backend/models/` — nouveaux modèles Pydantic
- `backend/services/project_context.py` — injection mémoire dans contexte

**Objectif** : Implémenter les 3 types de mémoire avec les 3 règles d'écriture.

**Nouvelles tables proposées** :
```sql
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK(type IN ('personal', 'project', 'technical')),
    project_id TEXT,  -- NULL pour personal et technical globale
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(type);
CREATE INDEX IF NOT EXISTS idx_memories_project ON memories(project_id);
```

**Nouveaux endpoints proposés** :
| Méthode | Route | Usage |
|---|---|---|
| POST | `/api/memories` | Créer mémoire |
| GET | `/api/memories?type=...&project_id=...` | Lister mémoires |
| PUT | `/api/memories/{id}` | MAJ mémoire |
| DELETE | `/api/memories/{id}` | Supprimer mémoire |

**À faire** :
- [ ] Ajouter table `memories` dans `schema.sql`
- [ ] Ajouter méthodes CRUD dans `database.py`
- [ ] Créer modèles Pydantic dans `backend/models/memory.py`
- [ ] Ajouter endpoints dans `api.py`
- [ ] Modifier `build_project_context_message` pour injecter les mémoires pertinentes
- [ ] Modifier `send_message` pour injecter mémoires personnelles en chat simple
- [ ] Respecter les 3 règles d'écriture (via prompt cloud + détection côté backend)
- [ ] Tests unitaires + intégration

**Mémo** :
- Injection mémoire = préfixer le contexte avec les mémoires pertinentes
- Point d'injection : même endroit que le contexte projet (`api.py` L200-217)
- Mémoire personnelle : toujours injectée
- Mémoire projet : injectée si conversation liée à un projet
- Mémoire technique : injectée selon pertinence (à définir)

**Validation** : Test CRUD mémoires + vérifier que l'agent utilise les mémoires dans ses réponses.

---

### MISSION 7 — Validation obligatoire pour actions critiques

**Priorité** : 🟢 UTILE  
**Effort** : Élevé  
**Dépendances** : Mission 4 (séparation phases)  
**Fichiers impactés** :
- `backend/api.py` — workflow de validation
- `backend/db/schema.sql` — table pending_actions ou champ dans messages
- `backend/db/database.py` — méthodes validation
- Frontend : composant de confirmation

**Objectif** : Implémenter les gates de validation pour actions critiques.

**Actions nécessitant validation** (selon doc vision) :
- Suppression de fichiers
- Refactor massif
- Modification configuration
- Modification auth
- Modification `.env`
- Migration DB
- Changement architectural majeur

**Approche proposée** :
- Jarvis_maitre détecte (via prompt cloud) qu'une action est critique
- Il marque sa réponse avec un marqueur `[VALIDATION_REQUISE: description]`
- Le backend détecte ce marqueur et crée une entrée "pending_action"
- Le frontend affiche un bouton de validation
- L'utilisateur valide ou refuse
- Si validé, l'action est exécutée

**À faire** :
- [ ] Définir le format des marqueurs de validation
- [ ] Ajouter table ou mécanisme de pending_actions
- [ ] Modifier `send_message` pour détecter les marqueurs
- [ ] Créer endpoint de validation/refus
- [ ] Modifier frontend pour afficher les demandes de validation
- [ ] Tests

**Note** : Cette mission est complexe et peut être simplifiée en v1 en s'appuyant uniquement sur le prompt cloud (Jarvis_maitre demande confirmation dans sa réponse, l'utilisateur répond "oui" ou "non" dans le chat).

**Validation** : Test en mode projet — demander une action critique, vérifier que la validation est requise.

---

### MISSION 8 — Nettoyage fichiers obsolètes

**Priorité** : 🟡 IMPORTANT (à faire après les missions fonctionnelles)  
**Effort** : Faible  
**Dépendances** : Après validation des missions 1-5

**Fichiers à examiner/supprimer** :
- [ ] `frontend/index-old.html` — ancien fichier, remplacé par SPA
- [ ] `frontend/project-old.html` — ancien fichier
- [ ] `frontend/projects-old.html` — ancien fichier
- [ ] `frontend/script-old.js` — ancien fichier
- [ ] `frontend/style-old.css` — ancien fichier
- [ ] `frontend/js/chat-handler.js` — ancien handler non-SPA (utilise getElementById direct)
- [ ] `frontend/js/conversation-manager.js` — ancien manager non-SPA (redirect projects.html)
- [ ] `frontend/js/projects-manager.js` — vérifier si utilisé par la SPA
- [ ] `backend/agents/agent_registry.py` — si encore présent, supprimer (remplacé par agent_factory)

**À faire** :
- [ ] Vérifier chaque fichier : est-il importé/utilisé quelque part ?
- [ ] Supprimer les fichiers confirmés obsolètes
- [ ] Vérifier qu'aucun import cassé ne résulte de la suppression
- [ ] Lancer les tests pour confirmer

**Validation** : Tests passent + application fonctionne.

---

### MISSION 9 — Documentation et clôture

**Priorité** : 🟡 IMPORTANT (dernière étape de chaque mission)  
**Effort** : Faible par mission  
**Dépendances** : Après chaque mission validée

**À faire après chaque mission** :
- [ ] Mettre à jour `docs/reference/AGENT_SYSTEM.md` si agents modifiés
- [ ] Mettre à jour `docs/reference/ARCHITECTURE.md` si structure modifiée
- [ ] Mettre à jour `docs/reference/API_SPECIFICATION_V2.md` si endpoints ajoutés/modifiés
- [ ] Mettre à jour `docs/_meta/CHANGELOG.md` avec l'entrée de la mission
- [ ] Mettre à jour `docs/_meta/INDEX.md` si nouveaux documents
- [ ] Mettre à jour `docs/_meta/IA_CONTEXT.md` si architecture changée

**À faire en fin de chantier** :
- [ ] Archiver ce document → `docs/history/`
- [ ] Vérifier cohérence globale de la documentation
- [ ] MAJ mémoires Cascade si nécessaire

---

## ORDRE D'EXÉCUTION

| # | Mission | Priorité | Effort | Prérequis |
|---|---|---|---|---|
| 1 | Prompt Cloud Jarvis_maitre | 🔴 | Faible | Aucun — **PREMIER** |
| 2 | Paramètres techniques (temperature) | 🔴 | Faible | Aucun |
| 3 | Détection Mode Chat / Projet | 🟡 | Faible | M1 |
| 4 | Séparation Réflexion / Production | 🟡 | Moyen | M1 + M3 |
| 5 | Orchestration simple | 🟡 | Moyen-élevé | M1 + M2 |
| 6 | Système de Mémoire | 🟢 | Élevé | M3 |
| 7 | Validation actions critiques | 🟢 | Élevé | M4 |
| 8 | Nettoyage fichiers obsolètes | 🟡 | Faible | M1-M5 validées |
| 9 | Documentation et clôture | 🟡 | Faible | Après chaque mission |

**Cycle par mission** : Exécution → Tests → Validation Val C. → Documentation → Nettoyage → Mission suivante

---

## NOTES TECHNIQUES TRANSVERSALES

### Points d'injection principaux dans le code

1. **Contexte agent** : `api.py` L200-217 — là où le contexte projet est construit et préfixé au message
2. **Appel Mistral** : `mistral_client.py` L66-77 — `beta.conversations.start()`
3. **Config agents** : `agent_config.py` L6-26 — `AGENT_CONFIGS` dict
4. **Instanciation agents** : `agent_factory.py` L46-57 — switch sur agent_name
5. **Schema DB** : `schema.sql` — toute modification de structure
6. **Frontend state** : `core/state.js` — état global SPA
7. **Frontend mode** : `views/chat-simple.js` L154 (`mode: 'simple'`) et `views/project-detail.js` L177 (`mode: 'project'`)

### Conventions à respecter

- Noms d'agents : `"BASE"` et `"JARVIS_Maître"` (avec accent)
- Rôles messages : uniquement `"user"` et `"assistant"` (jamais `"system"`)
- Session ID = conversation_id (pour traçabilité logs)
- Logs : JSON Lines dans `jarvis_audit.log`
- Tests : pytest, fichiers dans `tests/`
- Documentation : méthodologie reference/work/history/_meta
