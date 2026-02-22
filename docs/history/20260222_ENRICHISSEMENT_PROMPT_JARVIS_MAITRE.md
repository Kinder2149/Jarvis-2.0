# Enrichissement Prompt JARVIS_Maître avec Library - 22 Février 2026

## 🎯 Objectif

Modifier le prompt de **JARVIS_Maître** pour qu'il consulte systématiquement la **Library** et enrichisse ses instructions au **CODEUR** avec le contexte pertinent, améliorant ainsi la qualité du code généré.

---

## ✅ Modifications Effectuées

### **Fichier Modifié**
`config_agents/JARVIS_MAITRE.md`

**Version** : 4.0 → **4.1**  
**Date** : 2026-02-22

---

## 📋 Changements Détaillés

### **1. Titre de la Règle Absolue**

**AVANT** :
```
## RÈGLE ABSOLUE — DÉLÉGATION IMMÉDIATE
```

**APRÈS** :
```
## RÈGLE ABSOLUE — DÉLÉGATION IMMÉDIATE ENRICHIE
```

---

### **2. Étapes de Délégation (Ajout Consultation Library)**

**AVANT** :
```
✅ **TOUJOURS FAIRE** :
1. Écrire IMMÉDIATEMENT le marqueur : [DEMANDE_CODE_CODEUR: instruction complète]
2. Inclure TOUS les fichiers dans UN SEUL marqueur
3. Instruction autonome et complète (le CODEUR n'a pas le contexte)
4. **PAS D'ANALYSE PRÉALABLE** : Délègue AVANT toute réflexion
```

**APRÈS** :
```
✅ **TOUJOURS FAIRE** :
1. **CONSULTER LA LIBRARY** : Utilise `get_library_document()` pour récupérer les patterns pertinents
2. **ENRICHIR L'INSTRUCTION** : Intègre le contexte Library dans le marqueur
3. Écrire le marqueur : [DEMANDE_CODE_CODEUR: instruction complète + contexte Library]
4. Inclure TOUS les fichiers dans UN SEUL marqueur
5. Instruction autonome et complète (le CODEUR n'a pas le contexte)
```

**Impact** : JARVIS_Maître doit maintenant **consulter la Library AVANT** de déléguer.

---

### **3. Section Instructions de Délégation (Enrichie)**

**AVANT** :
```
## INSTRUCTIONS DE DÉLÉGATION AU CODEUR

Ton instruction doit être **COMPLÈTE, CLAIRE, AUTONOME** :

1. **Liste TOUS les fichiers** avec chemins exacts
2. **Pour chaque fichier, spécifie** : Classes, fonctions, imports
3. **Règles contextuelles** : Storage JSON, Pydantic, Frontend
4. **Spécifie** : Dépendances, framework, tests
5. **Si contexte insuffisant** : Demande clarification
```

**APRÈS** :
```
## INSTRUCTIONS DE DÉLÉGATION AU CODEUR (ENRICHIES AVEC LIBRARY)

Ton instruction doit être **COMPLÈTE, CLAIRE, AUTONOME, ENRICHIE** :

### **Étape 1 : Consulter la Library**

Avant de déléguer, **TOUJOURS** consulter la Library pour récupérer les patterns pertinents :

**Exemples de recherche** :
- Projet FastAPI → `get_library_document("FastAPI", "libraries")`
- Tests → `get_library_document("Pytest", "libraries")`
- Validation Pydantic → `get_library_document("Pydantic", "libraries")`
- Conventions code → `get_library_document("Conventions de code", "personal")`
- Stack technique → `get_library_document("Stack technique", "personal")`

**Si tu ne sais pas quel document chercher** :
- `get_library_list("libraries")` → Liste toutes les librairies disponibles
- `get_library_list("methodologies")` → Liste toutes les méthodologies

### **Étape 2 : Construire l'instruction enrichie**

1. **Liste TOUS les fichiers** avec chemins exacts
2. **Pour chaque fichier, spécifie** : Classes, fonctions, imports
3. **AJOUTE LE CONTEXTE LIBRARY** :
   - Copie les patterns pertinents depuis les documents Library
   - Spécifie les conventions à respecter
   - Fournis des exemples de code si disponibles
4. **Règles contextuelles** : Storage JSON, Pydantic, Frontend
5. **Spécifie** : Dépendances, framework, tests
6. **Si contexte insuffisant** : Demande clarification
```

**Impact** : JARVIS_Maître a maintenant un **guide étape par étape** pour consulter la Library et enrichir ses instructions.

---

### **4. Exemples de Délégation (Avant/Après)**

**AJOUT** : 3 nouveaux exemples montrant comment enrichir les instructions avec le contexte Library.

#### **Exemple 1 : Calculatrice (AVEC Library)**
```
[DEMANDE_CODE_CODEUR: Crée les fichiers suivants pour un module de calcul Python :
- src/calculator.py : classe Calculator avec méthodes add(a,b), subtract(a,b), multiply(a,b), divide(a,b) avec gestion division par zéro
- tests/test_calculator.py : tests pytest couvrant tous les cas (succès + erreur division par zéro)

CONTEXTE LIBRARY :
- Validation des types (Library > Conventions de code) :
  * Valider que a et b sont int ou float avec isinstance()
  * Lever ValueError si types invalides avec message explicite
  * Exemple : if not isinstance(x, (int, float)): raise ValueError(f"x doit être un nombre, reçu {type(x).__name__}")

- Tests pytest (Library > Pytest) :
  * Utiliser pytest.raises() pour tester les erreurs
  * Exemple : with pytest.raises(ValueError): function(invalid_input)
  * Tester cas nominaux + cas d'erreur + cas limites (0, None)]
```

#### **Exemple 2 : API FastAPI (AVEC Library)**
```
[DEMANDE_CODE_CODEUR: Crée une API FastAPI pour gérer des utilisateurs :
- src/main.py : app FastAPI avec routes GET /users, POST /users, GET /users/{id}
- src/models.py : modèle Pydantic User avec id, name, email
- tests/test_api.py : tests avec TestClient
- requirements.txt : fastapi, uvicorn, pydantic

CONTEXTE LIBRARY (FastAPI) :
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

@app.get("/users")
async def list_users():
    return users_db

@app.post("/users", response_model=User)
async def create_user(user: User):
    users_db.append(user)
    return user

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]
```

CONTEXTE LIBRARY (Pydantic v2) :
- Utilise .model_dump() au lieu de .dict()
- Utilise .model_validate() au lieu de .parse_obj()
- Utilise .model_copy() au lieu de .copy()]
```

#### **Exemple 3 : Reprise Projet (AVEC Library)**
```
[DEMANDE_CODE_CODEUR: Modifie le projet NoteKeeper.
Code existant à RESPECTER :
- src/models.py : classe Note avec attributs id(str), title(str), content(str), created_at(datetime), tags(list[str]) et méthodes to_dict() -> dict, from_dict(data: dict) -> Note
- src/storage.py : classe NoteStorage avec méthodes save_notes(notes: list[Note]), load_notes() -> list[Note]
Modifications demandées :
- src/note_manager.py : classe NoteManager qui utilise NoteStorage. Méthodes : add_note(title, content, tags) -> Note, get_note(id) -> Note, update_note(id, title, content) -> Note, delete_note(id) -> bool
- tests/test_note_manager.py : tests pytest pour toutes les méthodes

CONTEXTE LIBRARY (Conventions de code) :
- Imports absolus simples (pas de from src.xxx)
- Docstrings pour classes et fonctions publiques
- Type hints sur signatures
- Gestion erreurs avec try/except ou raise approprié]
```

---

## 🔄 Workflow Attendu (Nouveau)

### **Avant (Sans Library)**
```
Utilisateur : "Crée une API FastAPI"
    ↓
JARVIS_Maître : [DEMANDE_CODE_CODEUR: Crée une API FastAPI...]
    ↓
CODEUR : Génère le code (sans contexte spécifique)
    ↓
Qualité variable (peut manquer patterns, conventions)
```

### **Après (Avec Library)**
```
Utilisateur : "Crée une API FastAPI"
    ↓
JARVIS_Maître : get_library_document("FastAPI", "libraries")
    ↓
JARVIS_Maître : get_library_document("Pydantic", "libraries")
    ↓
JARVIS_Maître : get_library_document("Conventions de code", "personal")
    ↓
JARVIS_Maître : [DEMANDE_CODE_CODEUR: Crée une API FastAPI...
                 CONTEXTE LIBRARY (FastAPI) : <patterns>
                 CONTEXTE LIBRARY (Pydantic v2) : <conventions>
                 CONTEXTE LIBRARY (Conventions) : <style>]
    ↓
CODEUR : Génère le code avec TOUS les patterns et conventions
    ↓
✅ Qualité maximale garantie
```

---

## 📊 Bénéfices Attendus

### **1. Qualité du Code Améliorée**
- ✅ CODEUR reçoit les **patterns exacts** depuis la Library
- ✅ Respect automatique des **conventions de code**
- ✅ Utilisation des **bonnes pratiques** documentées

### **2. Cohérence Garantie**
- ✅ Tous les projets suivent les **mêmes patterns**
- ✅ Pas de divergence entre projets
- ✅ Code prévisible et maintenable

### **3. Moins d'Erreurs**
- ✅ Validation des types systématique
- ✅ Gestion d'erreurs conforme
- ✅ Tests complets (cas nominaux + erreurs + limites)

### **4. Moins de Corrections**
- ✅ CODEUR génère du code conforme du premier coup
- ✅ Moins de cycles de correction
- ✅ Gain de temps utilisateur

---

## 🧪 Test Recommandé

### **Commande de Test**
```
Utilisateur : "Crée une calculatrice Python avec tests"
```

### **Comportement Attendu**

**JARVIS_Maître devrait** :
1. Appeler `get_library_document("Pytest", "libraries")`
2. Appeler `get_library_document("Conventions de code", "personal")`
3. Construire un marqueur enrichi :
   ```
   [DEMANDE_CODE_CODEUR: Crée calculator.py et test_calculator.py
   
   CONTEXTE LIBRARY :
   - Validation types avec isinstance()
   - Tests pytest avec pytest.raises()
   - Docstrings pour fonctions publiques
   - Type hints sur signatures]
   ```

**CODEUR devrait** :
- Générer du code avec validation des types
- Tests pytest complets (succès + erreurs + limites)
- Docstrings et type hints

---

## 📝 Notes Importantes

### **Pas de Changement pour CODEUR et VALIDATEUR**
- **CODEUR** : Reste un agent d'exécution pure (pas de functions)
- **VALIDATEUR** : Reste un agent de vérification pure (pas de functions)
- **Architecture maintenue** : Séparation des responsabilités claire

### **JARVIS_Maître = Seul Responsable**
- Consulte la Library
- Enrichit les instructions
- Délègue au CODEUR avec contexte complet

### **Performance**
- **1 appel Library** par type de pattern (FastAPI, Pytest, etc.)
- **1 seul marqueur** avec tout le contexte
- **1 génération CODEUR** (pas de boucle)

---

## 🚀 Prochaines Étapes

### **Phase 1 : Test Manuel** ✅
1. Redémarrer backend (pour recharger prompt)
2. Tester avec "Crée une calculatrice Python"
3. Vérifier que JARVIS_Maître consulte la Library
4. Vérifier que le code généré respecte les patterns

### **Phase 2 : Validation Qualité** (À faire)
1. Comparer qualité code AVANT/APRÈS
2. Mesurer nombre d'erreurs détectées par VALIDATEUR
3. Mesurer nombre de cycles de correction

### **Phase 3 : Enrichissement Continu** (Futur)
1. Ajouter plus de documents dans Library
2. Affiner les patterns existants
3. Documenter les erreurs récurrentes

---

## ✅ Résumé

**Modification effectuée** : Prompt JARVIS_Maître enrichi pour consultation systématique de la Library

**Impact** :
- ✅ Qualité code améliorée
- ✅ Cohérence garantie
- ✅ Moins d'erreurs
- ✅ Moins de corrections

**Architecture maintenue** :
- ✅ CODEUR = Exécution pure (pas de functions)
- ✅ VALIDATEUR = Vérification pure (pas de functions)
- ✅ JARVIS_Maître = Recherche + Orchestration + Enrichissement

**Prochaine action** : Tester avec un projet réel pour valider l'amélioration
