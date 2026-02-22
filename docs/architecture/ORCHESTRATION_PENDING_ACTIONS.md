# ORCHESTRATION — Gestion des Actions en Attente

**Module** : `backend/services/orchestration.py`  
**Classe** : `SimpleOrchestrator`  
**Attribut** : `_pending_actions`

---

## 📍 LOCALISATION DANS LE CODE

**Déclaration** : Ligne 58 de `orchestration.py`

```python
class SimpleOrchestrator:
    # Stockage temporaire actions bloquées (conversation_id -> action_data)
    _pending_actions = {}
```

**Type** : Attribut de classe (dictionnaire partagé entre toutes les instances)

---

## 🗂️ STRUCTURE DES DONNÉES STOCKÉES

**Clé** : `conversation_id` (str)

**Valeur** : Dictionnaire avec structure exacte suivante :

```python
{
    "user_message": str,              # Message utilisateur original
    "delegations": list[dict],        # Liste délégations détectées
    "classification": dict,           # Résultat SafetyService.classify_action()
    "conversation_history": list,     # Historique complet conversation
    "project_path": str,              # Chemin projet
    "function_executor": object,      # Instance FunctionExecutor
    "session_state": SessionState,    # État session complet
    "confirmed": bool,                # Flag confirmation (False par défaut)
}
```

### Détail des Champs

| Champ | Type | Source | Usage |
|-------|------|--------|-------|
| `user_message` | str | `conversation_history[-1]["content"]` | Affichage challenge |
| `delegations` | list[dict] | `detect_delegations(response)` | Relance exécution |
| `classification` | dict | `SafetyService.classify_action()` | Raison blocage |
| `conversation_history` | list | Paramètre `process_response()` | Contexte relance |
| `project_path` | str | Paramètre `process_response()` | Écriture fichiers |
| `function_executor` | FunctionExecutor | Paramètre `process_response()` | Functions Mistral |
| `session_state` | SessionState | Paramètre `process_response()` | Protection écriture |
| `confirmed` | bool | Initialisé `False`, modifié par API | Bypass safety |

---

## 🔄 CYCLE DE VIE

### 1. Création (Stockage)

**Localisation** : Lignes 773-782 de `orchestration.py`

**Condition** :
```python
if not classification["is_safe"] and classification["requires_validation"]:
    SimpleOrchestrator._pending_actions[session_id] = {...}
```

**Déclencheur** : Action classifiée NON-SAFE par `SafetyService`

**Log** :
```
Orchestration: action NON-SAFE détectée, challenge généré et action stockée (raison)
```

### 2. Lecture (Bypass Safety)

**Localisation** : Ligne 760 de `orchestration.py`

**Code** :
```python
bypass_safety = SimpleOrchestrator._pending_actions.get(session_id, {}).get("confirmed", False)
```

**Usage** : Vérifier si action confirmée avant classification SafetyService

### 3. Modification (Confirmation)

**Localisation** : Ligne 346 de `api.py`

**Code** :
```python
SimpleOrchestrator._pending_actions[conversation_id]["confirmed"] = True
```

**Déclencheur** : Appel endpoint `POST /api/conversations/{id}/confirm-action`

**Log** :
```
API: confirmation action NON-SAFE pour conversation {conversation_id}
```

### 4. Suppression (Nettoyage)

**Localisation** : Lignes 798-800 de `orchestration.py`

**Code** :
```python
if bypass_safety and session_id in SimpleOrchestrator._pending_actions:
    del SimpleOrchestrator._pending_actions[session_id]
    logger.info("Orchestration: action confirmée exécutée, flag nettoyé")
```

**Déclencheur** : Après exécution action confirmée

**Obligation** : Nettoyage automatique pour éviter fuite mémoire

---

## ⚠️ LIMITES ET CONTRAINTES

### Limite 1 : Stockage Mémoire Uniquement

**Conséquence** : Actions perdues si redémarrage serveur

**Impact** :
- Utilisateur doit relancer action après redémarrage
- Challenge affiché mais confirmation impossible

**Mitigation** : Acceptable pour MVP mono-utilisateur

### Limite 2 : Non Persistant

**Conséquence** : Aucune trace après suppression

**Impact** :
- Pas d'historique confirmations
- Pas d'audit trail

**Mitigation** : Logs applicatifs conservent trace

### Limite 3 : Hypothèse Mono-Utilisateur

**Conséquence** : Dictionnaire partagé entre toutes conversations

**Impact** :
- Clé = `conversation_id` (pas `user_id`)
- Multi-utilisateurs : risque collision si même `conversation_id`

**Mitigation** : UUID garantit unicité en pratique

### Limite 4 : Pas de TTL (Time To Live)

**Conséquence** : Actions non confirmées restent en mémoire indéfiniment

**Impact** :
- Fuite mémoire si utilisateur abandonne
- Dictionnaire grandit sans limite

**Mitigation** : Redémarrage serveur nettoie tout

---

## 🧹 NETTOYAGE OBLIGATOIRE

### Règle Absolue

**Toute action confirmée DOIT être nettoyée après exécution**

**Code** (lignes 798-800) :
```python
if bypass_safety and session_id in SimpleOrchestrator._pending_actions:
    del SimpleOrchestrator._pending_actions[session_id]
```

### Pourquoi Obligatoire ?

1. **Éviter fuite mémoire** : Dictionnaire grandit indéfiniment
2. **Éviter rejeu** : Action confirmée ne doit pas être rejouable
3. **Cohérence état** : `confirmed=True` ne doit pas persister

### Vérification

**Test intégration** : `test_confirmation_workflow_complete`

```python
# Après exécution
assert session_id not in SimpleOrchestrator._pending_actions
```

---

## 🚨 RISQUES IDENTIFIÉS

### Risque 1 : Redémarrage Serveur

**Scénario** :
1. Utilisateur reçoit challenge
2. Serveur redémarre
3. Utilisateur clique "Confirmer"
4. Erreur 404 "Aucune action en attente"

**Gravité** : ⚠️ Importante (UX dégradée)

**Mitigation** : Message erreur explicite + relancer action

### Risque 2 : Fuite Mémoire

**Scénario** :
1. Utilisateur reçoit 100 challenges
2. Utilisateur ne confirme jamais
3. 100 entrées restent en mémoire

**Gravité** : ⚠️ Faible (mono-utilisateur, redémarrage nettoie)

**Mitigation** : Implémenter TTL (hors périmètre MVP)

### Risque 3 : Oubli Nettoyage

**Scénario** :
1. Développeur modifie `process_response()`
2. Oublie ligne `del _pending_actions[session_id]`
3. Actions confirmées rejouables

**Gravité** : 🚨 Critique (sécurité)

**Mitigation** : Test intégration vérifie nettoyage

---

## 📊 MÉTRIQUES

**Capacité** : Illimitée (dictionnaire Python)

**Durée de vie** : Jusqu'à redémarrage serveur ou nettoyage

**Concurrence** : Thread-safe (GIL Python)

**Persistance** : Aucune

---

## ✅ VALIDATION

**Test** : `tests/test_integration_stabilization.py::TestIntegrationConfirmation::test_confirmation_workflow_complete`

**Couverture** :
- ✅ Stockage action bloquée
- ✅ Lecture flag `confirmed`
- ✅ Modification flag `confirmed`
- ✅ Nettoyage après exécution

---

## 📝 HYPOTHÈSES IMPLICITES

1. **Mono-utilisateur** : Pas de gestion multi-tenancy
2. **Serveur stateful** : Pas de load balancing multi-instances
3. **Actions courtes** : Pas de timeout gestion
4. **Confirmation unique** : Pas de multi-validation
5. **Nettoyage manuel** : Pas de garbage collection automatique

---

**Document synchronisé avec code réel** : 2026-02-17  
**Fichiers sources** : `orchestration.py` (L58, L760, L773-800), `api.py` (L346)
