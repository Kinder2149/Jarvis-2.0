# Configuration Function Calling — Mistral AI Studio

**Statut** : WORK  
**Date** : 2026-02-13  
**Objectif** : Guide de configuration des functions sur Mistral AI Studio pour les 3 agents

---

## 🎯 Vue d'ensemble

Les agents JARVIS 2.0 utilisent le **Function Calling** de Mistral AI pour accéder à la Knowledge Base et aux fichiers projet.

**Principe** :
1. L'agent détecte qu'il a besoin d'information (doc KB, fichier projet)
2. Il appelle une function configurée sur Mistral Studio
3. Le backend exécute la function via `FunctionExecutor`
4. Le résultat est renvoyé à l'agent
5. L'agent formule sa réponse finale avec l'information

---

## 📋 Configuration par Agent

### 1. BASE (ag_019ba8ca8eaa76288371e13fb962d1ed)

**Functions à configurer** :

```json
[
  {
    "name": "get_library_document",
    "description": "Récupère un document de la Knowledge Base par nom et catégorie optionnelle",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "Nom exact du document à rechercher"
        },
        "category": {
          "type": "string",
          "enum": ["libraries", "methodologies", "prompts", "personal"],
          "description": "Catégorie pour filtrer la recherche (optionnel)"
        }
      },
      "required": ["name"]
    }
  },
  {
    "name": "get_library_list",
    "description": "Liste les documents disponibles dans la Knowledge Base avec filtres optionnels",
    "parameters": {
      "type": "object",
      "properties": {
        "category": {
          "type": "string",
          "enum": ["libraries", "methodologies", "prompts", "personal"],
          "description": "Filtrer par catégorie"
        },
        "agent": {
          "type": "string",
          "description": "Filtrer par agent concerné (ex: CODEUR, BASE, JARVIS_Maître)"
        }
      }
    }
  }
]
```

---

### 2. CODEUR (ag_019c526dafbe718aa5d365f823aadad8)

**Functions à configurer** :

```json
[
  {
    "name": "get_library_document",
    "description": "Récupère un document technique de la Knowledge Base (librairies, conventions de code)",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "Nom du document (ex: FastAPI, Pydantic, Conventions de code)"
        },
        "category": {
          "type": "string",
          "enum": ["libraries", "personal"],
          "description": "Catégorie (libraries pour frameworks, personal pour conventions)"
        }
      },
      "required": ["name"]
    }
  },
  {
    "name": "get_project_file",
    "description": "Lit le contenu d'un fichier du projet en cours pour reprise de code existant",
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {
          "type": "string",
          "description": "Chemin relatif du fichier depuis la racine du projet (ex: backend/models/user.py)"
        }
      },
      "required": ["file_path"]
    }
  }
]
```

**Note CODEUR** : Limité à `libraries` et `personal` car il n'a pas besoin des méthodologies/prompts.

---

### 3. JARVIS_Maître (ag_019c514a04a874159a21135b856a40e3)

**Functions à configurer** :

```json
[
  {
    "name": "get_library_document",
    "description": "Récupère un document de la Knowledge Base (toutes catégories)",
    "parameters": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "Nom du document à rechercher"
        },
        "category": {
          "type": "string",
          "enum": ["libraries", "methodologies", "prompts", "personal"],
          "description": "Catégorie optionnelle pour filtrer"
        }
      },
      "required": ["name"]
    }
  },
  {
    "name": "get_library_list",
    "description": "Liste les documents disponibles dans la Knowledge Base",
    "parameters": {
      "type": "object",
      "properties": {
        "category": {
          "type": "string",
          "enum": ["libraries", "methodologies", "prompts", "personal"]
        },
        "agent": {
          "type": "string",
          "description": "Filtrer par agent (CODEUR, BASE, JARVIS_Maître)"
        }
      }
    }
  },
  {
    "name": "get_project_structure",
    "description": "Récupère l'arborescence du projet en cours pour analyse",
    "parameters": {
      "type": "object",
      "properties": {
        "max_depth": {
          "type": "integer",
          "default": 3,
          "description": "Profondeur maximale de l'arborescence (1-5)"
        }
      }
    }
  }
]
```

---

## 🔧 Procédure de Configuration

### Sur Mistral AI Studio

1. **Accéder à l'agent** : Console → Agents → Sélectionner l'agent
2. **Section "Tools"** : Cliquer sur "Add Tool" ou "Configure Functions"
3. **Ajouter chaque function** : Copier-coller le JSON de chaque function
4. **Valider** : Sauvegarder les modifications
5. **Tester** : Utiliser le playground pour vérifier que l'agent peut appeler les functions

### Vérification

Pour chaque agent, tester dans le playground Mistral :

**BASE** :
```
Peux-tu me donner la référence FastAPI ?
```
→ Doit appeler `get_library_document(name="FastAPI")`

**CODEUR** :
```
Quelles sont les conventions de code Python à suivre ?
```
→ Doit appeler `get_library_document(name="Conventions de code", category="personal")`

**JARVIS_Maître** :
```
Liste-moi tous les documents de méthodologie disponibles
```
→ Doit appeler `get_library_list(category="methodologies")`

---

## 📊 Format des Réponses

Les functions retournent toujours un JSON avec `success` :

### Succès
```json
{
  "success": true,
  "document": {
    "name": "FastAPI",
    "category": "libraries",
    "description": "Framework web Python async...",
    "content": "# FastAPI — Référence rapide\n\n...",
    "tags": ["python", "web", "api"],
    "agents": ["CODEUR", "BASE"]
  }
}
```

### Erreur
```json
{
  "success": false,
  "error": "Document 'NonExistent' not found in Knowledge Base"
}
```

---

## ⚠️ Limitations et Bonnes Pratiques

### Limitations
- **Max 5 itérations** : Le cycle function calling est limité à 5 appels pour éviter les boucles infinies
- **Pas de RAG** : Recherche exacte par nom, pas de recherche sémantique
- **Latence** : Chaque tool_call = 1 appel Mistral supplémentaire (~1-2s)

### Bonnes Pratiques
- **Noms exacts** : Utiliser les noms exacts des documents (sensible à la casse)
- **Filtres** : Utiliser `category` pour accélérer la recherche
- **Cache** : Les documents sont chargés depuis SQLite (rapide)
- **Fallback** : Si function calling échoue, l'agent répond avec ses connaissances de base

---

## 🧪 Tests Backend

Les tests unitaires vérifient le bon fonctionnement :

```bash
# Tests FunctionExecutor
pytest tests/test_library_api.py -v

# Tests complets (à créer)
pytest tests/test_function_calling.py -v
```

---

## 📝 Mise à Jour des Prompts Cloud

Après configuration des functions, mettre à jour les prompts cloud pour informer les agents :

### BASE (docs/prompts_cloud/BASE.md)
Ajouter section :
```markdown
## Functions Disponibles

Tu as accès à ces functions :
- get_library_document(name, category?) : Récupère un document de la KB
- get_library_list(category?, agent?) : Liste les documents disponibles

Utilise-les quand tu as besoin d'information technique précise.
```

### CODEUR (docs/prompts_cloud/CODEUR.md)
Ajouter section :
```markdown
## Functions Disponibles

Tu as accès à ces functions :
- get_library_document(name, category?) : Récupère des références techniques (FastAPI, Pydantic, conventions)
- get_project_file(file_path) : Lit un fichier du projet pour reprise de code

Utilise get_library_document pour consulter les conventions de code avant d'écrire.
Utilise get_project_file pour reprendre du code existant.
```

### JARVIS_Maître (docs/prompts_cloud/JARVIS_MAITRE.md)
Ajouter section :
```markdown
## Functions Disponibles

Tu as accès à ces functions :
- get_library_document(name, category?) : Récupère tout document de la KB
- get_library_list(category?, agent?) : Liste les documents
- get_project_structure(max_depth?) : Arborescence du projet

Utilise-les pour accéder aux méthodologies, templates, et informations projet.
```

---

## ✅ Checklist de Déploiement

- [ ] Configurer functions sur Mistral Studio pour BASE
- [ ] Configurer functions sur Mistral Studio pour CODEUR
- [ ] Configurer functions sur Mistral Studio pour JARVIS_Maître
- [ ] Tester chaque function dans le playground Mistral
- [ ] Mettre à jour les prompts cloud (docs/prompts_cloud/)
- [ ] Exécuter la migration des données (`migrate_library_data()`)
- [ ] Lancer les tests backend
- [ ] Tester end-to-end avec une conversation réelle

---

## 🔗 Références

- Architecture : `docs/reference/AGENT_SYSTEM.md`
- Prompts cloud : `docs/prompts_cloud/`
- Code : `backend/services/function_executor.py`
- Tests : `tests/test_library_api.py`
