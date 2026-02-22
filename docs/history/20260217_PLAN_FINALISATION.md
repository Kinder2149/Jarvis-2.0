# 🎯 PLAN FINALISATION JARVIS 2.0 — 4 PHASES

**Date** : 2026-02-17  
**Objectif** : Finaliser, consolider et préparer production  
**Statut Actuel** : ✅ Stabilisation terminée, documentation validée

---

## 📋 ÉTAT ACTUEL VALIDÉ

### ✅ Acquis Stabilisation

**Sécurité** :
- ✅ Protection `can_write_disk()` active et testée
- ✅ Mode CHAT bloque écriture (100% garanti)
- ✅ Phase REFLEXION bloque écriture (100% garanti)
- ✅ Classification SafetyService fonctionnelle (82% couverture)

**Workflow Confirmation** :
- ✅ Cycle complet NON-SAFE → Challenge → Confirmation → Exécution
- ✅ Stockage réponse originale (pas de reconstruction artificielle)
- ✅ Nettoyage automatique actions confirmées
- ✅ Tests end-to-end validés (100%)

**Tests Critiques** :
- ✅ 7/7 tests stabilisation + système (100%)
- ✅ API Mistral réelle testée
- ✅ Écriture fichiers réels validée
- ✅ DB intégration validée

**Documentation** :
- ✅ 4070 lignes documentation technique
- ✅ Architecture alignée avec code réel
- ✅ Protocoles validation formalisés
- ✅ Checklists opérationnelles

**Couverture Modules Critiques** :
- ✅ Orchestration : 78%
- ✅ File Writer : 81%
- ✅ Safety Service : 82%
- ✅ Session State : 62%
- ✅ **Moyenne** : 76%

### ⚠️ Points Restants

**Tests** :
- ⚠️ 51/289 tests échouent (18%)
- ⚠️ API endpoints non testés (0% couverture `api.py`)
- ⚠️ Tests HTTP manquants

**Infrastructure** :
- ⚠️ Database : 35% couverture
- ⚠️ Mistral Client : 46% couverture
- ⚠️ Function Executor : 25% couverture

**Qualité** :
- ⚠️ Ruff non installé
- ⚠️ Formatage non standardisé
- ⚠️ 1 warning pytest (escape sequence)

---

## 🔴 PHASE 1 — SÉCURISATION STRUCTURELLE (OBLIGATOIRE)

**Objectif** : Valider endpoint `/confirm-action` en conditions réelles HTTP

**Priorité** : 🔴 **BLOQUANT PRODUCTION**

**Durée Estimée** : 2-3 heures

### Tâches

#### 1.1 Tests HTTP Endpoint `/confirm-action` ✅ OBLIGATOIRE

**Fichier** : `tests/test_api_confirm_action.py` (à créer)

**Tests Requis** :

1. **Test Confirmation Valide**
   - Créer conversation + projet DEBT
   - Envoyer action NON-SAFE
   - Vérifier challenge généré
   - Appeler `POST /api/conversations/{id}/confirm-action`
   - Vérifier statut 200 OK
   - Vérifier exécution réelle
   - Vérifier nettoyage `_pending_actions`

2. **Test Erreur Conversation Inexistante**
   - Appeler `POST /api/conversations/fake-id/confirm-action`
   - Vérifier statut 404 Not Found
   - Vérifier message erreur

3. **Test Erreur Aucune Action Bloquée**
   - Créer conversation sans action bloquée
   - Appeler `POST /api/conversations/{id}/confirm-action`
   - Vérifier statut 400 Bad Request
   - Vérifier message erreur

4. **Test Double Confirmation**
   - Créer action bloquée
   - Confirmer 1ère fois (OK)
   - Confirmer 2ème fois (erreur)
   - Vérifier statut 400 Bad Request

5. **Test Sécurité Injection**
   - Tenter injection SQL dans conversation_id
   - Tenter injection XSS dans réponse
   - Vérifier protection active

**Outils** :
- `httpx.AsyncClient` pour tests HTTP
- `pytest-asyncio` pour tests async
- Fixture `test_client` avec app FastAPI

**Validation** :
- ✅ 5/5 tests passent
- ✅ Endpoint sécurisé
- ✅ Gestion erreurs complète

**Critère Succès** : 5/5 tests HTTP passent → **GO PRODUCTION**

#### 1.2 Tests Erreurs API Générales

**Fichier** : `tests/test_api_errors.py` (à créer)

**Tests Requis** :

1. **Test 404 Routes Inexistantes**
2. **Test 405 Méthodes Non Autorisées**
3. **Test 422 Validation Pydantic**
4. **Test 500 Erreurs Serveur**

**Validation** : 4/4 tests passent

#### 1.3 Documentation Tests HTTP

**Fichier** : `docs/work/TESTS_HTTP_VALIDATION.md` (à créer)

**Contenu** :
- Résultats tests HTTP
- Preuves sécurité endpoint
- Recommandations production

**Validation** : Document complet avec preuves

### Livrables Phase 1

- [ ] `tests/test_api_confirm_action.py` (5 tests)
- [ ] `tests/test_api_errors.py` (4 tests)
- [ ] `docs/work/TESTS_HTTP_VALIDATION.md`
- [ ] **9/9 tests HTTP passent**

**Décision** : ✅ **GO PRODUCTION** si 9/9 tests passent

---

## 🟠 PHASE 2 — NETTOYAGE DETTE TESTS

**Objectif** : Résoudre 51 tests échoués, atteindre 0 échec

**Priorité** : 🟠 **IMPORTANT** (non bloquant production)

**Durée Estimée** : 1-2 jours

### Tâches

#### 2.1 Audit Tests Échoués

**Fichier** : `docs/work/AUDIT_TESTS_ECHOUES.md` (à créer)

**Actions** :
1. Lister 51 tests échoués avec catégories
2. Identifier tests obsolètes (à supprimer)
3. Identifier tests async mal gérés (à corriger)
4. Identifier tests mauvaise implémentation (à refactor)

**Catégories Attendues** :
- Tests async/await non corrigés (35 tests estimés)
- Tests logs fichiers manquants (10 tests estimés)
- Tests orchestration anciens (6 tests estimés)

**Validation** : Audit complet avec décisions par test

#### 2.2 Suppression Tests Obsolètes

**Critères Obsolescence** :
- Test code supprimé/refactoré
- Test fonctionnalité abandonnée
- Test doublon avec tests récents

**Actions** :
1. Supprimer fichiers tests obsolètes
2. Documenter suppressions dans audit
3. Mettre à jour README tests

**Validation** : Tests obsolètes supprimés, documentation à jour

#### 2.3 Correction Tests Async/Await

**Problème** : Tests appellent coroutines sans `await`

**Exemples Erreurs** :
- `TypeError: object str can't be used in 'await' expression`
- `TypeError: cannot unpack non-iterable coroutine object`
- `AssertionError: assert <coroutine object ...> == 'expected'`

**Solution** :
1. Ajouter `await` devant appels async
2. Décorer tests avec `@pytest.mark.asyncio`
3. Utiliser fixtures async correctement

**Validation** : Tests async corrigés, tous passent

#### 2.4 Correction Tests Logs

**Problème** : `FileNotFoundError: test_audit.log`

**Solution** :
1. Vérifier création répertoire logs dans fixtures
2. Utiliser `tmp_path` pytest pour logs temporaires
3. Nettoyer logs après tests

**Validation** : Tests logs passent

#### 2.5 Refactor Tests Orchestration

**Problème** : Tests orchestration anciens (avant stabilisation)

**Solution** :
1. Aligner tests avec nouvelle architecture
2. Utiliser `SessionState` correctement
3. Mocker `SafetyService` si nécessaire

**Validation** : Tests orchestration passent

### Livrables Phase 2

- [ ] `docs/work/AUDIT_TESTS_ECHOUES.md`
- [ ] Tests obsolètes supprimés (liste documentée)
- [ ] Tests async/await corrigés
- [ ] Tests logs corrigés
- [ ] Tests orchestration refactorés
- [ ] **0 test échoué (289/289 passent)**

**Critère Succès** : 289/289 tests passent (100%)

---

## 🟡 PHASE 3 — STABILISATION INFRASTRUCTURE

**Objectif** : Augmenter couverture infrastructure (27% → 60%+)

**Priorité** : 🟡 **MOYEN** (amélioration qualité)

**Durée Estimée** : 1-2 jours

### Tâches

#### 3.1 Couverture `api.py` (0% → 60%)

**Fichier** : `tests/test_api_endpoints.py` (à créer ou compléter)

**Endpoints à Tester** :

**Projets** :
- `GET /api/projects` (liste projets)
- `POST /api/projects` (créer projet)
- `GET /api/projects/{id}` (détails projet)
- `PUT /api/projects/{id}` (modifier projet)
- `DELETE /api/projects/{id}` (supprimer projet)

**Conversations** :
- `POST /api/projects/{id}/conversations` (créer conversation)
- `GET /api/conversations/{id}` (détails conversation)
- `DELETE /api/conversations/{id}` (supprimer conversation)

**Messages** :
- `POST /api/conversations/{id}/messages` (envoyer message)
- `GET /api/conversations/{id}/messages` (historique messages)

**Fichiers** :
- `GET /api/projects/{id}/files` (liste fichiers)
- `GET /api/projects/{id}/files/content` (contenu fichier)

**Agents** :
- `GET /api/agents` (liste agents)

**Tests Requis** : 15-20 tests HTTP

**Validation** : Couverture `api.py` ≥ 60%

#### 3.2 Couverture `database.py` (35% → 60%)

**Fichier** : `tests/test_database.py` (à compléter)

**Méthodes à Tester** :

**Projets** :
- `create_project()`, `get_project()`, `update_project()`, `delete_project()`
- `list_projects()`

**Conversations** :
- `create_conversation()`, `get_conversation()`, `delete_conversation()`
- `get_conversations_by_project()`

**Messages** :
- `add_message()`, `get_messages()`, `get_conversation_history()`

**Fichiers** :
- `add_file()`, `get_files()`, `delete_file()`

**Tests Requis** : 20-25 tests

**Validation** : Couverture `database.py` ≥ 60%

#### 3.3 Couverture `function_executor.py` (25% → 60%)

**Fichier** : `tests/test_function_executor.py` (à créer)

**Fonctions à Tester** :

**Exécution** :
- `execute_function()` (succès)
- `execute_function()` (erreur)
- `execute_function()` (timeout)

**Functions Disponibles** :
- `get_project_structure()`
- `get_project_file()`
- `write_file()`
- `read_file()`

**Tests Requis** : 10-15 tests

**Validation** : Couverture `function_executor.py` ≥ 60%

### Livrables Phase 3

- [ ] `tests/test_api_endpoints.py` (15-20 tests)
- [ ] `tests/test_database.py` (20-25 tests complétés)
- [ ] `tests/test_function_executor.py` (10-15 tests)
- [ ] Couverture `api.py` ≥ 60%
- [ ] Couverture `database.py` ≥ 60%
- [ ] Couverture `function_executor.py` ≥ 60%
- [ ] **Couverture infrastructure ≥ 60%**

**Critère Succès** : Couverture infrastructure 60%+ (vs 27% actuel)

---

## 🟢 PHASE 4 — HYGIÈNE CODE

**Objectif** : Standardiser qualité code, formater, nettoyer warnings

**Priorité** : 🟢 **FAIBLE** (optionnel, amélioration continue)

**Durée Estimée** : 2-3 heures

### Tâches

#### 4.1 Installer Ruff

**Actions** :
1. `pip install ruff`
2. Créer `pyproject.toml` avec config ruff
3. Ajouter ruff à `requirements.txt`

**Validation** : Ruff installé et configuré

#### 4.2 Formatter Code

**Commandes** :
```bash
ruff format .
```

**Actions** :
1. Formatter tout le code backend
2. Formatter tests
3. Vérifier diff (ne pas casser tests)
4. Commit formatage

**Validation** : Code formaté, tests passent

#### 4.3 Vérifier Warnings Ruff

**Commandes** :
```bash
ruff check .
```

**Actions** :
1. Lister warnings ruff
2. Corriger warnings critiques (imports inutilisés, etc.)
3. Documenter warnings acceptables
4. Configurer ruff pour ignorer warnings acceptables

**Validation** : Warnings critiques corrigés

#### 4.4 Corriger Warnings Pytest

**Warning Actuel** : `DeprecationWarning: invalid escape sequence '\C'`

**Fichier** : `test_live_projects.py:1`

**Solution** : Corriger échappement caractères (utiliser raw string `r"..."`)

**Validation** : 0 warning pytest

#### 4.5 Standardiser Logs

**Actions** :
1. Vérifier format logs cohérent
2. Ajouter logs manquants (confirmation, nettoyage)
3. Standardiser niveaux logs (INFO, WARNING, ERROR)
4. Documenter convention logs

**Validation** : Logs standardisés, documentation à jour

### Livrables Phase 4

- [ ] Ruff installé et configuré
- [ ] Code formaté (`ruff format .`)
- [ ] Warnings ruff critiques corrigés
- [ ] Warning pytest corrigé
- [ ] Logs standardisés
- [ ] `docs/work/CONVENTION_LOGS.md` (à créer)

**Critère Succès** : Code formaté, 0 warning critique

---

## 📊 MÉTRIQUES CIBLES

### Tests

| Métrique | Actuel | Cible Phase 1 | Cible Phase 2 |
|----------|--------|---------------|---------------|
| Tests critiques | 7/7 (100%) | 16/16 (100%) | 16/16 (100%) |
| Tests globaux | 238/289 (82%) | 247/298 (83%) | 298/298 (100%) |
| Tests HTTP | 0 | 9 | 9 |

### Couverture

| Module | Actuel | Cible Phase 3 |
|--------|--------|---------------|
| Orchestration | 78% | 78% ✅ |
| File Writer | 81% | 81% ✅ |
| Safety Service | 82% | 82% ✅ |
| Session State | 62% | 62% ✅ |
| **API** | **0%** | **60%** |
| **Database** | **35%** | **60%** |
| **Function Executor** | **25%** | **60%** |
| **Infrastructure** | **27%** | **60%** |
| **Globale** | **40%** | **55%** |

### Qualité

| Métrique | Actuel | Cible Phase 4 |
|----------|--------|---------------|
| Ruff installé | ❌ | ✅ |
| Code formaté | ❌ | ✅ |
| Warnings ruff critiques | ? | 0 |
| Warnings pytest | 1 | 0 |
| Logs standardisés | ⚠️ | ✅ |

---

## 🎯 CRITÈRES VALIDATION GLOBALE

### Phase 1 (Bloquant Production)

**Critère GO PRODUCTION** :
- ✅ 9/9 tests HTTP passent
- ✅ Endpoint `/confirm-action` sécurisé
- ✅ Gestion erreurs complète

**Si échec** : ❌ **NO-GO PRODUCTION** (corriger avant déploiement)

### Phase 2 (Important)

**Critère Qualité** :
- ✅ 0 test échoué (289/289 passent)
- ✅ Tests obsolètes supprimés
- ✅ Dette tests résolue

**Si échec** : ⚠️ Production possible mais qualité dégradée

### Phase 3 (Amélioration)

**Critère Couverture** :
- ✅ Couverture infrastructure ≥ 60%
- ✅ Couverture globale ≥ 55%

**Si échec** : ⚠️ Production possible mais couverture faible

### Phase 4 (Optionnel)

**Critère Hygiène** :
- ✅ Code formaté
- ✅ 0 warning critique

**Si échec** : ⚠️ Production possible mais hygiène à améliorer

---

## 📅 PLANNING RECOMMANDÉ

### Semaine 1 : Phases 1 + 2

**Jour 1-2** : Phase 1 (Sécurisation)
- Tests HTTP endpoint `/confirm-action`
- Tests erreurs API
- Validation sécurité

**Jour 3-5** : Phase 2 (Dette Tests)
- Audit tests échoués
- Suppression tests obsolètes
- Correction tests async/await
- Correction tests logs
- Refactor tests orchestration

**Livrable Semaine 1** : ✅ GO PRODUCTION + 0 test échoué

### Semaine 2 : Phases 3 + 4

**Jour 1-3** : Phase 3 (Infrastructure)
- Tests API endpoints
- Tests database
- Tests function_executor
- Mesure couverture

**Jour 4-5** : Phase 4 (Hygiène)
- Installer ruff
- Formatter code
- Corriger warnings
- Standardiser logs

**Livrable Semaine 2** : ✅ Couverture 55%+ + Code formaté

---

## 🚀 PROCHAINES ÉTAPES

### Immédiat (Avant Codage)

1. **Analyser État Réel Projet**
   - Lister exactement les 51 tests échoués
   - Identifier modules infrastructure à tester
   - Vérifier dépendances manquantes

2. **Valider Plan avec Utilisateur**
   - Confirmer priorités phases
   - Ajuster planning si nécessaire
   - Valider critères succès

3. **Préparer Environnement**
   - Installer dépendances tests (`httpx`, `pytest-asyncio`)
   - Vérifier serveur test disponible
   - Préparer fixtures communes

### Après Validation Plan

4. **Démarrer Phase 1**
   - Créer `tests/test_api_confirm_action.py`
   - Implémenter 5 tests HTTP
   - Valider sécurité endpoint

---

## 📝 NOTES IMPORTANTES

### Règles Exécution

1. **Pas de code avant plan validé** : Analyser état réel d'abord
2. **Phase 1 obligatoire** : Bloquant production
3. **Phases 2-4 séquentielles** : Terminer phase avant suivante
4. **Tests avant corrections** : Écrire tests d'abord, corriger ensuite
5. **Documentation continue** : Documenter chaque phase

### Risques Identifiés

1. **Tests HTTP complexes** : Nécessitent serveur test + fixtures
2. **51 tests échoués** : Audit peut révéler plus de travail
3. **Couverture infrastructure** : Peut nécessiter refactor code
4. **Ruff formatage** : Peut casser tests si mal configuré

### Mitigations

1. Utiliser `httpx.AsyncClient` avec app FastAPI (pas de serveur)
2. Audit détaillé avant corrections (éviter surprises)
3. Tests incrémentaux (module par module)
4. Vérifier tests après formatage (commit séparé)

---

**Plan finalisation 4 phases** : ✅ **COMPLET**  
**Date** : 2026-02-17  
**Prêt pour** : Analyse état réel projet + validation utilisateur

---

## 🎯 RÉSUMÉ EXÉCUTIF

**4 Phases Structurées** :
- 🔴 Phase 1 : Sécurisation (2-3h) — **BLOQUANT PRODUCTION**
- 🟠 Phase 2 : Dette tests (1-2j) — **IMPORTANT**
- 🟡 Phase 3 : Infrastructure (1-2j) — **AMÉLIORATION**
- 🟢 Phase 4 : Hygiène (2-3h) — **OPTIONNEL**

**Durée Totale Estimée** : 5-7 jours

**Critère GO PRODUCTION** : Phase 1 terminée (9/9 tests HTTP passent)

**Objectif Final** : 298/298 tests (100%), couverture 55%+, code formaté
