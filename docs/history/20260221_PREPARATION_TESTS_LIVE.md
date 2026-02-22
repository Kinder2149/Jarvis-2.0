# Préparation Tests Live - État des Lieux

**Date** : 2026-02-21
**Objectif** : Valider l'orchestration complète avec Gemini

---

## ✅ État Configuration

### Providers Configurés
- ✅ Gemini API Key : Configurée
- ✅ Tous agents → Gemini (gratuit)
- ✅ Prompts provider-agnostic chargés
- ✅ Tests unitaires : 19/19 passent

### Agents Paramétrés
- ✅ JARVIS_Maître : Gemini, temp 0.3, prompt chargé, délégation OK
- ✅ BASE : Gemini, temp 0.7, prompt chargé
- ✅ CODEUR : Gemini, temp 0.3, prompt chargé
- ✅ VALIDATEUR : Gemini, temp 0.5, prompt chargé

---

## ⚠️ Orchestration - À Vérifier

### Fichiers Clés
- `backend/services/orchestration.py` : ✅ Existe
- `backend/api.py` : ⚠️ À vérifier intégration
- `tests/live/test_live_projects.py` : ✅ Existe

### Points à Valider
1. **Orchestration activée dans API** : Vérifier que `SimpleOrchestrator` est utilisé
2. **Marqueurs détectés** : `[DEMANDE_CODE_CODEUR:]`, `[DEMANDE_VALIDATION_BASE:]`
3. **Boucle itérative** : CODEUR → BASE → validation
4. **Écriture fichiers** : `file_writer.py` fonctionnel

---

## 🎯 Tests Live Disponibles

### Test 1 : Calculatrice (Simple)
**Fichier** : `tests/live/test_live_projects.py::test_calculatrice`
**Attendu** : 4 fichiers Python
**Complexité** : Faible

### Test 2 : TODO App (Moyen)
**Fichier** : `tests/live/test_live_projects.py::test_todo`
**Attendu** : 6 fichiers Python
**Complexité** : Moyenne

### Test 3 : MiniBlog (Complexe)
**Fichier** : `tests/live/test_live_projects.py::test_miniblog`
**Attendu** : 6+ fichiers Python
**Complexité** : Élevée

---

## 📋 Checklist Avant Tests Live

### Configuration
- [x] `.env` configuré avec Gemini
- [x] Tous agents → Gemini
- [x] Prompts chargés dynamiquement
- [ ] Orchestration vérifiée dans `api.py`

### Backend
- [x] Providers fonctionnels (15/15 tests)
- [x] Agents fonctionnels (4/4 tests)
- [ ] Orchestration intégrée dans `/chat`
- [ ] Backend démarré sur localhost:8000

### Tests
- [x] Tests unitaires providers : 15/15 ✅
- [x] Tests intégration Gemini : 4/4 ✅
- [ ] Backend démarré pour tests live
- [ ] Dossier `D:\Coding\TEST` créé

---

## 🚀 Plan de Lancement

### Étape 1 : Vérifier Orchestration
```bash
# Vérifier que SimpleOrchestrator est utilisé dans api.py
grep -n "SimpleOrchestrator\|process_response" backend/api.py
```

### Étape 2 : Démarrer Backend
```bash
# Terminal 1 : Démarrer serveur
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

### Étape 3 : Créer Dossier Test
```bash
# Créer dossier pour projets de test
New-Item -ItemType Directory -Path "D:\Coding\TEST" -Force
```

### Étape 4 : Lancer Test Simple
```bash
# Terminal 2 : Test calculatrice (simple)
pytest tests/live/test_live_projects.py::test_calculatrice -v -s
```

### Étape 5 : Analyser Résultats
- Vérifier fichiers créés dans `D:\Coding\TEST\calculatrice\`
- Vérifier logs backend
- Vérifier délégation JARVIS_Maître → CODEUR

---

## ⚠️ Différences Architecture Mistral vs Gemini

### Mistral (Ancien)
- Agent IDs cloud (ag_019c514a...)
- Prompts configurés sur Mistral Console
- Function calling via API Mistral
- Conversations persistantes

### Gemini (Actuel)
- Pas d'Agent IDs
- Prompts chargés localement
- Function calling via abstraction provider
- Conversations gérées par backend

### Impact sur Orchestration
- ✅ Marqueurs de délégation : Identiques
- ✅ Boucle CODEUR/BASE : Identique
- ⚠️ Function calling : Format différent (géré par providers)
- ⚠️ Contexte : Pas de persistance cloud (géré par backend)

---

## 🔍 Points de Vigilance

### 1. Function Calling
**Problème potentiel** : Format functions différent Gemini vs Mistral
**Solution** : `GeminiProvider.format_functions()` gère la conversion

### 2. Contexte Limité
**Problème potentiel** : Gemini 2.5 Flash = 1M tokens context
**Solution** : Largement suffisant pour projets simples

### 3. Quotas Gemini
**Problème potentiel** : 15 RPM, 1M TPM
**Solution** : Ajouter retry avec backoff si quota dépassé

### 4. Orchestration Backend
**Problème potentiel** : `SimpleOrchestrator` peut référencer ancien `MistralClient`
**Solution** : Vérifier et adapter si nécessaire

---

## 📝 Actions Immédiates

### 1. Vérifier Orchestration dans API
```bash
grep -A 10 "def chat" backend/api.py | grep -i orchestr
```

### 2. Vérifier Imports Orchestration
```bash
grep "from.*orchestration import\|import.*orchestration" backend/api.py
```

### 3. Tester Backend Démarre
```bash
uvicorn backend.app:app --reload --port 8000
```

---

## 🎯 Critères de Succès

### Test Calculatrice (Minimum)
- [ ] Backend démarre sans erreur
- [ ] JARVIS_Maître reçoit demande
- [ ] Marqueur `[DEMANDE_CODE_CODEUR:]` détecté
- [ ] CODEUR génère 4 fichiers
- [ ] Fichiers écrits dans `D:\Coding\TEST\calculatrice\`
- [ ] Tests pytest passent (5/5)

### Test TODO (Optimal)
- [ ] 6 fichiers générés
- [ ] Tests pytest passent (10/11 minimum)
- [ ] Validation BASE fonctionne

### Test MiniBlog (Excellence)
- [ ] 6+ fichiers générés
- [ ] Architecture FastAPI complète
- [ ] Tests pytest passent (majorité)

---

## 🚨 Problèmes Potentiels

### Si Backend Ne Démarre Pas
1. Vérifier imports providers
2. Vérifier `.env` copié
3. Vérifier dépendances installées

### Si Orchestration Ne Fonctionne Pas
1. Vérifier `SimpleOrchestrator` dans `api.py`
2. Vérifier marqueurs détectés dans logs
3. Vérifier agents appelés

### Si Fichiers Non Créés
1. Vérifier `file_writer.py` fonctionne
2. Vérifier permissions dossier `D:\Coding\TEST`
3. Vérifier parsing code blocks

---

## 📊 Métriques Attendues

### Performance
- Temps génération calculatrice : ~30-60s
- Temps génération TODO : ~60-120s
- Temps génération MiniBlog : ~120-180s

### Qualité
- Code propre avec docstrings : ✅
- Tests unitaires inclus : ✅
- Gestion erreurs : ✅
- Type hints : ✅

---

## Prochaine Étape

**Vérifier orchestration dans `api.py` et démarrer backend**
