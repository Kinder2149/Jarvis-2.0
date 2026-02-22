# SAFETY SERVICE — Mécanisme de Bypass Sécurité

**Module** : `backend/services/safety_service.py`  
**Classe** : `SafetyService`  
**Mécanisme** : Bypass via flag `confirmed` dans `_pending_actions`

---

## 📍 LOCALISATION DANS LE CODE

**SafetyService ne gère PAS le bypass directement**

Le bypass est géré par `SimpleOrchestrator` qui **court-circuite** l'appel à `SafetyService`.

**Code orchestration** : Lignes 758-795 de `orchestration.py`

```python
# Vérifier si action confirmée (bypass safety check)
bypass_safety = SimpleOrchestrator._pending_actions.get(session_id, {}).get("confirmed", False)

if session_state and session_state.mode == Mode.PROJECT and delegations and not bypass_safety:
    # Classification SafetyService UNIQUEMENT si pas de bypass
    classification = SafetyService.classify_action(...)
```

---

## 🔓 CONDITION EXACTE D'ACTIVATION

### Condition Bypass

**Code** : Ligne 760 de `orchestration.py`

```python
bypass_safety = SimpleOrchestrator._pending_actions.get(session_id, {}).get("confirmed", False)
```

**Activation** : `bypass_safety == True`

### Condition Classification

**Code** : Ligne 762 de `orchestration.py`

```python
if session_state and session_state.mode == Mode.PROJECT and delegations and not bypass_safety:
    # SafetyService appelé
```

**Conditions cumulatives** :
1. `session_state` existe (pas None)
2. `session_state.mode == Mode.PROJECT` (pas CHAT)
3. `delegations` non vide (délégation détectée)
4. `not bypass_safety` (pas de confirmation)

**Si une condition échoue** : SafetyService **non appelé** (pas de classification)

---

## 📖 LECTURE DU FLAG `confirmed`

### Étape 1 : Lecture Flag

**Localisation** : Ligne 760 de `orchestration.py`

**Code** :
```python
bypass_safety = SimpleOrchestrator._pending_actions.get(session_id, {}).get("confirmed", False)
```

**Logique** :
- Si `session_id` absent de `_pending_actions` → `bypass_safety = False`
- Si `session_id` présent mais pas de clé `"confirmed"` → `bypass_safety = False`
- Si `"confirmed": True` → `bypass_safety = True`

### Étape 2 : Court-Circuit Classification

**Localisation** : Ligne 762 de `orchestration.py`

**Code** :
```python
if ... and not bypass_safety:
    # Classification SafetyService
```

**Effet** :
- `bypass_safety = False` → Classification exécutée
- `bypass_safety = True` → Classification **ignorée**, exécution directe

### Étape 3 : Exécution Délégation

**Localisation** : Lignes 801-820 de `orchestration.py`

**Code** :
```python
# Exécuter délégations (avec ou sans bypass)
for delegation in delegations:
    result = await self.execute_delegation(...)
```

**Comportement** : Délégation exécutée normalement, bypass transparent

---

## 🧹 NETTOYAGE DU FLAG

### Nettoyage Automatique

**Localisation** : Lignes 798-800 de `orchestration.py`

**Code** :
```python
# Si bypass_safety activé, nettoyer le flag après exécution
if bypass_safety and session_id in SimpleOrchestrator._pending_actions:
    del SimpleOrchestrator._pending_actions[session_id]
    logger.info("Orchestration: action confirmée exécutée, flag nettoyé")
```

**Déclencheur** : Après lecture `bypass_safety = True` et **avant** exécution délégations

**Timing** : Nettoyage **immédiat** (pas après exécution)

### Pourquoi Nettoyage Immédiat ?

**Raison** : Éviter rejeu action confirmée

**Scénario sans nettoyage** :
1. Utilisateur confirme action
2. Action exécutée avec `bypass_safety = True`
3. Flag `confirmed` reste `True`
4. Utilisateur relance même action
5. Action re-exécutée sans challenge (🚨 FAILLE)

**Solution** : Nettoyage immédiat après lecture flag

---

## 🚨 RISQUES DE CONTOURNEMENT

### Risque 1 : Manipulation Directe `_pending_actions`

**Scénario** :
```python
# Code malveillant
SimpleOrchestrator._pending_actions["conv-123"] = {"confirmed": True}
```

**Gravité** : 🚨 Critique (bypass sans validation)

**Mitigation** :
- Attribut de classe (pas d'encapsulation)
- Hypothèse : code backend sûr
- Pas de protection runtime

### Risque 2 : Oubli Nettoyage

**Scénario** :
1. Développeur commente ligne `del _pending_actions[session_id]`
2. Flag `confirmed` persiste
3. Actions rejouables sans challenge

**Gravité** : 🚨 Critique (sécurité)

**Mitigation** : Test intégration vérifie nettoyage

### Risque 3 : Race Condition Multi-Threads

**Scénario** :
1. Thread A lit `bypass_safety = True`
2. Thread B modifie `_pending_actions[session_id]`
3. Thread A nettoie mauvaise entrée

**Gravité** : ⚠️ Faible (GIL Python + mono-utilisateur)

**Mitigation** : Hypothèse mono-thread orchestration

### Risque 4 : Bypass Sans Stockage Initial

**Scénario** :
```python
# Créer directement entrée confirmée
SimpleOrchestrator._pending_actions["conv-999"] = {"confirmed": True}
```

**Gravité** : 🚨 Critique (bypass complet SafetyService)

**Mitigation** : Aucune protection code

---

## 📊 TRACE LOGS EXISTANTE

### Log 1 : Détection Action NON-SAFE

**Localisation** : Lignes 791-794 de `orchestration.py`

**Code** :
```python
logger.info(
    "Orchestration: action NON-SAFE détectée, challenge généré et action stockée (%s)",
    classification["reason"]
)
```

**Contenu** : Raison classification NON-SAFE

### Log 2 : Confirmation API

**Localisation** : Lignes 348-351 de `api.py`

**Code** :
```python
logger.info(
    "API: confirmation action NON-SAFE pour conversation %s",
    conversation_id
)
```

**Contenu** : ID conversation confirmée

### Log 3 : Nettoyage Flag

**Localisation** : Ligne 800 de `orchestration.py`

**Code** :
```python
logger.info("Orchestration: action confirmée exécutée, flag nettoyé")
```

**Contenu** : Confirmation nettoyage

### Log 4 : Blocage Écriture Disque

**Localisation** : Lignes 213-217 de `file_writer.py`

**Code** :
```python
logger.warning(
    "🚨 ÉCRITURE DISQUE BLOQUÉE : mode=%s, phase=%s",
    session_state.mode.value if session_state.mode else "unknown",
    session_state.phase.value if session_state.phase else "none"
)
```

**Contenu** : Mode et phase lors du blocage

### Logs Manquants

**Aucun log pour** :
- Lecture flag `bypass_safety`
- Valeur `bypass_safety` (True/False)
- Court-circuit classification SafetyService

**Impact** : Difficile de tracer bypass en production

---

## 🔍 ANALYSE FLUX COMPLET

### Flux Normal (Sans Bypass)

```
1. Utilisateur envoie message
2. Jarvis_maitre détecte délégation
3. bypass_safety = False (pas d'entrée _pending_actions)
4. SafetyService.classify_action() appelé
5. Classification NON-SAFE
6. Stockage _pending_actions avec confirmed=False
7. Retour challenge utilisateur
8. Fin (pas d'exécution)
```

### Flux Confirmation (Avec Bypass)

```
1. Utilisateur clique "Confirmer"
2. API modifie _pending_actions[conv_id]["confirmed"] = True
3. API relance orchestration
4. bypass_safety = True (lecture flag)
5. SafetyService.classify_action() NON APPELÉ (court-circuit)
6. Nettoyage _pending_actions[conv_id]
7. Exécution délégation directe
8. Écriture fichiers (si can_write_disk() = True)
9. Retour résultat utilisateur
```

---

## ⚙️ RÈGLES MÉTIER

### Règle 1 : Bypass = Court-Circuit Complet

**SafetyService n'est JAMAIS appelé si `bypass_safety = True`**

**Conséquence** : Pas de double validation, pas de log classification

### Règle 2 : Nettoyage = Consommation Unique

**Flag `confirmed` consommé après 1 lecture**

**Conséquence** : Action confirmée non rejouable

### Règle 3 : Bypass ≠ Autorisation Écriture

**Bypass SafetyService ≠ Bypass `can_write_disk()`**

**Validation indépendante** :
- SafetyService : Classification SAFE/NON-SAFE
- SessionState : Autorisation écriture disque

**Code** : `file_writer.py` ligne 212
```python
if session_state and not session_state.can_write_disk():
    # Blocage même si bypass_safety = True
```

### Règle 4 : Mode CHAT Jamais Bypass

**Condition ligne 762** : `session_state.mode == Mode.PROJECT`

**Conséquence** : Mode CHAT ne peut pas utiliser bypass (pas de délégation)

---

## ✅ VALIDATION

**Test** : `tests/test_integration_stabilization.py::TestIntegrationConfirmation::test_confirmation_workflow_complete`

**Couverture** :
- ✅ Classification NON-SAFE initiale
- ✅ Stockage action avec `confirmed=False`
- ✅ Modification `confirmed=True`
- ✅ Lecture flag `bypass_safety`
- ✅ Nettoyage après exécution

---

## 📝 HYPOTHÈSES IMPLICITES

1. **Code backend sûr** : Pas de protection contre manipulation `_pending_actions`
2. **Mono-thread orchestration** : Pas de gestion concurrence
3. **Nettoyage manuel** : Développeur doit maintenir ligne `del`
4. **Logs suffisants** : Pas de log détaillé bypass
5. **Bypass transparent** : Délégation ne sait pas si bypass actif
6. **Validation indépendante** : `can_write_disk()` toujours vérifié

---

## 🔗 INTERACTIONS AVEC AUTRES MODULES

### Avec `SafetyService`

**Relation** : Court-circuit (bypass évite appel)

**Code** : Ligne 764 de `orchestration.py`

### Avec `SessionState`

**Relation** : Indépendante (bypass n'affecte pas `can_write_disk()`)

**Code** : Ligne 212 de `file_writer.py`

### Avec `file_writer`

**Relation** : Aucune (bypass transparent pour écriture)

**Code** : Écriture protégée par `session_state.can_write_disk()`

### Avec API

**Relation** : API modifie flag, orchestration lit flag

**Code** : Ligne 346 de `api.py` (écriture), ligne 760 de `orchestration.py` (lecture)

---

**Document synchronisé avec code réel** : 2026-02-17  
**Fichiers sources** : `orchestration.py` (L760, L762, L798-800), `api.py` (L346), `file_writer.py` (L212)
