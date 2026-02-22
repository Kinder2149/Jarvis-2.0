# Système d'Agents - JARVIS 2.0

**Statut** : REFERENCE  
**Version** : 4.1  
**Date** : 2026-02-13  
**Dernière mise à jour** : Rapport structuré BASE après délégation CODEUR, reprise de projet, prompts v2.3/v1.2/v1.2

---

## 🎯 Vue d'Ensemble

Le système d'agents de JARVIS 2.0 est conçu pour être **évolutif** et **multi-agent**.

**État actuel** : Trois agents opérationnels (BASE, CODEUR, JARVIS_Maître) avec Agent IDs Mistral distincts  
**Architecture** : Factory + Configuration centralisée + Orchestration backend (SimpleOrchestrator)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    agent_config.py                      │
│              (Configuration centralisée)                │
│  AGENT_CONFIGS = {                                      │
│    "BASE":           { env_var, name, role, type... }  │
│    "CODEUR":         { env_var, name, role, type... }  │
│    "JARVIS_Maître":  { env_var, name, role, type... }  │
│  }                                                      │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    agent_factory.py                     │
│                (Instanciation + Cache)                  │
│  get_agent(name) → BaseAgent | JarvisMaitre            │
│  clear_cache() → vide le cache                         │
│  Injection dynamique Agent ID depuis .env              │
└────────────────────────┬────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
┌──────────────────────┐    ┌──────────────────────┐
│   base_agent.py      │    │  jarvis_maitre.py    │
│    (BaseAgent)       │    │  (JarvisMaitre)      │
│                      │    │  extends BaseAgent   │
│  - id                │    │                      │
│  - name              │    │  - orchestration     │
│  - role              │    │    (futur)           │
│  - permissions       │    └──────────────────────┘
│  - state             │
│  - handle(messages)  │
│  - log(action, ...)  │
│                      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  mistral_client.py   │
│   (MistralClient)    │
│                      │
│  - send(messages)    │
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│  jarvis_audit.log    │
│   (JSON Lines)       │
└──────────────────────┘
```

---

## 📦 Composants

### 1. `agent_config.py` - Configuration Centralisée

**Responsabilités** :
- Source unique de vérité pour la configuration des agents
- Mapping agent_name → variable d'environnement + métadonnées
- Lister les agents disponibles avec métadonnées

**Fonctions disponibles** :
```python
def get_agent_config(agent_name: str) -> dict
def list_available_agents() -> list[dict]
```

**Structure de configuration** :
```python
AGENT_CONFIGS = {
    "BASE": {
        "env_var": "JARVIS_BASE_AGENT_ID",
        "name": "BASE",
        "role": "Assistant générique",
        "description": "Agent neutre servant de worker pour tâches génériques.",
        "permissions": ["read", "write"],
        "type": "worker",
        "temperature": 0.7,
        "max_tokens": 4096
    },
    "CODEUR": {
        "env_var": "JARVIS_CODEUR_AGENT_ID",
        "name": "CODEUR",
        "role": "Agent spécialisé code",
        "description": "Agent spécialisé dans l'écriture de code...",
        "permissions": ["read", "write", "code"],
        "type": "worker",
        "temperature": 0.3,
        "max_tokens": 4096
    },
    "JARVIS_Maître": {
        "env_var": "JARVIS_MAITRE_AGENT_ID",
        "name": "JARVIS_Maître",
        "role": "Assistant personnel principal",
        "description": "Assistant IA personnel de Val C. ...",
        "permissions": ["read", "write", "orchestrate"],
        "type": "orchestrator",
        "temperature": 0.3,
        "max_tokens": 4096
    }
}
```

### 2. `agent_factory.py` - Factory avec Cache

**Responsabilités** :
- Instancier les agents selon leur configuration
- Injecter dynamiquement l'Agent ID depuis `.env`
- Gérer le cache des instances (singleton par nom)

**Fonctions disponibles** :
```python
def get_agent(agent_name: str) -> BaseAgent
def clear_cache() -> None
```

**Comportement** :
- Lit la variable d'environnement définie dans `agent_config.py`
- Lève `RuntimeError` si la variable est absente
- Cache l'instance pour réutilisation
- Chaque agent reçoit son propre Agent ID Mistral

### 3. `base_agent.py` - Agent de Base

**Classe** : `BaseAgent`

**Attributs** :
- `id` (str) : Agent ID Mistral (distinct par agent)
- `name` (str) : Nom lisible de l'agent
- `role` (str) : Rôle de l'agent
- `description` (str) : Description de l'agent
- `permissions` (list[str]) : Permissions de l'agent
- `temperature` (float|None) : Température (métadonnée locale, configurée côté Mistral Cloud)
- `max_tokens` (int|None) : Max tokens (métadonnée locale, configurée côté Mistral Cloud)
- `state` (str) : État actuel ("idle", "working", "error")
- `client` (MistralClient) : Client de communication avec Mistral
- `log_file` (Path) : Chemin vers jarvis_audit.log

**Méthodes principales** :
```python
def handle(self, messages: list[dict], session_id: str | None = None) -> str
def log(self, action: str, details: dict, session_id: str | None = None) -> None
```

**Responsabilités** :
- Validation stricte du format des messages
- Délégation à `MistralClient` pour l'exécution
- Journalisation en JSON Lines de toutes les actions
- Gestion des états (idle → working → idle/error)

**Validation des messages** :
- `messages` doit être une liste
- Chaque message doit être un dict
- Chaque message doit avoir `role` in `("user", "assistant")` — `system` rejeté
- Chaque message doit avoir `content` (string non vide)

**Exception** :
- `InvalidRuntimeMessageError` : levée si validation échoue

### 4. `jarvis_maitre.py` - Agent JARVIS_Maître

**Classe** : `JarvisMaitre(BaseAgent)`

Hérite de `BaseAgent` avec :
- Permission `orchestrate` supplémentaire
- Rôle "Assistant personnel principal"
- Pas de `system_prompt` local (personnalisation côté Mistral Cloud)

---

## 🔑 Principe : Personnalisation Cloud

Les instructions et paramètres de chaque agent sont configurés **côté Mistral** (plateforme Mistral AI).

- Le backend est **neutre** : il ne contient aucun `system_prompt`
- Chaque agent a son propre **Agent ID Mistral** pointant vers des instructions distinctes
- La différenciation comportementale est gérée **côté cloud**
- `temperature` et `max_tokens` sont configurés côté cloud (l'API Mistral interdit `completion_args` avec un `agent_id`)
- Les valeurs dans `agent_config.py` servent de **métadonnées locales** (documentation, logs)

**Configuration actuelle Mistral Cloud** :
- **JARVIS_Maître** (v2.3) : temperature 0.3, max_tokens 4096, instructions complètes (identité, méthodologie, modes, marqueurs de délégation, reprise de projet avec rapport BASE)
- **CODEUR** (v1.2) : temperature 0.3, max_tokens 4096, instructions spécialisées code (format de réponse obligatoire, reprise de code existant, imports absolus)
- **BASE** (v1.2) : temperature 0.7, max_tokens 4096, instructions légères (worker générique, vérification de complétude, rapport de code structuré)

---

## 🔄 Flux de Traitement

### Flux : Envoi de Message

```
1. api.py reçoit POST /api/conversations/{id}/messages
   ↓
2. Récupération conversation + historique depuis SQLite
   ↓
3. agent_factory.get_agent(conversation.agent_id)
   ↓
4. agent.handle(messages, session_id)
   │  ├─ État: idle → working
   │  ├─ Log: handle_request (JSON Lines)
   │  ├─ Validation des messages (rôles user/assistant uniquement)
   │  ├─ mistral_client.send(validated_messages)
   │  ├─ Log: handle_response (JSON Lines)
   │  └─ État: working → idle
   ↓
5. Sauvegarde message user + réponse assistant en DB
   ↓
6. Retour JSON {response, conversation_id, agent_id}
```

### Flux : Journalisation (JSON Lines)

```
Chaque action agent génère une entrée dans jarvis_audit.log :
{
  "timestamp": "2026-02-12T12:00:00.123456",
  "agent_id": "ag_019ba8ca...",
  "agent_name": "BASE",
  "session_id": "uuid",
  "action": "handle_request",
  "state": "working",
  "details": {"message_count": 3, "last_user_message": "..."}
}
```

---

## 🌐 Endpoint API

### GET /agents
**Description** : Liste tous les agents disponibles avec métadonnées

**Response** :
```json
{
  "agents": [
    {
      "id": "BASE",
      "name": "BASE",
      "role": "Assistant générique",
      "description": "Agent neutre servant de worker pour tâches génériques."
    },
    {
      "id": "CODEUR",
      "name": "CODEUR",
      "role": "Agent spécialisé code",
      "description": "Agent spécialisé dans l'écriture de code..."
    },
    {
      "id": "JARVIS_Maître",
      "name": "JARVIS_Maître",
      "role": "Assistant personnel principal",
      "description": "Assistant IA personnel de Val C. ..."
    }
  ]
}
```

Voir `API_SPECIFICATION_V2.md` pour la spécification complète des endpoints.

---

## 🔮 Évolution Multi-Agent

### Agents Spécialisés Prévus

```
agent_config.py / agent_factory.py
├── BASE (worker, générique, vérification) ✅
├── CODEUR (worker, spécialiste code) ✅
├── JARVIS_Maître (orchestrator) ✅
├── ARCHITECTE (conception, plans)
├── AUDITEUR (audit technique)
├── PLANIFICATEUR (séquençage)
├── EXÉCUTANT (implémentation)
├── VALIDATEUR (conformité)
├── DOCUMENTALISTE (documentation)
├── CHERCHEUR (recherche)
└── TESTEUR (tests)
```

### Architecture Orchestrateur/Worker

```
User Request → JARVIS_Maître (orchestrator)
                  ├─→ CODEUR (worker code) ✅
                  ├─→ BASE (worker vérification) ✅
                  ├─→ Futur Worker N
              ← Agrégation résultats → Réponse User
```

### Fonctionnalités Implémentées

1. **Orchestration backend** : `SimpleOrchestrator` avec détection de marqueurs et délégation automatique ✅
2. **Écriture fichiers** : `file_writer` parse les blocs code et écrit sur le disque ✅
3. **Boucle de vérification** : BASE vérifie la complétude, relance CODEUR si incomplet ✅
4. **Rapport structuré** : BASE lit les fichiers produits et génère un rapport (classes, fonctions, signatures, imports, routes) envoyé à Jarvis_maitre ✅

### Fonctionnalités Futures

1. **Routage intelligent** : Détection automatique de l'agent à solliciter
2. **Workflow engine** : Séquençage multi-étapes avec dépendances
3. **Agents Spécialisés** : Chaque agent = 1 Agent ID Mistral + instructions cloud dédiées

---

## 🛡️ Gestion des Erreurs

### Erreurs de Validation (`InvalidRuntimeMessageError`)

**Causes** :
- `messages` n'est pas une liste
- Un message n'est pas un dict
- `role` invalide (ni "user" ni "assistant")
- `content` vide ou non-string

**Gestion** :
- Exception levée par `base_agent.handle()`
- Capturée dans `api.py`
- Retournée comme HTTP 400

### Erreurs Mistral

**Causes** :
- API Mistral indisponible (`MistralUpstreamError`)
- Format de réponse inattendu (`MistralResponseFormatError`)

**Gestion** :
- Exceptions levées par `mistral_client.send()`
- Capturées dans `api.py`
- Retournées comme HTTP 502/503

---

## 🧪 Tests

### Tests Unitaires (193/193 passent)

#### `test_base_agent.py` (19 tests)
- Validation messages valides/invalides
- Gestion d'état (idle, working, error)
- Journalisation (request, response, error, session_id)

#### `test_jarvis_maitre.py` (26 tests)
- Contrat JARVIS_Maître (héritage, nom, rôle, permissions, description)
- Non-régression (handle, validation, état, logs)
- Endpoint GET /agents (liste, métadonnées)

#### `test_codeur.py` (14 tests)
- Configuration CODEUR (nom, rôle, permissions, type, temperature)
- Factory (instanciation, cache, Agent ID)

#### `test_orchestration.py` (57 tests)
- Détection marqueurs (CODEUR, BASE, multiples, partiels)
- Exécution délégation (succès, échec, session_id)
- Vérification complétude (complet, incomplet, fallback)
- Boucle de complétion (relance CODEUR, skip si complet)
- Followup et process_response (flux complet, max 1/agent, fallback)
- Lecture fichiers projet (_read_project_files)
- Rapport structuré BASE (_build_code_report)
- Followup enrichi avec rapport (inclusion, non-régression)

#### `test_file_writer.py` (29 tests)
- Parse blocs code (header, bold, backtick, inline, multiples)
- Nettoyage artefacts markdown (_clean_content)
- Validation chemins (sécurité, extensions)
- Écriture fichiers (création, sous-dossiers, écrasement)

---

## 📋 Checklist d'Ajout d'un Nouvel Agent

1. [ ] Créer l'agent côté Mistral (plateforme) → obtenir un Agent ID
2. [ ] Ajouter la variable `JARVIS_<NOM>_AGENT_ID` dans `.env` et `.env.example`
3. [ ] Ajouter l'entrée dans `AGENT_CONFIGS` (`agent_config.py`)
4. [ ] Si comportement spécifique : créer une classe héritant de `BaseAgent`
5. [ ] Ajouter le branchement dans `agent_factory.py` (`get_agent()`)
6. [ ] Tester l'instanciation et le comportement
7. [ ] Vérifier les logs JSON Lines (agent_id distinct)
8. [ ] Documenter le nouvel agent dans ce fichier
9. [ ] Mettre à jour `INDEX.md` et `CHANGELOG.md`

---

## ⚠️ Limitations Actuelles (Usage Local/Personnel)

- **Rotation logs simple** : jarvis_audit.log renommé en .log.old au-delà de 5 Mo
- **Pas de métriques** : aucun tracking d'utilisation par agent
- **Fallback basique** : si un agent échoue, retour à la réponse initiale de Jarvis_maitre
- **Cache singleton** : modification `.env` nécessite redémarrage serveur
- **Branchement if/elif** dans factory : acceptable < 5 agents, à refactorer au-delà
- **Pas de health check Agent ID** : validité vérifiée uniquement au premier appel Mistral

---

## 🎯 Bonnes Pratiques

### Conception d'un Agent
1. **Rôle clair** : définir précisément le périmètre
2. **Instructions cloud** : configurer le comportement côté Mistral, pas dans le backend
3. **Validation stricte** : ne jamais faire confiance aux inputs
4. **Gestion d'erreur** : toujours prévoir les cas d'échec
5. **Documentation** : chaque agent doit être documenté

### Utilisation de la Factory
1. **Toujours passer par `get_agent()`** : ne jamais instancier directement
2. **Configuration dans `agent_config.py`** : source unique de vérité
3. **Variables d'environnement** : 1 variable `.env` par Agent ID
