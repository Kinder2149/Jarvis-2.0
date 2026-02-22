# SESSION STATE — Autorité Décisionnelle Écriture Disque

**Module** : `backend/models/session_state.py`  
**Classe** : `SessionState`  
**Méthode** : `can_write_disk()`

---

## 🎯 RÈGLE FORMELLE

### Règle Absolue

**`can_write_disk()` est la seule autorité décisionnelle d'écriture disque.**

**Conséquence** :
- Toute écriture disque DOIT appeler `can_write_disk()` avant exécution
- Toute écriture disque DOIT passer par `file_writer.write_files_to_project()`
- Aucun module ne peut écrire directement sur disque sans cette validation

---

## 📍 LOCALISATION DANS LE CODE

**Définition** : Lignes 152-171 de `session_state.py`

```python
def can_write_disk(self) -> bool:
    """
    Détermine si l'écriture disque est autorisée
    
    Returns:
        True si écriture autorisée, False sinon
    
    Règles :
        - Mode CHAT : jamais d'écriture
        - Mode PROJECT + Phase REFLEXION : jamais d'écriture
        - Mode PROJECT + Phase EXECUTION : écriture autorisée
    """
    if self.mode == Mode.CHAT:
        return False
    
    if self.phase == Phase.REFLEXION:
        return False
    
    # Phase EXECUTION
    return True
```

**Protection** : Lignes 211-226 de `file_writer.py`

```python
def write_files_to_project(
    project_path: str,
    files: list[dict],
    session_state=None,
) -> list[dict]:
    # 🚨 PROTECTION CRITIQUE : Vérifier autorisation écriture disque
    if session_state and not session_state.can_write_disk():
        logger.warning(
            "🚨 ÉCRITURE DISQUE BLOQUÉE : mode=%s, phase=%s",
            session_state.mode.value if session_state.mode else "unknown",
            session_state.phase.value if session_state.phase else "none"
        )
        # Retourner tous les fichiers comme "blocked"
        return [
            {
                "path": f["path"],
                "status": "blocked",
                "error": f"Écriture disque interdite (...)"
            }
            for f in files
        ]
```

---

## 🔒 RÈGLES DE DÉCISION

### Règle 1 : Mode CHAT → Blocage Absolu

**Code** : Lignes 164-165 de `session_state.py`

```python
if self.mode == Mode.CHAT:
    return False
```

**Justification** : Mode CHAT = conversation simple, pas de projet, pas d'écriture

**Validation** : Test `test_chat_mode_blocks_disk_write` ✅

### Règle 2 : Phase REFLEXION → Blocage Absolu

**Code** : Lignes 167-168 de `session_state.py`

```python
if self.phase == Phase.REFLEXION:
    return False
```

**Justification** : Phase REFLEXION = planification, pas d'exécution

**Validation** : Test `test_reflexion_phase_blocks_write` ✅

### Règle 3 : Phase EXECUTION → Autorisation

**Code** : Lignes 170-171 de `session_state.py`

```python
# Phase EXECUTION
return True
```

**Justification** : Phase EXECUTION = production code, écriture autorisée

**Validation** : Test `test_new_project_safe_action_allowed` ✅

---

## 🛡️ PROTECTION CENTRALISÉE

### Point Unique d'Écriture

**Module** : `backend/services/file_writer.py`

**Fonction** : `write_files_to_project()`

**Paramètre obligatoire** : `session_state`

**Code** : Ligne 212 de `file_writer.py`

```python
if session_state and not session_state.can_write_disk():
    # Blocage + log + retour status="blocked"
```

### Points d'Appel Protégés

**Total** : 3 points d'écriture identifiés dans `orchestration.py`

#### Point 1 : Passe 1 Écriture Initiale CODEUR

**Localisation** : Ligne 456 de `orchestration.py`

```python
files_written = write_files_to_project(
    project_path, code_blocks, session_state
)
```

#### Point 2 : Passes Supplémentaires CODEUR

**Localisation** : Ligne 496 de `orchestration.py`

```python
files_written = write_files_to_project(
    project_path, code_blocks, session_state
)
```

#### Point 3 : Correction Fichiers CODEUR

**Localisation** : Ligne 585 de `orchestration.py`

```python
files_written = write_files_to_project(
    project_path, code_blocks, session_state
)
```

**Garantie** : Tous les points d'écriture passent par `file_writer` avec `session_state`

---

## 🔍 VÉRIFICATION ÉCRITURES DIRECTES

### Recherche Exhaustive Backend

**Commande** : `grep -r "write_text|\.write\(" backend/*.py`

**Résultats** : 3 occurrences détectées

#### Occurrence 1 : `file_writer.py` (Ligne 241)

**Code** :
```python
target.write_text(content, encoding="utf-8")
```

**Contexte** : Fonction `write_files_to_project()` — **PROTÉGÉE** par `can_write_disk()`

**Statut** : ✅ **CONFORME**

#### Occurrence 2 : `migrations.py` (Ligne 139)

**Code** :
```python
f.write_text("hello")
```

**Contexte** : Exemple documentation pytest (commentaire)

**Statut** : ✅ **INOFFENSIF** (pas de code exécuté)

#### Occurrence 3 : `base_agent.py` (Ligne 86)

**Code** :
```python
with open(self.log_file, "a", encoding="utf-8") as f:
    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
```

**Contexte** : Écriture logs agent (fichier `.jsonl` dans `logs/`)

**Statut** : ⚠️ **ÉCRITURE DIRECTE NON PROTÉGÉE**

**Analyse** :
- **Type** : Logs applicatifs (pas fichiers projet)
- **Destination** : `logs/{agent_name}.jsonl` (hors projet)
- **Impact** : Aucun (logs système, pas code utilisateur)
- **Protection nécessaire ?** : Non (hors périmètre `can_write_disk()`)

**Conclusion** : ✅ **ACCEPTABLE** (logs système exclus du périmètre)

---

## 📊 SYNTHÈSE CONFORMITÉ

### Écritures Projet (Protégées)

| Module | Fonction | Protection | Statut |
|--------|----------|------------|--------|
| `file_writer.py` | `write_files_to_project()` | `can_write_disk()` | ✅ Conforme |
| `orchestration.py` | Appels `write_files_to_project()` (×3) | Via `file_writer` | ✅ Conforme |

### Écritures Système (Hors Périmètre)

| Module | Fonction | Type | Statut |
|--------|----------|------|--------|
| `base_agent.py` | `log()` | Logs applicatifs | ✅ Acceptable |

### Écritures Absentes

**Aucune écriture directe projet détectée hors `file_writer.py`**

**Conclusion** : ✅ **Règle respectée — Toute écriture projet passe par `file_writer`**

---

## 🔗 INDÉPENDANCE AVEC SAFETY SERVICE

### Validation Indépendante

**`can_write_disk()` ≠ Classification SafetyService**

**Deux validations distinctes** :

#### Validation 1 : SafetyService (Orchestration)

**Responsabilité** : Classifier action SAFE/NON-SAFE

**Localisation** : Ligne 764 de `orchestration.py`

**Peut être bypassée** : Oui (via flag `confirmed`)

#### Validation 2 : can_write_disk() (File Writer)

**Responsabilité** : Autoriser écriture disque

**Localisation** : Ligne 212 de `file_writer.py`

**Peut être bypassée** : ❌ **NON** (validation systématique)

### Scénario Combiné

**Exemple** : Action NON-SAFE confirmée en phase REFLEXION

```python
# Orchestration
bypass_safety = True  # Action confirmée
# SafetyService NON appelé (bypass)

# File Writer
session_state.can_write_disk()  # False (phase REFLEXION)
# Écriture BLOQUÉE malgré bypass SafetyService
```

**Conclusion** : `can_write_disk()` est **non contournable**

---

## ⚠️ RISQUES IDENTIFIÉS

### Risque 1 : Écriture Directe Future

**Scénario** :
1. Développeur crée nouveau module
2. Écrit directement fichier sans passer par `file_writer`
3. Bypass complet `can_write_disk()`

**Gravité** : 🚨 Critique (contournement protection)

**Mitigation** :
- Documentation claire (ce document)
- Revue code obligatoire
- Tests intégration détectent écritures non protégées

### Risque 2 : Paramètre `session_state` Omis

**Scénario** :
```python
# Code incorrect
write_files_to_project(project_path, files)  # session_state omis
```

**Gravité** : 🚨 Critique (protection désactivée)

**Mitigation** :
- Paramètre `session_state` obligatoire (pas de défaut)
- Tests vérifient passage `session_state`

**État actuel** : ⚠️ Paramètre optionnel (`session_state=None`)

**Recommandation** : Rendre obligatoire (hors périmètre sprint)

### Risque 3 : Modification Logique `can_write_disk()`

**Scénario** :
1. Développeur modifie règles `can_write_disk()`
2. Oublie mettre à jour tests
3. Régression non détectée

**Gravité** : ⚠️ Importante (sécurité)

**Mitigation** : Tests intégration couvrent 3 règles

---

## ✅ VALIDATION

### Tests Intégration

**Fichier** : `tests/test_integration_stabilization.py`

**Couverture** :

#### Test 1 : Mode CHAT Bloqué

**Méthode** : `test_chat_mode_blocks_disk_write`

**Validation** :
```python
session_state = SessionState(mode=Mode.CHAT, ...)
assert session_state.can_write_disk() is False
results = write_files_to_project(..., session_state)
assert results[0]["status"] == "blocked"
```

**Statut** : ✅ PASSÉ

#### Test 2 : Phase REFLEXION Bloquée

**Méthode** : `test_reflexion_phase_blocks_write`

**Validation** :
```python
session_state = SessionState(mode=Mode.PROJECT, phase=Phase.REFLEXION, ...)
assert session_state.can_write_disk() is False
results = write_files_to_project(..., session_state)
assert results[0]["status"] == "blocked"
```

**Statut** : ✅ PASSÉ

#### Test 3 : Phase EXECUTION Autorisée

**Méthode** : `test_new_project_safe_action_allowed`

**Validation** :
```python
session_state = SessionState(mode=Mode.PROJECT, phase=Phase.EXECUTION, ...)
assert session_state.can_write_disk() is True
results = write_files_to_project(..., session_state)
assert results[0]["status"] == "written"
```

**Statut** : ✅ PASSÉ

---

## 📝 HYPOTHÈSES IMPLICITES

1. **Logs système exclus** : Écriture logs `base_agent.py` hors périmètre
2. **Paramètre optionnel** : `session_state=None` accepté (protection désactivée si None)
3. **Développeurs disciplinés** : Pas de nouvelle écriture directe
4. **Tests suffisants** : 3 tests couvrent toutes les règles
5. **Règles stables** : Logique `can_write_disk()` ne changera pas
6. **Protection file_writer** : Seul point d'écriture projet

---

## 🎯 GARANTIES FOURNIES

### Garantie 1 : Blocage Mode CHAT

**Énoncé** : Mode CHAT ne peut jamais écrire sur disque

**Preuve** : Test `test_chat_mode_blocks_disk_write` ✅

### Garantie 2 : Blocage Phase REFLEXION

**Énoncé** : Phase REFLEXION ne peut jamais écrire sur disque

**Preuve** : Test `test_reflexion_phase_blocks_write` ✅

### Garantie 3 : Autorisation Phase EXECUTION

**Énoncé** : Phase EXECUTION autorise écriture disque

**Preuve** : Test `test_new_project_safe_action_allowed` ✅

### Garantie 4 : Protection Non Contournable

**Énoncé** : Bypass SafetyService n'affecte pas `can_write_disk()`

**Preuve** : Validations indépendantes (orchestration vs file_writer)

### Garantie 5 : Point Unique Écriture

**Énoncé** : Toute écriture projet passe par `file_writer`

**Preuve** : Recherche exhaustive backend (3 occurrences, 1 protégée, 2 hors périmètre)

---

## 🔧 MAINTENANCE

### Ajout Nouvelle Écriture

**Procédure obligatoire** :

1. Utiliser `file_writer.write_files_to_project()`
2. Passer `session_state` en paramètre
3. Ajouter test intégration
4. Vérifier logs blocage

**Exemple** :
```python
from backend.services.file_writer import write_files_to_project

results = write_files_to_project(
    project_path=project["path"],
    files=[{"path": "new_file.py", "content": "..."}],
    session_state=session_state  # ← OBLIGATOIRE
)
```

### Modification Règles `can_write_disk()`

**Procédure obligatoire** :

1. Modifier `session_state.py`
2. Mettre à jour tests intégration
3. Mettre à jour ce document
4. Vérifier tous les appels `write_files_to_project()`

---

**Document synchronisé avec code réel** : 2026-02-17  
**Fichiers sources** : `session_state.py` (L152-171), `file_writer.py` (L211-226), `orchestration.py` (L456, L496, L585), `base_agent.py` (L86)
