# PLAN DE CORRECTION COMPLET — JARVIS 2.0

**Date** : 2026-02-16  
**Basé sur** : Audit externe complet du système JARVIS 2.0  
**Objectif** : Résoudre tous les problèmes de cohérence identifiés  
**Durée estimée** : 20h réparties sur 5 phases  
**Score actuel** : 6.5/10 → **Score cible** : 9/10

---

## RÉSUMÉ EXÉCUTIF

### Problèmes critiques à résoudre

1. **JARVIS_Maître ne délègue pas systématiquement** → Fait des audits au lieu de déléguer
2. **CODEUR génère du code de mauvaise qualité** → Tests échouent, fichiers écrasés
3. **Timeouts 900s insuffisants** → 3/5 étapes NoteKeeper en timeout
4. **Boucle de vérification BASE fragile** → Dépend d'un parsing regex
5. **Système non générique** → Biaisé vers Python + FastAPI + pytest

### Approche de correction

**Principe** : Corrections **incrémentales et testées** à chaque étape. Pas de refonte massive.

**Ordre de priorité** :
1. Prompts agents (impact immédiat sur comportement)
2. Orchestration backend (fiabilité)
3. Performance (timeouts)
4. Généricité (capacité multi-projets)
5. Validation complète

---

## PHASE 1 : SIMPLIFICATION PROMPTS AGENTS (CRITIQUE)

**Durée** : 4h  
**Impact** : CRITIQUE  
**Objectif** : Prompts clairs, concis, sans ambiguïté

### Actions détaillées

#### 1.1 JARVIS_Maître (349 → 150 lignes)
- Créer `config_mistral/agents/JARVIS_MAITRE_V3.md`
- Retirer toute mention d'audit/plan
- 1 seule section "DÉLÉGATION IMMÉDIATE" en haut
- Workflow reprise projet en 4 étapes claires
- Déployer sur Mistral Console

#### 1.2 CODEUR (561 → 250 lignes)
- Créer `config_mistral/agents/CODEUR_V2.md`
- Retirer patterns génériques (131 lignes) → Knowledge Base
- Rendre validation obligatoire (pas "recommandé")
- Procédure obligatoire : get_project_structure() TOUJOURS
- Activer Code Interpreter sur Mistral Console

#### 1.3 BASE (194 → 120 lignes)
- Créer `config_mistral/agents/BASE_V2.md`
- Simplifier section "RAPPORT DE CODE"
- Rapport max 2000 chars (pas 500)

#### 1.4 VALIDATEUR (nouveau, 100 lignes)
- Créer `config_mistral/agents/VALIDATEUR.md`
- Agent spécialisé validation qualité
- Créer sur Mistral Console
- Ajouter `JARVIS_VALIDATEUR_AGENT_ID` dans `.env`

### Livrables Phase 1
- 4 prompts agents simplifiés
- 2 documents Knowledge Base (patterns Python/JS)
- 4 agents déployés sur Mistral Console
- Tests validation pour chaque agent

---

## PHASE 2 : AMÉLIORATION ORCHESTRATION

**Durée** : 6h  
**Impact** : ÉLEVÉ  
**Objectif** : Orchestration fiable, vérification robuste

### Actions détaillées

#### 2.1 Extraction fichiers (4 stratégies)
- Modifier `_extract_expected_files()` dans `orchestration.py`
- Ajouter 3 stratégies : listes explicites, arborescence, markdown
- Créer `tests/test_orchestration_extraction.py` (5 tests)

#### 2.2 Vérification complétude renforcée
- Améliorer prompt vérification BASE (procédure 4 étapes)
- Validation locale renforcée (3 types de matching)

#### 2.3 Parsing markdown robuste
- Ajouter logging détaillé si 0 fichiers détectés
- Détecter patterns alternatifs pour diagnostic

#### 2.4 Gestion erreurs
- Remonter erreurs dans réponse finale à JARVIS_Maître
- Format : "❌ ERREUR : [détails]"

#### 2.5 Intégrer VALIDATEUR dans boucle
- Après vérification complétude, appeler VALIDATEUR
- Si INVALIDE, demander correction au CODEUR
- Reboucler jusqu'à validation OK

### Livrables Phase 2
- `orchestration.py` modifié (5 améliorations)
- `file_writer.py` modifié (logging)
- `tests/test_orchestration_extraction.py`
- Tests : 5/5 passent

---

## PHASE 3 : OPTIMISATION PERFORMANCE

**Durée** : 4h  
**Impact** : ÉLEVÉ  
**Objectif** : Réduire timeouts de 50%

### Actions détaillées

#### 3.1 Compression contexte projet
- Modifier `build_project_context_message()` dans `project_context.py`
- Limiter arborescence : max 3 niveaux, 50 fichiers
- Ajouter message : "Utilise get_project_structure() pour voir complet"

#### 3.2 Optimisation historique conversation
- Modifier `_optimize_history()` dans `mistral_client.py`
- Compresser messages > 2000 chars (garder début + fin)
- Ajouter méthode `_compress_message()`

#### 3.3 Timeout adaptatif
- Augmenter `API_TIMEOUT` de 60s à 120s
- Timeout adaptatif : 120s + 1s par 1000 chars (max 300s)

#### 3.4 Max iterations function calling
- Augmenter de 7 à 15 iterations
- Détecter appels répétitifs (même function 3+ fois)
- Arrêt forcé avec message explicite

#### 3.5 Retry logic amélioré
- Logger WARNING à chaque retry
- Logger succès après N tentatives

### Livrables Phase 3
- `project_context.py` modifié
- `mistral_client.py` modifié (3 améliorations)
- Tests performance : timeouts réduits 50%

---

## PHASE 4 : AMÉLIORATION GÉNÉRICITÉ

**Durée** : 4h  
**Impact** : MOYEN  
**Objectif** : Support multi-langages (Python, JavaScript, TypeScript)

### Actions détaillées

#### 4.1 Retirer règles spécifiques
- Déplacer "Storage JSON" et "Frontend HTML/JS" vers Knowledge Base
- Créer `docs/knowledge_base/REGLES_STORAGE_JSON.md`
- Créer `docs/knowledge_base/REGLES_FRONTEND_HTML_JS.md`
- Modifier prompt CODEUR : règles contextuelles

#### 4.2 Support JavaScript/TypeScript
- Créer `docs/knowledge_base/PATTERNS_JAVASCRIPT.md`
- Patterns : Express API, React Component, Jest Tests
- Modifier prompt CODEUR : mentionner JavaScript

#### 4.3 Détection automatique langage/framework
- Créer `backend/services/project_detector.py`
- Méthodes : `detect_language()`, `detect_framework()`, `get_project_info()`
- Intégrer dans `build_project_context_message()`

#### 4.4 Tests multi-langages
- Créer `tests/test_live_express_api.py` (API Express)
- Créer `tests/test_live_react_app.py` (App React)
- Vérifier : génération code JavaScript OK

### Livrables Phase 4
- 3 documents Knowledge Base (règles spécifiques)
- `project_detector.py` (nouveau service)
- `project_context.py` modifié (détection auto)
- 2 tests live JavaScript

---

## PHASE 5 : VALIDATION ET TESTS COMPLETS

**Durée** : 2h  
**Impact** : CRITIQUE  
**Objectif** : Valider toutes les corrections

### Actions détaillées

#### 5.1 Tests unitaires complets
- Exécuter tous les tests : `pytest tests/ -v`
- Vérifier : 200+ tests passent
- Corriger tests cassés si nécessaire

#### 5.2 Tests live NoteKeeper (5 étapes)
- Exécuter `python test_live_notekeeper.py`
- Vérifier : 5/5 étapes réussies (vs 0/5 avant)
- Timeouts < 300s par étape (vs 900s avant)

#### 5.3 Tests live multi-projets
- Calculatrice Python : 5/5 tests ✅
- TODO Python : 11/11 tests ✅
- MiniBlog Python : 15/15 tests ✅
- API Express JavaScript : 8/8 tests ✅
- App React JavaScript : 10/10 tests ✅

#### 5.4 Documentation mise à jour
- Mettre à jour `JARVIS_Base_Document_Complet.md`
- Mettre à jour `docs/_meta/CHANGELOG.md`
- Mettre à jour `docs/_meta/INDEX.md`
- Créer `docs/reference/ARCHITECTURE_V3.md`

#### 5.5 Validation finale
- Vérifier cohérence prompts cloud vs locaux
- Vérifier configuration Mistral Console (4 agents)
- Vérifier `.env` complet (4 Agent IDs)

### Livrables Phase 5
- Tests unitaires : 200+/200+ ✅
- Tests live : 5/5 projets ✅
- Documentation à jour
- Rapport validation final

---

## CRITÈRES DE SUCCÈS GLOBAUX

### Avant corrections (état actuel)
- Score cohérence : 6.5/10
- Tests NoteKeeper : 0/5 étapes
- Timeouts : 3/5 étapes (900s)
- Qualité code : 4/10
- Généricité : 5/10 (Python seulement)

### Après corrections (cible)
- Score cohérence : **9/10** ✅
- Tests NoteKeeper : **5/5 étapes** ✅
- Timeouts : **0/5 étapes** (< 300s) ✅
- Qualité code : **8/10** ✅
- Généricité : **8/10** (Python + JavaScript) ✅

---

## ORDRE D'EXÉCUTION RECOMMANDÉ

### Semaine 1 (10h)
- **Jour 1-2** : Phase 1 (4h) — Simplification prompts
- **Jour 3-4** : Phase 2 (6h) — Amélioration orchestration

### Semaine 2 (10h)
- **Jour 5-6** : Phase 3 (4h) — Optimisation performance
- **Jour 7-8** : Phase 4 (4h) — Amélioration généricité
- **Jour 9** : Phase 5 (2h) — Validation complète

---

## RISQUES ET MITIGATIONS

### Risque 1 : Régression sur tests existants
**Probabilité** : MOYENNE  
**Impact** : ÉLEVÉ  
**Mitigation** : Exécuter tests unitaires après chaque phase

### Risque 2 : Prompts trop courts = perte de contexte
**Probabilité** : FAIBLE  
**Impact** : MOYEN  
**Mitigation** : Tester chaque prompt avant déploiement

### Risque 3 : Timeouts persistent malgré optimisations
**Probabilité** : FAIBLE  
**Impact** : ÉLEVÉ  
**Mitigation** : Monitoring détaillé, ajuster paramètres si nécessaire

---

## CHECKLIST VALIDATION FINALE

### Prompts agents
- [ ] JARVIS_Maître v3.0 : 150 lignes, délégation immédiate
- [ ] CODEUR v2.0 : 250 lignes, validation obligatoire
- [ ] BASE v2.0 : 120 lignes, rapport 2000 chars
- [ ] VALIDATEUR v1.0 : 100 lignes, détection erreurs

### Orchestration
- [ ] Extraction fichiers : 4 stratégies
- [ ] Vérification complétude : 3 types matching
- [ ] Parsing markdown : logging détaillé
- [ ] VALIDATEUR intégré dans boucle

### Performance
- [ ] Contexte projet : max 3 niveaux, 50 fichiers
- [ ] Historique : messages compressés 2000 chars
- [ ] Timeout adaptatif : 120s + 1s/1000 chars
- [ ] Max iterations : 15, détection répétitions

### Généricité
- [ ] Règles spécifiques → Knowledge Base
- [ ] Support JavaScript/TypeScript
- [ ] Détection auto langage/framework
- [ ] Tests multi-langages

### Tests
- [ ] Tests unitaires : 200+/200+
- [ ] Tests live NoteKeeper : 5/5
- [ ] Tests live multi-projets : 5/5
- [ ] Documentation à jour

---

**FIN DU PLAN DE CORRECTION COMPLET**
