# Prompt à lancer sur une conversation JARVIS_Maître

> **Objectif** : Obtenir un plan complet pour implémenter la Knowledge Base (Librairie) avec Function Calling dans JARVIS 2.0.
> **Comment l'utiliser** : Copier-coller le prompt ci-dessous dans une conversation avec JARVIS_Maître en mode projet (projet JARVIS 2.0).

---

## Le prompt

```
Je veux implémenter un système de Knowledge Base (Librairie) dans JARVIS 2.0. Voici le contexte complet :

## ÉTAT ACTUEL

### Architecture
- Backend : FastAPI + SQLite (aiosqlite) + Mistral AI Agent API
- Frontend : HTML/CSS/JS vanilla, SPA hash-based
- 3 agents : BASE (worker), CODEUR (code), JARVIS_Maître (orchestrateur)
- Orchestration : marqueurs [DEMANDE_CODE_CODEUR:] et [DEMANDE_VALIDATION_BASE:]
- Agents configurés sur Mistral AI Studio avec : instructions, temperature, max_tokens, format réponse, et "fonctionnalité" (function calling, actuellement vide)

### Ce qui existe déjà
- Une page frontend "Librairie" (#/library) avec des données statiques en JS
- 4 catégories : Librairies & Frameworks, Méthodologies, Prompts & Templates, Données personnelles
- Chaque item a : id, name, icon, description, tags, agents (liste d'agents concernés), content (texte)
- Modal de prévisualisation du contenu
- Filtres par catégorie

## CE QUE JE VEUX

### 1. Backend — Stockage et API de la Knowledge Base
- Les documents de la librairie doivent être stockés de manière persistante (pas en dur dans le JS)
- CRUD complet : ajouter, modifier, supprimer des documents depuis le frontend
- Organisation par catégories (librairies, méthodologies, prompts, personnel)
- Chaque document a : id, category, name, description, content, tags[], agents[], created_at, updated_at
- API REST : GET /api/library, GET /api/library/{id}, POST /api/library, PUT /api/library/{id}, DELETE /api/library/{id}
- Filtrage : GET /api/library?category=X&agent=Y&tag=Z&search=Q

### 2. Function Calling — Intégration avec les agents Mistral
- Configurer des functions sur Mistral AI Studio pour chaque agent
- Côté backend : intercepter les tool_calls dans les réponses Mistral, exécuter la fonction, renvoyer le résultat
- Functions prévues :
  * get_library_document(name, category) — récupère un document de la librairie
  * get_library_list(category, agent) — liste les documents disponibles
  * get_project_file(file_path) — lit un fichier du projet en cours
  * get_project_structure(max_depth) — arborescence du projet
- Modifier mistral_client.py pour gérer le cycle : appel → tool_call → exécution → renvoi résultat → réponse finale

### 3. Frontend — Évolution de la page Librairie
- Remplacer les données statiques par des appels API
- Ajouter un formulaire de création/édition de document
- Bouton supprimer sur chaque item
- Éditeur de contenu (textarea markdown)
- Indicateur visuel des agents qui ont accès à chaque document

## CONTRAINTES
- Pas de RAG pour l'instant (volume trop faible)
- Stockage : SQLite (nouvelle table) OU fichiers JSON/Markdown dans un dossier dédié — à toi de recommander
- Gratuit : pas de service externe payant
- Respecter l'architecture existante (backend/services/, backend/api.py, etc.)
- Tests pytest pour chaque nouveau module

## CE QUE J'ATTENDS DE TOI
1. Fais un AUDIT de l'architecture actuelle par rapport à ce besoin
2. Propose un PLAN détaillé en étapes ordonnées (fichiers à créer/modifier, dépendances)
3. Pour le function calling : détaille exactement quoi configurer sur Mistral Studio (JSON des functions par agent) ET quoi modifier côté backend
4. Recommande le format de stockage (SQLite vs fichiers) avec justification
5. Estime la complexité de chaque étape
6. N'exécute RIEN — je veux valider le plan d'abord
```

---

## Notes d'utilisation

- Ce prompt est conçu pour le **mode projet** (avec le projet JARVIS 2.0 sélectionné)
- JARVIS_Maître suivra sa méthodologie Audit → Plan → Validation
- Il ne doit PAS exécuter — seulement proposer un plan
- Une fois le plan validé, on pourra lancer l'exécution étape par étape
