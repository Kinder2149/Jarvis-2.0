# Templates de Code JARVIS 2.0

Ce dossier contient des templates de code de référence pour les agents JARVIS.

## Objectif

Fournir des exemples de code bien structurés que les agents peuvent consulter via la **Document Library** de Mistral AI Studio pour améliorer la qualité du code généré.

## Templates Disponibles

### 1. `template_calculator.py`
**Description** : Module de calcul avec opérations de base  
**Contenu** :
- Classe `Calculator` avec méthodes statiques
- Gestion d'erreurs (ZeroDivisionError)
- Interface CLI complète
- Docstrings et type hints

**Cas d'usage** : Projets nécessitant des calculs mathématiques simples

---

### 2. `template_todo.py`
**Description** : Gestionnaire de tâches TODO complet  
**Contenu** :
- Classe `Task` avec sérialisation JSON
- Classe `TodoStorage` pour persistance
- Classe `TodoManager` pour logique métier
- Interface CLI avec toutes les opérations CRUD

**Cas d'usage** : Applications de gestion de tâches, listes, notes

---

### 3. `template_fastapi_miniblog.py`
**Description** : API REST complète avec FastAPI  
**Contenu** :
- Modèles Pydantic (ArticleBase, ArticleCreate, ArticleUpdate, Article)
- Endpoints CRUD complets (GET, POST, PUT, DELETE)
- Gestion d'erreurs HTTP
- Documentation OpenAPI automatique

**Cas d'usage** : APIs REST, backends web, microservices

---

### 4. `template_pytest_tests.py`
**Description** : Structure de tests pytest standard  
**Contenu** :
- Fixtures communes (sample_data, temp_file)
- Tests paramétrés
- Tests d'exceptions
- Tests de classes
- Tests avec setup/teardown
- Marqueurs pytest (skip, xfail)

**Cas d'usage** : Tout projet nécessitant des tests automatisés

---

## Utilisation

### Pour les Agents JARVIS

Les agents peuvent consulter ces templates via la Document Library :
1. JARVIS_Maître consulte les templates avant de déléguer au CODEUR
2. CODEUR consulte les templates pour s'inspirer de la structure
3. Les templates servent de référence pour le style de code attendu

### Pour les Développeurs

Ces templates peuvent être copiés et adaptés pour créer de nouveaux projets :

```bash
# Copier un template
cp templates/template_calculator.py mon_projet/calculator.py

# Adapter le code selon les besoins
```

## Bonnes Pratiques

### Structure de Code
- ✅ Classes bien organisées avec responsabilités claires
- ✅ Docstrings pour toutes les fonctions/classes publiques
- ✅ Type hints pour améliorer la lisibilité
- ✅ Gestion d'erreurs appropriée

### Style
- ✅ PEP 8 respecté
- ✅ Noms de variables explicites
- ✅ Commentaires uniquement quand nécessaire
- ✅ Imports organisés (stdlib → third-party → local)

### Tests
- ✅ Tests unitaires pour chaque fonction
- ✅ Tests d'intégration pour les workflows complets
- ✅ Fixtures pour éviter la duplication
- ✅ Tests paramétrés pour les cas multiples

## Ajout de Nouveaux Templates

Pour ajouter un nouveau template :

1. Créer le fichier `template_nom.py`
2. Suivre la structure des templates existants
3. Ajouter des docstrings complètes
4. Inclure des exemples d'utilisation
5. Mettre à jour ce README

## Upload sur Mistral AI Studio

### Étapes

1. Aller sur https://console.mistral.ai/
2. Cliquer sur l'onglet **"Fichiers"**
3. Uploader chaque template :
   - `template_calculator.py`
   - `template_todo.py`
   - `template_fastapi_miniblog.py`
   - `template_pytest_tests.py`
4. Noter les IDs des fichiers uploadés
5. Activer l'outil **"Document Library"** pour les agents :
   - JARVIS_Maître
   - CODEUR

### Configuration des Agents

Après l'upload, mettre à jour les prompts des agents :

**JARVIS_MAITRE.md** :
```
Avant de déléguer au CODEUR, consulte la Document Library pour trouver des templates similaires.
```

**CODEUR.md** :
```
Consulte la Document Library pour trouver des exemples de code similaires avant de produire.
```

## Maintenance

- Mettre à jour les templates quand de nouveaux patterns émergent
- Supprimer les templates obsolètes
- Garder les templates simples et génériques
- Éviter les dépendances externes complexes

## Liens Utiles

- Documentation Mistral AI Studio : https://docs.mistral.ai/agents/tools/built-in/document_library
- Guide Configuration Agents : `../GUIDE_CONFIGURATION_AGENTS.md`
- Document de Travail : `../docs/work/20260214_INTEGRATION_MISTRAL_AI_STUDIO.md`
