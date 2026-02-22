# 📋 PLAN INTÉGRATION PHASE 4

**Date** : 2026-02-17  
**Objectif** : Intégrer session_state, project_service, safety_service dans backend

---

## 🎯 STRATÉGIE GLOBALE

**Principe** : Modifications minimales et ciblées, tests unitaires systématiques

**Ordre d'intégration** :
1. **api.py** : Injection SessionState au début de `/chat`
2. **orchestration.py** : Intégration ProjectService + SafetyService
3. **Tests unitaires** : Validation chaque modification
4. **Tests régression** : Vérification baseline maintenue

---

## 📝 MODIFICATION 1 — api.py

### Point d'injection : `/api/chat` (ligne ~200)

**Objectif** : Créer SessionState au début de la requête chat

**Modifications** :

```python
# AVANT (ligne ~200)
conversation = await db_instance.get_conversation(conversation_id)
if not conversation:
    raise HTTPException(status_code=404, detail="Conversation not found")

messages = await db_instance.get_conversation_history(conversation_id)

# APRÈS
from backend.models.session_state import SessionState

conversation = await db_instance.get_conversation(conversation_id)
if not conversation:
    raise HTTPException(status_code=404, detail="Conversation not found")

# Créer SessionState depuis conversation
session_state = SessionState.from_conversation(conversation)

messages = await db_instance.get_conversation_history(conversation_id)
```

**Impact** :
- +2 lignes (import)
- +2 lignes (création session_state)
- Total : +4 lignes

**Tests** :
- Test création SessionState mode CHAT
- Test création SessionState mode PROJECT
- Test validation cohérence état

---

## 📝 MODIFICATION 2 — api.py (enrichissement contexte)

### Point d'injection : Contexte projet (ligne ~226)

**Objectif** : Utiliser ProjectService pour enrichir contexte

**Modifications** :

```python
# AVANT (ligne ~226)
context_content = build_project_context_message(project, file_tree)
msg.content = f"{context_content}\n\n---\n\n{msg.content}"

# APRÈS
from backend.services.project_service import ProjectService

# Analyser état projet
project_state = ProjectService.analyze_project_state(project["path"])
session_state.set_project_state(project_state)

# Analyser dette si nécessaire
debt_report = None
if project_state == ProjectState.DEBT:
    debt_report = ProjectService.analyze_debt(project["path"])

# Contexte enrichi
context_content = ProjectService.build_enriched_context(
    project, file_tree, project_state, debt_report
)
msg.content = f"{context_content}\n\n---\n\n{msg.content}"
```

**Impact** :
- +1 ligne (import)
- +10 lignes (analyse projet + dette + contexte)
- Total : +11 lignes

**Tests** :
- Test enrichissement contexte NEW
- Test enrichissement contexte CLEAN
- Test enrichissement contexte DEBT
- Test analyse dette intégrée

---

## 📝 MODIFICATION 3 — orchestration.py

### Point d'injection : `process_response` (ligne ~700)

**Objectif** : Intégrer SafetyService avant délégation

**Modifications** :

```python
# AVANT (ligne ~700)
async def process_response(
    self,
    response: str,
    conversation_history: list[dict],
    session_id: str | None = None,
    project_path: str | None = None,
    function_executor = None,
) -> tuple[str, list[dict]]:

# APRÈS
from backend.services.safety_service import SafetyService
from backend.models.session_state import SessionState

async def process_response(
    self,
    response: str,
    conversation_history: list[dict],
    session_id: str | None = None,
    project_path: str | None = None,
    function_executor = None,
    session_state: SessionState | None = None,  # NOUVEAU
) -> tuple[str, list[dict]]:
```

**Impact** :
- +2 lignes (imports)
- +1 ligne (paramètre session_state)
- Total : +3 lignes

---

## 📝 MODIFICATION 4 — orchestration.py (classification SAFE)

### Point d'injection : Avant `execute_delegation` (ligne ~750)

**Objectif** : Classifier action et générer challenge si NON-SAFE

**Modifications** :

```python
# AVANT
for delegation in delegations:
    result = await self.execute_delegation(...)
    delegation_results.append(result)

# APRÈS
for delegation in delegations:
    # Classification SAFE/NON-SAFE
    if session_state and session_state.mode == Mode.PROJECT:
        user_message = conversation_history[-1]["content"] if conversation_history else ""
        classification = SafetyService.classify_action(
            user_message,
            session_state.project_state or ProjectState.NEW,
            session_state.phase.value if session_state.phase else "reflexion"
        )
        
        # Si NON-SAFE et validation requise, générer challenge
        if not classification["is_safe"] and classification["requires_validation"]:
            challenge = SafetyService.generate_challenge(
                user_message,
                classification,
                session_state.project_state
            )
            # Retourner challenge au lieu d'exécuter
            return challenge, []
    
    result = await self.execute_delegation(...)
    delegation_results.append(result)
```

**Impact** :
- +20 lignes (classification + challenge)
- Total : +20 lignes

**Tests** :
- Test classification SAFE → exécution
- Test classification NON-SAFE → challenge
- Test challenge projet DEBT
- Test challenge action structurante

---

## 📝 MODIFICATION 5 — api.py (passage session_state)

### Point d'injection : Appel `process_response` (ligne ~266)

**Objectif** : Passer session_state à orchestration

**Modifications** :

```python
# AVANT (ligne ~266)
response, delegation_results = await orchestrator.process_response(
    response=response,
    conversation_history=messages_for_api,
    session_id=conversation_id,
    project_path=project_path,
    function_executor=function_executor,
)

# APRÈS
response, delegation_results = await orchestrator.process_response(
    response=response,
    conversation_history=messages_for_api,
    session_id=conversation_id,
    project_path=project_path,
    function_executor=function_executor,
    session_state=session_state,  # NOUVEAU
)
```

**Impact** :
- +1 ligne (paramètre session_state)
- Total : +1 ligne

---

## 📊 RÉCAPITULATIF MODIFICATIONS

| Fichier | Modifications | Lignes ajoutées | Tests |
|---------|---------------|-----------------|-------|
| `api.py` | 3 points | +16 lignes | 4 tests |
| `orchestration.py` | 2 points | +23 lignes | 4 tests |

**Total** : 5 modifications, +39 lignes, 8 tests unitaires

---

## ✅ CHECKLIST INTÉGRATION

### Avant modifications
- [x] Plan d'intégration validé
- [ ] Backup baseline tests (195 passed)
- [ ] Lecture complète fichiers à modifier

### Pendant modifications
- [ ] Modification 1 : api.py (SessionState)
- [ ] Test 1 : Création SessionState
- [ ] Modification 2 : api.py (ProjectService)
- [ ] Test 2 : Enrichissement contexte
- [ ] Modification 3 : orchestration.py (paramètre)
- [ ] Modification 4 : orchestration.py (SafetyService)
- [ ] Test 3 : Classification SAFE/NON-SAFE
- [ ] Modification 5 : api.py (passage session_state)

### Après modifications
- [ ] Tests unitaires intégration (8 tests)
- [ ] Tests régression (baseline 195 passed maintenue)
- [ ] Validation manuelle Chat simple
- [ ] Validation manuelle Projet NEW
- [ ] Validation manuelle Projet DEBT

---

## 🎯 CRITÈRES SUCCÈS

1. ✅ Tous les tests unitaires intégration passent (8/8)
2. ✅ Baseline tests maintenue (195 passed)
3. ✅ Aucune régression comportement Chat
4. ✅ Aucune régression comportement Projet
5. ✅ SessionState créé et utilisé correctement
6. ✅ ProjectService enrichit contexte
7. ✅ SafetyService classifie et challenge

---

**FIN PLAN INTÉGRATION PHASE 4**
