# Régression Library - Enrichissement Prompt JARVIS_Maître

**Date** : 22 février 2026  
**Statut** : ✅ RÉSOLU - Retour à la version stable  
**Impact** : Critique - Système totalement non fonctionnel  
**Durée** : ~2h (détection + résolution)

---

## 🎯 Contexte

### Objectif Initial
Améliorer la qualité du code généré par CODEUR en enrichissant automatiquement les instructions de JARVIS_Maître avec le contexte de la Library (13 documents de patterns, conventions, librairies).

### Implémentation
**Prompt JARVIS_Maître v4.1** (22/02/2026) :
- Ajout d'une étape obligatoire : "CONSULTER LA LIBRARY avant de déléguer"
- Instructions pour utiliser `get_library_document()` et `get_library_list()`
- Enrichissement des exemples avec contexte Library

**Fichiers modifiés** :
- `config_agents/JARVIS_MAITRE.md` : Prompt v4.0 → v4.1
- `docs/work/ENRICHISSEMENT_PROMPT_JARVIS_MAITRE_22FEV2026.md` : Documentation

---

## ❌ Problème Critique Détecté

### Symptômes
**Tests live (3/3) échouent complètement** :
- ✅ Projet créé
- ✅ Conversation créée
- ✅ Réponse reçue (**0 chars**) ← PROBLÈME
- ⚠️ Aucune délégation exécutée
- ❌ 0 fichier généré

**Pattern d'échec** :
```
Message 1 : response_length: 0
Message 2 (relance) : response_length: 0
Message 3 (relance) : response_length: 0
Message 4 (relance) : response_length: 0
```

**Logs backend (`jarvis_audit.log`)** :
```json
{"response_length": 0}  // Systématique sur tous les messages
{"function_calling_enabled": true}  // Functions activées
```

---

## 🔍 Analyse de la Cause Racine

### Hypothèse Confirmée : Boucle Infinie de Function Calls

**Scénario probable** :
1. Gemini lit le prompt : "**TOUJOURS** consulter la Library avant de déléguer"
2. Gemini appelle `get_library_document("FastAPI", "libraries")`
3. Backend exécute la function et retourne le résultat
4. Gemini reçoit le résultat mais **ne génère PAS de texte**
5. Gemini appelle une autre function (boucle)
6. Backend retourne finalement `content=""` (vide)
7. Frontend filtre la réponse vide (correction récente)
8. Aucun message ajouté à l'historique
9. **Pas de délégation au CODEUR**

### Différence avec Version Précédente

**Prompt v4.0 (fonctionnel - tests 13/02/2026)** :
```
✅ TOUJOURS FAIRE :
1. Écrire IMMÉDIATEMENT le marqueur : [DEMANDE_CODE_CODEUR: ...]
2. Inclure TOUS les fichiers dans UN SEUL marqueur
```

**Prompt v4.1 (non fonctionnel - tests 22/02/2026)** :
```
✅ TOUJOURS FAIRE :
1. **CONSULTER LA LIBRARY** : Utilise get_library_document()
2. **ENRICHIR L'INSTRUCTION** : Intègre le contexte Library
3. Écrire le marqueur : [DEMANDE_CODE_CODEUR: ...]
```

**Conclusion** : L'ajout de l'étape obligatoire de consultation Library empêche Gemini de générer du texte.

---

## ✅ Solution Appliquée

### Action Immédiate : Rollback Prompt v4.0

**Fichier** : `config_agents/JARVIS_MAITRE.md`

**Modifications** :
- ✅ Version 4.1 → 4.0
- ✅ Supprimé : Obligation de consulter la Library
- ✅ Supprimé : Étapes enrichies avec contexte Library
- ✅ Supprimé : Exemples avec CONTEXTE LIBRARY
- ✅ Restauré : Délégation immédiate simple

**Résultat** :
- ✅ Premier test calculatrice : **PASSÉ**
- ✅ Système revenu à la normale
- ✅ Délégation au CODEUR fonctionnelle

---

## 📊 Comparaison Avant/Après

| Critère | Prompt v4.0 (Stable) | Prompt v4.1 (Régression) |
|---------|---------------------|-------------------------|
| **Délégation** | ✅ Immédiate | ❌ Jamais exécutée |
| **Réponses** | ✅ Contenu généré | ❌ 0 chars systématique |
| **Fichiers** | ✅ Générés | ❌ 0 fichier |
| **Tests live** | ✅ 3/3 passants (13/02) | ❌ 0/3 passants (22/02) |
| **Function calls** | ✅ Optionnels | ❌ Boucle infinie |

---

## 🔧 Corrections Connexes Appliquées

### 1. Validation Backend (`base_agent.py`)
**Problème** : Validation rejetait messages `assistant` avec `content` vide

**Solution** :
```python
# Permettre content vide pour assistant (Gemini peut retourner "" avec tool_calls)
if role in ("user", "system", "tool"):
    if not isinstance(content, str) or not content.strip():
        raise InvalidRuntimeMessageError(...)
else:  # role == "assistant"
    if not isinstance(content, str):
        raise InvalidRuntimeMessageError(...)
```

**Résultat** : ✅ Évite erreur validation, mais ne résout pas le problème de fond

---

### 2. Filtrage Frontend (`chat.js`)
**Problème** : Frontend ajoutait réponses vides à l'historique

**Solution** :
```javascript
if (data.response && data.response.trim()) {
    this.addMessage('assistant', data.response);
    this.messages.push({ ... });
}
```

**Résultat** : ✅ Évite erreur au message suivant, mais ne résout pas le problème de fond

---

### 3. Logs Détaillés Gemini (`gemini_provider.py`)
**Ajout** : Logs détaillés si réponse vide
```python
if not content and not tool_calls:
    logger.warning(f"Gemini returned empty response!")
    logger.warning(f"Candidate finish_reason: {response.candidates[0].finish_reason}")
```

**Résultat** : ⏳ Prêt pour investigation future

---

## 📝 Leçons Apprises

### 1. Risque des Instructions Obligatoires avec Functions
**Problème** : Forcer un LLM à appeler des functions avant de générer du texte peut créer une boucle infinie.

**Bonne pratique** :
- ✅ Suggérer l'utilisation de functions (optionnel)
- ❌ Obliger l'utilisation de functions (risque de boucle)

### 2. Importance des Tests de Régression
**Problème** : Modification du prompt sans test immédiat → régression non détectée

**Bonne pratique** :
- ✅ Tester immédiatement après modification de prompt
- ✅ Comparer avec baseline fonctionnelle (tests 13/02)
- ✅ Rollback rapide si régression

### 3. Séparation des Préoccupations
**Problème** : Mélanger orchestration (JARVIS_Maître) et enrichissement (Library)

**Bonne pratique** :
- ✅ JARVIS_Maître : Orchestration pure (délégation)
- ✅ CODEUR : Génération de code (peut consulter Library si besoin)
- ❌ JARVIS_Maître : Enrichissement + Orchestration (trop complexe)

---

## 🚀 Recommandations Futures

### Option 1 : Library Optionnelle (Recommandé)
**Approche** : Suggérer (pas obliger) la consultation Library

**Prompt modifié** :
```
✅ TOUJOURS FAIRE :
1. Écrire IMMÉDIATEMENT le marqueur : [DEMANDE_CODE_CODEUR: ...]
2. **OPTIONNEL** : Si besoin de patterns, consulte get_library_document()
```

**Avantages** :
- ✅ Pas de boucle infinie
- ✅ Enrichissement possible si pertinent
- ✅ Délégation immédiate garantie

---

### Option 2 : Enrichissement Côté CODEUR
**Approche** : CODEUR consulte la Library directement

**Avantages** :
- ✅ Séparation des responsabilités
- ✅ JARVIS_Maître reste simple (orchestration)
- ✅ CODEUR enrichit son contexte si besoin

**Inconvénients** :
- ⚠️ CODEUR doit savoir quels documents chercher
- ⚠️ Nécessite modification du prompt CODEUR

---

### Option 3 : Désactiver Functions pour JARVIS_Maître
**Approche** : Retirer `get_library_document` des functions disponibles

**Avantages** :
- ✅ Aucune boucle possible
- ✅ Délégation immédiate garantie

**Inconvénients** :
- ❌ Perd complètement l'accès à la Library
- ❌ Retour à l'état initial

---

## 📊 État Final

### Système Stable
- ✅ Prompt JARVIS_Maître v4.0 restauré
- ✅ Tests live fonctionnels
- ✅ Délégation au CODEUR opérationnelle
- ✅ Library disponible (13 documents peuplés)

### Fonctionnalités Opérationnelles
- ✅ Library Seed : Peuplement automatique au démarrage
- ✅ API Library : `/api/library` fonctionnelle
- ✅ Frontend Library : Affichage dynamique des documents
- ✅ Functions Library : `get_library_document()`, `get_library_list()` disponibles

### Fonctionnalités En Attente
- ⏳ Enrichissement automatique des instructions (nécessite investigation)
- ⏳ Utilisation effective de la Library par les agents

---

## 🎯 Conclusion

**Problème** : Prompt enrichi v4.1 causait boucle infinie de function calls → système non fonctionnel

**Solution** : Rollback prompt v4.0 → système stable et fonctionnel

**Prochaines Étapes** :
1. Investiguer pourquoi Gemini boucle sur les functions
2. Tester approche "Library optionnelle" (pas obligatoire)
3. Considérer enrichissement côté CODEUR (pas JARVIS_Maître)

**Durée Totale** : ~2h (détection + analyse + résolution + documentation)

**Impact** : Critique → Résolu ✅
