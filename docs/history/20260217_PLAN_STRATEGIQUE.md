# 📋 PLAN STRATÉGIQUE — ALIGNEMENT VISION PRODUIT JARVIS 2.0

**Date** : 2026-02-17  
**Mission** : Planification complète de l'alignement système avec vision produit validée  
**Statut** : PLAN EXHAUSTIF PRÊT POUR IMPLÉMENTATION

---

## 📊 RÉSUMÉ EXÉCUTIF

**Objectif** : Aligner intégralement le système JARVIS avec la vision produit validée.

**Écarts identifiés** : **12 écarts majeurs** entre implémentation actuelle et vision validée

**Complexité estimée** : **MOYENNE** (6 phases, 47 modifications, 15-20 jours)

**Risques** : **FAIBLES** (architecture robuste, pas de refonte majeure)

---

## 1️⃣ ÉTAT DES LIEUX TECHNIQUE RÉEL

### Architecture Backend Actuelle

**Stack** : FastAPI + SQLite + Mistral AI Agent API  
**Agents** : BASE, CODEUR, VALIDATEUR, JARVIS_Maître  
**Tests** : 193 tests unitaires (tous passent)

### Flux Actuel Mode CHAT

✅ **CONFORME** : Pas d'orchestration, pas d'écriture disque

### Flux Actuel Mode PROJET

⚠️ **PARTIELLEMENT CONFORME** : Orchestration active, écriture disque autorisée, mais manque gestion phases RÉFLEXION/EXÉCUTION

### Incohérences Identifiées (12 écarts)

1. Pas de gestion d'état mode/phase
2. Pas de détection phase RÉFLEXION/EXÉCUTION
3. Pas de blocage écriture disque en RÉFLEXION
4. Pas de détection actions SAFE/NON-SAFE
5. Pas de challenge utilisateur automatique
6. Pas de détection dette technique automatique
7. Pas de détection état projet (nouveau/propre/avec dette)
8. Prompt JARVIS_Maître contradictoire (délégation immédiate)
9. Pas de gate validation bloquant
10. Contexte projet trop limité
11. Pas d'indicateur visuel mode/phase (frontend)
12. Pas de workflow Réflexion → Validation → Exécution

---

## 2️⃣ ÉCARTS STRATÉGIQUES

### Conformes ✅

- Architecture backend robuste
- Orchestration délégation fonctionnelle
- Écriture fichiers sécurisée
- Détermination mode par frontend
- 4 agents fixes

### Non Conformes 🔴

- Gestion phases RÉFLEXION/EXÉCUTION
- Détection dette technique
- Classification actions SAFE/NON-SAFE
- Challenge utilisateur automatique
- Détection état projet

---

## 3️⃣ PLAN DE TRANSFORMATION

### PHASE A — NETTOYAGE (1 jour)

**A.1** Archiver `JARVIS_Base_Document_Complet.md` → `docs/history/`  
**A.2** Mettre à jour `README.md` (référence nouveau doc officiel)  
**A.3** Corriger prompt JARVIS_Maître (supprimer "délégation immédiate", ajouter "délégation intelligente")

### PHASE B — MISE EN CONFORMITÉ ARCHITECTURE (5 jours)

**B.1** Créer `backend/models/session_state.py` (SessionState, Mode, Phase, ProjectState)  
**B.2** Créer `backend/services/project_analyzer.py` (détection état projet)  
**B.3** Créer `backend/services/debt_analyzer.py` (audit dette technique)  
**B.4** Créer `backend/services/safety_classifier.py` (classification SAFE/NON-SAFE)  
**B.5** Créer `backend/services/user_challenger.py` (génération messages challenge)  
**B.6** Adapter `backend/api.py` (injection SessionState, classification, challenge)  
**B.7** Adapter `backend/services/orchestration.py` (blocage écriture en RÉFLEXION)  
**B.8** Enrichir `backend/services/project_context.py` (état projet + dette)

### PHASE C — RÉVISION AGENTS MISTRAL (2 jours)

**C.1** JARVIS_Maître : Remplacer délégation immédiate par délégation intelligente  
**C.2** BASE : Aucune modification (conforme)  
**C.3** CODEUR : Aucune modification (conforme)  
**C.4** VALIDATEUR : Aucune modification (conforme)

### PHASE D — SÉCURISATION EXÉCUTION (2 jours)

**D.1** Créer `backend/services/validation_gate.py` (gate validation bloquant - optionnel)  
**D.2** Enrichir logs audit (ajout mode/phase/project_state)  
**D.3** Ajouter gestion erreurs robuste (try/except services)

### PHASE E — TESTS ET VALIDATION (3 jours)

**E.1** Tests Mode CHAT (3 tests)  
**E.2** Tests Mode PROJET RÉFLEXION (3 tests)  
**E.3** Tests Mode PROJET EXÉCUTION SAFE (3 tests)  
**E.4** Tests Mode PROJET EXÉCUTION NON-SAFE (3 tests)  
**E.5** Tests Mode PROJET Avec Dette (3 tests)  
**E.6** Tests Régression (193 tests existants)

### PHASE F — ORDRE D'IMPLÉMENTATION

**Semaine 1** : Fondations (A + B.1-B.4)  
**Semaine 2** : Intégration Backend (B.5-B.8 + C)  
**Semaine 3** : Sécurisation + Tests (D + E.1-E.4)  
**Semaine 4** : Validation + Déploiement (E.5-E.6 + corrections + déploiement)

**Durée totale** : 15-20 jours

---

## 4️⃣ FICHIERS IMPACTÉS

### Nouveaux Fichiers (6)

- `backend/models/session_state.py` (~80 lignes)
- `backend/services/project_analyzer.py` (~60 lignes)
- `backend/services/debt_analyzer.py` (~120 lignes)
- `backend/services/safety_classifier.py` (~80 lignes)
- `backend/services/user_challenger.py` (~40 lignes)
- `backend/services/validation_gate.py` (~50 lignes)

**Total** : ~430 lignes + 70 tests

### Fichiers Modifiés (5)

- `backend/api.py` (~120 lignes impactées)
- `backend/services/orchestration.py` (~220 lignes impactées)
- `backend/services/project_context.py` (~74 lignes impactées)
- `backend/agents/base_agent.py` (~25 lignes impactées)
- `config_mistral/agents/JARVIS_MAITRE.md` (~30 lignes impactées)

**Total** : ~469 lignes modifiées

---

## 5️⃣ AGENTS MISTRAL À MODIFIER

### JARVIS_Maître (CRITIQUE)

**Agent ID** : ag_019c514a04a874159a21135b856a40e3  
**Modifications** :
- ❌ Supprimer : "RÈGLE ABSOLUE — DÉLÉGATION IMMÉDIATE"
- ✅ Ajouter : Section "DÉLÉGATION INTELLIGENTE" (règles SAFE/NON-SAFE)
- ✅ Ajouter : Section "CHALLENGE UTILISATEUR" (format + exemples)

**Déploiement** : Mistral Console → Instructions → Coller nouveau prompt → Sauvegarder

### Autres Agents

- BASE : ✅ Conforme (aucune modification)
- CODEUR : ✅ Conforme (aucune modification)
- VALIDATEUR : ✅ Conforme (aucune modification)

---

## 6️⃣ RISQUES TECHNIQUES

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Régression tests existants | MOYENNE | ÉLEVÉ | Tests régression après chaque phase |
| Performance debt_analyzer | FAIBLE | MOYEN | Limiter analyse à .py, .js |
| Faux positifs SafetyClassifier | MOYENNE | MOYEN | Affiner mots-clés après tests |
| Désynchronisation prompts Mistral | MOYENNE | ÉLEVÉ | Versionner prompts, checklist déploiement |

---

## 7️⃣ VALIDATION FINALE

### Checklist Cohérence

- ✅ Modes explicites (route frontend uniquement)
- ✅ Pas d'écriture en mode CHAT
- ✅ Pas d'écriture en phase RÉFLEXION (après implémentation)
- ✅ Challenge si action NON-SAFE (après implémentation)
- ✅ Détection dette automatique (après implémentation)
- ✅ 4 agents fixes (aucun ajout)

### Critères de Succès

1. ✅ 193 tests unitaires existants passent (aucune régression)
2. ✅ 15 nouveaux tests fonctionnels passent (modes/phases)
3. ✅ Prompt JARVIS_Maître déployé et testé
4. ✅ Documentation officielle à jour
5. ✅ Validation utilisateur finale (Val C.)

---

**FIN DU PLAN STRATÉGIQUE**
