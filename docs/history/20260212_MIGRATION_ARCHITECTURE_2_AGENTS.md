# Migration Architecture 2 Agents - JARVIS 2.0

**Date** : 2026-02-12  
**Statut** : WORK - PLAN DE MIGRATION OFFICIEL (PHASE 1 EN COURS)  
**Objectif** : Migrer de 1 Agent ID Mistral partagé vers 2 Agents Cloud distincts

---

## 🎯 OBJECTIF DE LA MIGRATION

Passer de l'architecture actuelle (1 Agent ID Mistral partagé entre BASE et JARVIS_Maître) vers une architecture avec :

- **2 Agents Cloud Mistral distincts** (chacun avec son propre Agent ID)
- **Sélection dynamique** de l'agent selon le contexte
- **Personnalisation exclusivement côté Mistral** (pas de system prompts locaux)
- **Backend neutre** (pas de logique métier liée aux agents)
- **Architecture prête pour OS IA** (orchestrateur + workers)

---

## 1️⃣ AUDIT RÉSUMÉ FINAL

### État Actuel

**Configuration** :
- 1 seul Agent ID Mistral : `JARVIS_BASE_AGENT_ID`
- Partagé entre BASE et JARVIS_Maître
- System prompts définis localement mais **jamais envoyés à Mistral**
- Différenciation purement locale (métadonnées)

**Fichiers Concernés** :
- `backend/agents/agent_registry.py` : Factory avec Agent ID unique (ligne 35)
- `backend/agents/base_agent.py` : Stocke system_prompt inutilisé (ligne 39)
- `backend/agents/jarvis_maitre.py` : System prompt hardcodé (lignes 29-41)
- `backend/ia/mistral_client.py` : Client avec agent_id fixe (ligne 58)

### Points Problématiques

1. **Agent ID Unique Partagé**
   - Impossible de différencier BASE et JARVIS_Maître côté Mistral
   - Les deux agents appellent le même Agent ID cloud

2. **System Prompts Locaux Inutilisés**
   - Définis dans le code mais jamais envoyés à l'API
   - Redondance et confusion sur le comportement réel
   - Source de vérité dupliquée (local + Mistral)

3. **Configuration Rigide**
   - Variable `.env` unique
   - Lecture centralisée (ligne 35)
   - Impossible d'injecter plusieurs IDs sans refonte

4. **Validation Incohérente**
   - Accepte `role="system"` mais Mistral Agent API le refuse
   - Risque d'erreur runtime

### Contraintes Techniques

- **Dépendances fortes** : Agent ID hardcodé dans agent_registry.py
- **Couplage** : MistralClient créé dans BaseAgent.__init__
- **Cache global** : Instances agents partagées (singleton par nom)
- **Mémoire locale** : SQLite (pas d'impact sur migration)

---

## 2️⃣ ARCHITECTURE CIBLE DÉTAILLÉE

### Configuration .env Cible

```bash
# Clé API Mistral
MISTRAL_API_KEY=***

# Modèle (optionnel)
MISTRAL_MODEL=mistral-small-latest

# Agent IDs distincts
JARVIS_BASE_AGENT_ID=ag_xxx...
JARVIS_MAITRE_AGENT_ID=ag_yyy...

# Forcer Agent API
USE_MISTRAL_AGENT_API=1
```

**Important** : Les deux Agent IDs existent déjà côté Mistral avec leurs propres instructions.

### Structure Fichiers Cible

```
backend/
├── agents/
│   ├── base_agent.py           # Classe de base (nettoyée)
│   ├── agent_factory.py        # Factory dynamique (refactor registry)
│   ├── agent_config.py         # Configuration agents
│   └── jarvis_maitre.py        # Classe héritée (nettoyée)
├── ia/
│   └── mistral_client.py       # Client Mistral (inchangé)
└── api.py                      # Routes API (validation corrigée)
```

### Schéma Architecture Cible

```
┌─────────────────────────────────────────────────────────────┐
│                         .env                                │
│  JARVIS_BASE_AGENT_ID=ag_xxx                               │
│  JARVIS_MAITRE_AGENT_ID=ag_yyy                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              agent_config.py                                │
│  AGENT_CONFIGS = {                                          │
│    "BASE": {                                                │
│      "env_var": "JARVIS_BASE_AGENT_ID",                     │
│      "type": "worker",                                      │
│      "role": "Assistant générique"                          │
│    },                                                       │
│    "JARVIS_Maître": {                                       │
│      "env_var": "JARVIS_MAITRE_AGENT_ID",                   │
│      "type": "orchestrator",                                │
│      "role": "Assistant personnel principal"                │
│    }                                                        │
│  }                                                          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              agent_factory.py                               │
│  def get_agent(agent_name: str):                            │
│    config = AGENT_CONFIGS[agent_name]                       │
│    agent_id = os.environ.get(config["env_var"])            │
│    return BaseAgent(agent_id=agent_id, ...)                │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                  base_agent.py                              │
│  def __init__(self, agent_id, name, ...):                   │
│    self.client = MistralClient(agent_id)                    │
│    # PAS de system_prompt                                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              mistral_client.py                              │
│  client.beta.conversations.start(                          │
│      agent_id=self.agent_id,  ← ID DISTINCT PAR AGENT      │
│      inputs=messages                                        │
│  )                                                          │
└─────────────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                   Mistral Cloud                             │
│  Agent BASE: ag_xxx (instructions côté Mistral)            │
│  Agent JARVIS_Maître: ag_yyy (instructions côté Mistral)   │
└─────────────────────────────────────────────────────────────┘
```

### Responsabilités des Composants

**agent_config.py** (NOUVEAU)
- Définit la configuration de chaque agent
- Mapping agent_name → variable .env
- Type (orchestrator/worker) pour OS IA futur
- Métadonnées (role, description)

**agent_factory.py** (REFACTOR de agent_registry.py)
- Factory pattern pour instanciation agents
- Lecture dynamique de la config
- Récupération Agent ID depuis .env selon config
- Cache des instances

**base_agent.py** (NETTOYÉ)
- Classe de base pour tous les agents
- Validation messages (sans `system`)
- Appel MistralClient
- Logging
- **SUPPRESSION** : system_prompt, logique inutilisée

**jarvis_maitre.py** (NETTOYÉ)
- Classe héritée de BaseAgent
- **SUPPRESSION** : system_prompt hardcodé

**mistral_client.py** (INCHANGÉ)
- Client bas niveau Mistral
- Reçoit agent_id distinct par instance

### Flux d'Appel Complet

```
1. Frontend → POST /api/conversations/{id}/messages
   body: { "content": "..." }
   conversation.agent_id: "JARVIS_Maître"

2. api.py:221 → get_agent("JARVIS_Maître")

3. agent_factory.py:get_agent()
   ├─ config = AGENT_CONFIGS["JARVIS_Maître"]
   ├─ agent_id = os.environ.get("JARVIS_MAITRE_AGENT_ID")
   └─ return BaseAgent(agent_id=agent_id, name="JARVIS_Maître", ...)

4. base_agent.py:__init__()
   └─ self.client = MistralClient(agent_id)

5. base_agent.py:handle(messages)
   ├─ Validation messages
   └─ self.client.send(messages)

6. mistral_client.py:send()
   └─ client.beta.conversations.start(agent_id=self.agent_id, inputs=messages)

7. Mistral Cloud
   └─ Agent ag_yyy (JARVIS_Maître) traite la requête avec ses instructions cloud
```

---

## 3️⃣ SÉQUENCE EXACTE DE MIGRATION

### Phase 1 — Nettoyage

**Objectif** : Supprimer tout code mort et logique inutilisée

#### Fichier : `backend/agents/base_agent.py`

**Lignes à supprimer** :
- Ligne 32 : Paramètre `system_prompt: str` du constructeur
- Ligne 39 : `self.system_prompt = system_prompt`

**Modification** :
```python
# AVANT
def __init__(
    self,
    agent_id: str,
    name: str,
    role: str,
    description: str,
    system_prompt: str,  # ← SUPPRIMER
    permissions: list[str] | None = None,
):
    # ...
    self.system_prompt = system_prompt  # ← SUPPRIMER

# APRÈS
def __init__(
    self,
    agent_id: str,
    name: str,
    role: str,
    description: str,
    permissions: list[str] | None = None,
):
    # ... (sans system_prompt)
```

**Effet attendu** :
- Suppression de la redondance
- Clarification : personnalisation côté Mistral uniquement

#### Fichier : `backend/agents/base_agent.py`

**Lignes à modifier** :
- Lignes 108-111 : Validation messages

**Modification** :
```python
# AVANT
if role not in ("user", "assistant", "system"):
    raise InvalidRuntimeMessageError(...)

# APRÈS
if role not in ("user", "assistant"):
    raise InvalidRuntimeMessageError(
        f"messages[{idx}].role must be 'user' or 'assistant'"
    )
```

**Effet attendu** :
- Cohérence avec Mistral Agent API
- Évite erreurs runtime

#### Fichier : `backend/agents/jarvis_maitre.py`

**Lignes à supprimer** :
- Lignes 29-41 : Paramètre `system_prompt` entier

**Modification** :
```python
# AVANT
super().__init__(
    agent_id=agent_id,
    name="JARVIS_Maître",
    role="Assistant personnel principal",
    description=(...),
    system_prompt=(...),  # ← SUPPRIMER TOUT CE BLOC
    permissions=[...]
)

# APRÈS
super().__init__(
    agent_id=agent_id,
    name="JARVIS_Maître",
    role="Assistant personnel principal",
    description=(...),
    permissions=["read", "write", "orchestrate"]
)
```

**Effet attendu** :
- Suppression source de vérité dupliquée
- Classe allégée

---

### Phase 2 — Refactor Configuration Agents

**Objectif** : Créer configuration centralisée et dynamique

#### Fichier à créer : `backend/agents/agent_config.py`

**Contenu** :
```python
"""
Configuration des agents JARVIS 2.0
Mapping agent_name → variable .env + métadonnées
"""

AGENT_CONFIGS = {
    "BASE": {
        "env_var": "JARVIS_BASE_AGENT_ID",
        "name": "BASE",
        "role": "Assistant générique",
        "description": "Agent neutre servant de worker pour tâches génériques.",
        "permissions": ["read", "write"],
        "type": "worker"
    },
    "JARVIS_Maître": {
        "env_var": "JARVIS_MAITRE_AGENT_ID",
        "name": "JARVIS_Maître",
        "role": "Assistant personnel principal",
        "description": (
            "Assistant IA personnel de Val C. Interface centrale du système JARVIS. "
            "Répond de manière claire et structurée, traduit le technique en langage accessible."
        ),
        "permissions": ["read", "write", "orchestrate"],
        "type": "orchestrator"
    }
}


def get_agent_config(agent_name: str) -> dict:
    """
    Récupère la configuration d'un agent.
    
    Args:
        agent_name: Nom de l'agent ("BASE" ou "JARVIS_Maître")
        
    Returns:
        Configuration de l'agent
        
    Raises:
        ValueError: Si l'agent n'existe pas
    """
    if agent_name not in AGENT_CONFIGS:
        available = ", ".join(AGENT_CONFIGS.keys())
        raise ValueError(
            f"Agent inconnu: {agent_name}. Agents disponibles: {available}"
        )
    return AGENT_CONFIGS[agent_name]


def list_available_agents() -> list[dict]:
    """
    Liste tous les agents disponibles avec leurs métadonnées.
    
    Returns:
        Liste des agents avec id, name, role, description
    """
    return [
        {
            "id": name,
            "name": config["name"],
            "role": config["role"],
            "description": config["description"]
        }
        for name, config in AGENT_CONFIGS.items()
    ]
```

**Responsabilité** :
- Source unique de vérité pour configuration agents
- Mapping dynamique agent → variable .env
- Métadonnées centralisées
- Type (orchestrator/worker) pour OS IA futur

#### Fichier à créer : `backend/agents/agent_factory.py`

**Contenu** :
```python
"""
Factory pour instanciation des agents JARVIS 2.0
Remplace agent_registry.py avec injection dynamique Agent ID
"""

import os
from backend.agents.base_agent import BaseAgent
from backend.agents.jarvis_maitre import JarvisMaitre
from backend.agents.agent_config import get_agent_config

_AGENTS_CACHE: dict[str, BaseAgent] = {}


def get_agent(agent_name: str) -> BaseAgent:
    """
    Fournit une instance d'agent selon son nom.
    Injection dynamique de l'Agent ID depuis .env selon configuration.
    
    Args:
        agent_name: "BASE" ou "JARVIS_Maître"
        
    Returns:
        Instance de l'agent demandé
        
    Raises:
        ValueError: Si l'agent demandé n'existe pas
        RuntimeError: Si l'Agent ID n'est pas défini dans .env
    """
    global _AGENTS_CACHE
    
    # Retourner depuis cache si existe
    if agent_name in _AGENTS_CACHE:
        return _AGENTS_CACHE[agent_name]
    
    # Récupérer configuration
    config = get_agent_config(agent_name)
    
    # Récupérer Agent ID depuis .env
    agent_id = os.environ.get(config["env_var"])
    if not agent_id:
        raise RuntimeError(
            f"{config['env_var']} manquante dans l'environnement"
        )
    
    # Instancier agent selon type
    if agent_name == "BASE":
        agent = BaseAgent(
            agent_id=agent_id,
            name=config["name"],
            role=config["role"],
            description=config["description"],
            permissions=config["permissions"]
        )
    elif agent_name == "JARVIS_Maître":
        agent = JarvisMaitre(agent_id=agent_id)
    else:
        raise ValueError(f"Agent inconnu: {agent_name}")
    
    # Mettre en cache
    _AGENTS_CACHE[agent_name] = agent
    return agent


def clear_cache():
    """Vide le cache des agents (utile pour tests)"""
    global _AGENTS_CACHE
    _AGENTS_CACHE.clear()
```

**Responsabilité** :
- Factory pattern pour instanciation
- Injection dynamique Agent ID depuis .env
- Cache des instances
- Séparation configuration / instanciation

#### Fichier à supprimer : `backend/agents/agent_registry.py`

**Raison** : Remplacé par `agent_factory.py` + `agent_config.py`

**Action** :
1. Créer `agent_factory.py` et `agent_config.py`
2. Mettre à jour imports dans `backend/api.py`
3. Supprimer `agent_registry.py`

---

### Phase 3 — Injection Dynamique Agent ID

**Objectif** : Supprimer Agent ID partagé, injection dynamique par agent

#### Fichier : `backend/api.py`

**Ligne à modifier** :
- Ligne 3 : Import

**Modification** :
```python
# AVANT
from backend.agents.agent_registry import get_agent, list_available_agents

# APRÈS
from backend.agents.agent_factory import get_agent
from backend.agents.agent_config import list_available_agents
```

**Effet attendu** :
- Utilisation nouvelle factory
- Injection dynamique Agent ID

#### Fichier : `backend/agents/jarvis_maitre.py`

**Modification constructeur** :
```python
# AVANT
def __init__(self, agent_id: str):
    super().__init__(
        agent_id=agent_id,
        name="JARVIS_Maître",
        role="Assistant personnel principal",
        description=(...),
        system_prompt=(...),
        permissions=[...]
    )

# APRÈS
def __init__(self, agent_id: str):
    from backend.agents.agent_config import get_agent_config
    config = get_agent_config("JARVIS_Maître")
    
    super().__init__(
        agent_id=agent_id,
        name=config["name"],
        role=config["role"],
        description=config["description"],
        permissions=config["permissions"]
    )
```

**Effet attendu** :
- Métadonnées depuis config centralisée
- Pas de duplication

---

### Phase 4 — Validation et Cohérence API

**Objectif** : Vérifier cohérence endpoints et validation

#### Fichier : `backend/db/schema.sql`

**Ligne à vérifier** :
- Ligne 28 : Validation rôle messages

**Modification** :
```sql
-- AVANT
role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),

-- APRÈS
role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
```

**Effet attendu** :
- Cohérence DB avec Mistral Agent API
- Évite insertion messages system invalides

#### Fichier : `backend/api.py`

**Ligne à vérifier** :
- Lignes 213-216 : Injection contexte projet

**Vérification** :
- Le contexte projet est préfixé au message user (OK)
- Pas de message system injecté (OK)

**Action** : Aucune modification nécessaire

---

### Phase 5 — Préparation Orchestrateur/Worker

**Objectif** : Préparer architecture pour OS IA futur

#### Fichier : `backend/agents/agent_config.py`

**Déjà implémenté** :
```python
"type": "orchestrator"  # JARVIS_Maître
"type": "worker"        # BASE
```

**Utilisation future** :
- JARVIS_Maître : Reçoit requête utilisateur, décide quel worker appeler
- BASE : Exécute tâches déléguées par orchestrateur

**Architecture OS IA Cible** :
```
User Request
    ↓
JARVIS_Maître (orchestrator)
    ├─ Analyse requête
    ├─ Décide action
    └─ Délègue à worker(s)
         ↓
    BASE (worker)
         ├─ Exécute tâche
         └─ Retourne résultat
              ↓
         JARVIS_Maître
              └─ Synthétise et répond à l'utilisateur
```

**Préparation** :
- Champ `type` dans config
- Permission `orchestrate` pour JARVIS_Maître
- Architecture modulaire prête à extension

---

## 4️⃣ LISTE EXACTE DES FICHIERS À MODIFIER

### `backend/agents/base_agent.py`

**Pourquoi** : Supprimer system_prompt inutilisé, corriger validation

**Modifications** :
1. Supprimer paramètre `system_prompt` du constructeur (ligne 32)
2. Supprimer `self.system_prompt = system_prompt` (ligne 39)
3. Modifier validation messages : retirer `"system"` (ligne 108)

**Impact** :
- Classe allégée
- Cohérence avec Mistral Agent API
- Clarification source de vérité

### `backend/agents/jarvis_maitre.py`

**Pourquoi** : Supprimer system_prompt, utiliser config centralisée

**Modifications** :
1. Supprimer paramètre `system_prompt` de `super().__init__()` (lignes 29-41)
2. Importer et utiliser `get_agent_config()` pour métadonnées

**Impact** :
- Suppression duplication
- Métadonnées centralisées

### `backend/api.py`

**Pourquoi** : Utiliser nouvelle factory

**Modifications** :
1. Modifier import ligne 3 :
   ```python
   from backend.agents.agent_factory import get_agent
   from backend.agents.agent_config import list_available_agents
   ```

**Impact** :
- Injection dynamique Agent ID
- Utilisation config centralisée

### `backend/db/schema.sql`

**Pourquoi** : Cohérence validation avec Mistral Agent API

**Modifications** :
1. Modifier ligne 28 :
   ```sql
   role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
   ```

**Impact** :
- Évite insertion messages system invalides
- Cohérence DB/API

---

## 5️⃣ LISTE DES FICHIERS À CRÉER

### `backend/agents/agent_config.py`

**Responsabilité** :
- Configuration centralisée des agents
- Mapping agent_name → variable .env
- Métadonnées (name, role, description, permissions)
- Type (orchestrator/worker) pour OS IA

**Contenu** :
- Dictionnaire `AGENT_CONFIGS`
- Fonction `get_agent_config(agent_name)`
- Fonction `list_available_agents()`

### `backend/agents/agent_factory.py`

**Responsabilité** :
- Factory pattern pour instanciation agents
- Injection dynamique Agent ID depuis .env
- Cache des instances
- Remplacement de `agent_registry.py`

**Contenu** :
- Cache global `_AGENTS_CACHE`
- Fonction `get_agent(agent_name)`
- Fonction `clear_cache()`

---

## 6️⃣ LISTE DES SUPPRESSIONS

### Code Mort

**`backend/agents/base_agent.py`** :
- Paramètre `system_prompt` (ligne 32)
- Attribut `self.system_prompt` (ligne 39)

**`backend/agents/jarvis_maitre.py`** :
- Paramètre `system_prompt` de `super().__init__()` (lignes 29-41)

### Fichiers Obsolètes

**`backend/agents/agent_registry.py`** :
- Fichier entier remplacé par `agent_factory.py` + `agent_config.py`

### Variables Obsolètes

**Aucune** : `JARVIS_BASE_AGENT_ID` reste utilisé, `JARVIS_MAITRE_AGENT_ID` ajouté

### Couplages Supprimés

- Agent ID unique partagé → Injection dynamique par agent
- System prompts locaux → Personnalisation côté Mistral uniquement
- Configuration hardcodée → Configuration centralisée

---

## 7️⃣ PLAN DE TESTS POST-MIGRATION

### Test 1 : Sélection Agent BASE

**Objectif** : Vérifier que BASE utilise son propre Agent ID

**Procédure** :
1. Créer conversation avec `agent_id="BASE"`
2. Envoyer message "Qui es-tu ?"
3. Vérifier logs : `agent_id=ag_xxx` (JARVIS_BASE_AGENT_ID)
4. Vérifier réponse cohérente avec instructions BASE côté Mistral

**Résultat attendu** :
- Agent ID distinct utilisé
- Comportement BASE (générique, neutre)

### Test 2 : Sélection Agent JARVIS_Maître

**Objectif** : Vérifier que JARVIS_Maître utilise son propre Agent ID

**Procédure** :
1. Créer conversation avec `agent_id="JARVIS_Maître"`
2. Envoyer message "Qui es-tu ?"
3. Vérifier logs : `agent_id=ag_yyy` (JARVIS_MAITRE_AGENT_ID)
4. Vérifier réponse cohérente avec instructions JARVIS_Maître côté Mistral

**Résultat attendu** :
- Agent ID distinct utilisé
- Comportement JARVIS_Maître (personnalisé, français, méthodologie)

### Test 3 : Vérification Mémoire

**Objectif** : Vérifier isolation des conversations par agent

**Procédure** :
1. Créer conversation BASE, envoyer "Rappelle-toi : X"
2. Créer conversation JARVIS_Maître, envoyer "Que sais-tu de X ?"
3. Vérifier que JARVIS_Maître ne connaît pas X

**Résultat attendu** :
- Mémoire isolée par conversation
- Pas de fuite entre agents

### Test 4 : Absence de Mélange

**Objectif** : Vérifier qu'aucun agent n'utilise l'Agent ID de l'autre

**Procédure** :
1. Activer logs détaillés
2. Créer conversations BASE et JARVIS_Maître
3. Envoyer messages dans chaque conversation
4. Vérifier logs : Agent ID correct pour chaque appel

**Résultat attendu** :
- BASE → toujours `ag_xxx`
- JARVIS_Maître → toujours `ag_yyy`

### Test 5 : Isolation Agent ID

**Objectif** : Vérifier que les Agent IDs sont bien distincts

**Procédure** :
1. Lire `.env` : vérifier `JARVIS_BASE_AGENT_ID ≠ JARVIS_MAITRE_AGENT_ID`
2. Instancier les deux agents
3. Vérifier `base_agent.client.agent_id ≠ jarvis_maitre.client.agent_id`

**Résultat attendu** :
- Deux Agent IDs distincts
- Pas de partage

### Test 6 : Validation Messages

**Objectif** : Vérifier que messages `system` sont rejetés

**Procédure** :
1. Tenter d'envoyer message avec `role="system"`
2. Vérifier erreur `InvalidRuntimeMessageError`

**Résultat attendu** :
- Erreur levée
- Message non envoyé à Mistral

---

## 8️⃣ POINTS DE VIGILANCE

### Casse des Variables .env

**Risque** : Typo dans nom variable

**Vigilance** :
- `JARVIS_BASE_AGENT_ID` (pas `JARVIS_BASE_AGENTID`)
- `JARVIS_MAITRE_AGENT_ID` (pas `JARVIS_MASTER_AGENT_ID`)
- Respecter casse exacte

**Vérification** :
```bash
# Vérifier .env
grep "JARVIS_.*_AGENT_ID" .env
```

### Singleton Caché

**Risque** : Cache agents non vidé entre tests

**Vigilance** :
- Cache global `_AGENTS_CACHE` dans `agent_factory.py`
- Instances réutilisées (singleton par nom)

**Solution** :
- Fonction `clear_cache()` pour tests
- Redémarrer serveur entre tests si nécessaire

### Cache Agents

**Risque** : Modification .env non prise en compte sans redémarrage

**Vigilance** :
- Agent ID lu une seule fois à l'instanciation
- Stocké dans cache

**Solution** :
- Redémarrer serveur après modification .env
- Ou appeler `clear_cache()` en dev

### Collision Mémoire

**Risque** : Mémoire cloud Mistral partagée entre agents

**Vigilance** :
- Si Mistral Agent API a mémoire cloud interne
- Risque de confusion entre BASE et JARVIS_Maître

**Vérification** :
- Tester isolation (Test 3)
- Documenter comportement observé

### Orchestration Future

**Risque** : Architecture non prête pour appels inter-agents

**Vigilance** :
- Actuellement pas d'orchestration implémentée
- Permission `orchestrate` définie mais non vérifiée

**Préparation** :
- Champ `type` dans config
- Architecture modulaire prête

---

## 9️⃣ PRÉPARATION OS IA

### Configuration Type Agent

**Ajouté dans `agent_config.py`** :
```python
"BASE": {
    "type": "worker",
    # ...
},
"JARVIS_Maître": {
    "type": "orchestrator",
    # ...
}
```

### Rôles dans OS IA

**Orchestrator (JARVIS_Maître)** :
- Reçoit requête utilisateur
- Analyse et décompose la tâche
- Décide quel(s) worker(s) appeler
- Agrège résultats
- Répond à l'utilisateur

**Worker (BASE)** :
- Exécute tâches spécifiques
- Retourne résultat structuré
- Pas d'interaction directe utilisateur

### Architecture Cible OS IA

```
┌─────────────────────────────────────────────────────────────┐
│                      User Request                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────┐
│              JARVIS_Maître (Orchestrator)                   │
│  1. Analyse requête                                         │
│  2. Décompose en sous-tâches                                │
│  3. Sélectionne worker(s) approprié(s)                      │
│  4. Délègue tâches                                          │
└────────────┬────────────────────────┬───────────────────────┘
             │                        │
             ↓                        ↓
┌────────────────────┐    ┌────────────────────┐
│  BASE (Worker)     │    │  Futur Worker 2    │
│  Tâche générique   │    │  Tâche spécialisée │
└────────────┬───────┘    └────────────┬───────┘
             │                         │
             └────────────┬────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│              JARVIS_Maître (Orchestrator)                   │
│  5. Agrège résultats                                        │
│  6. Synthétise réponse                                      │
│  7. Répond à l'utilisateur                                  │
└─────────────────────────────────────────────────────────────┘
```

### Évolution Future

**Court Terme** :
- Implémentation routage JARVIS_Maître → BASE
- Vérification permission `orchestrate`

**Moyen Terme** :
- Ajout workers spécialisés (AUDITEUR, EXÉCUTANT, etc.)
- Protocole communication inter-agents

**Long Terme** :
- Orchestration complexe (parallélisation, dépendances)
- Gestion conflits entre agents
- Validation résultats

### Préparation Actuelle

**Déjà en place** :
- ✅ Champ `type` dans configuration
- ✅ Permission `orchestrate` pour JARVIS_Maître
- ✅ Architecture modulaire (factory, config séparée)
- ✅ Agents distincts côté Mistral

**À implémenter plus tard** :
- Logique de routage
- Vérification permissions
- Protocole appels inter-agents

---

## ✅ CHECKLIST FINALE

### Avant Migration

- [ ] Backup base de données `jarvis_data.db`
- [ ] Backup fichiers à modifier
- [ ] Vérifier `.env` contient les 2 Agent IDs
- [ ] Vérifier Agent IDs existent côté Mistral
- [ ] Vérifier instructions configurées côté Mistral

### Pendant Migration

**Phase 1 - Nettoyage** :
- [ ] Supprimer `system_prompt` de `base_agent.py`
- [ ] Modifier validation messages (retirer `system`)
- [ ] Supprimer `system_prompt` de `jarvis_maitre.py`

**Phase 2 - Configuration** :
- [ ] Créer `agent_config.py`
- [ ] Créer `agent_factory.py`
- [ ] Vérifier mapping agent → env_var

**Phase 3 - Injection** :
- [ ] Modifier import dans `api.py`
- [ ] Modifier constructeur `jarvis_maitre.py`
- [ ] Vérifier injection dynamique Agent ID

**Phase 4 - Validation** :
- [ ] Modifier validation `schema.sql`
- [ ] Vérifier cohérence API

**Phase 5 - OS IA** :
- [ ] Vérifier champ `type` dans config
- [ ] Documenter architecture cible

### Après Migration

**Tests** :
- [ ] Test 1 : Sélection BASE
- [ ] Test 2 : Sélection JARVIS_Maître
- [ ] Test 3 : Isolation mémoire
- [ ] Test 4 : Absence mélange
- [ ] Test 5 : Isolation Agent ID
- [ ] Test 6 : Validation messages

**Vérifications** :
- [ ] Logs : Agent ID distinct par agent
- [ ] Comportements distincts observés
- [ ] Pas d'erreur runtime
- [ ] Conversations isolées

**Nettoyage** :
- [ ] Supprimer `agent_registry.py`
- [ ] Supprimer backups si tests OK
- [ ] Mettre à jour documentation

### Documentation

- [ ] Mettre à jour README si nécessaire
- [ ] Archiver ce document dans `docs/history/` après exécution
- [ ] Créer document de référence architecture finale

---

## 📊 TABLEAU RÉCAPITULATIF

| Fichier | Action | Raison | Impact |
|---------|--------|--------|--------|
| `base_agent.py` | Modifier | Supprimer system_prompt, corriger validation | Clarification, cohérence |
| `jarvis_maitre.py` | Modifier | Supprimer system_prompt, utiliser config | Centralisation |
| `api.py` | Modifier | Changer imports | Utilisation factory |
| `schema.sql` | Modifier | Validation rôle messages | Cohérence DB/API |
| `agent_config.py` | Créer | Configuration centralisée | Source unique vérité |
| `agent_factory.py` | Créer | Factory avec injection dynamique | Séparation concerns |
| `agent_registry.py` | Supprimer | Remplacé par factory + config | Simplification |

---

## 🎯 RÉSUMÉ EXÉCUTIF

**Objectif** : Migrer de 1 Agent ID partagé vers 2 Agents Cloud distincts

**Bénéfices** :
- ✅ Différenciation réelle BASE vs JARVIS_Maître
- ✅ Personnalisation côté Mistral (source unique vérité)
- ✅ Backend neutre (pas de logique métier agents)
- ✅ Architecture prête pour OS IA (orchestrator/worker)
- ✅ Configuration dynamique et extensible

**Complexité** : Moyenne (refactoring structurel, pas de changement fonctionnel majeur)

**Durée estimée** : 2-3 heures (implémentation + tests)

**Risques** : Faibles (architecture préparée, tests définis)

**Prochaine étape** : Exécution phase par phase avec validation à chaque étape

---

**Document prêt à exécution immédiate.**
