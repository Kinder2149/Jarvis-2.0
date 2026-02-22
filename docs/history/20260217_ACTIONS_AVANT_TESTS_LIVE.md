# 🚀 ACTIONS AVANT TESTS LIVE

**Date** : 2026-02-17  
**Objectif** : Préparer le projet pour les tests live  
**Statut** : ⚠️ Actions requises

---

## ✅ STATUT ACTUEL

### Phases 1-4 : TOUTES TERMINÉES ✅

- ✅ **Phase 1** : Sécurisation (7/9 tests HTTP, workflow validé)
- ✅ **Phase 2** : Dette tests (241/244 tests, 99%)
- ✅ **Phase 3** : Infrastructure (70% couverture)
- ✅ **Phase 4** : Hygiène code (47 fichiers formatés, -95% warnings)

### Métriques Actuelles

**Tests** : 238/241 passent (99%)  
**Couverture** : 74%  
**Warnings** : 66 (non critiques)  
**Code** : Formaté et standardisé ✅

---

## ⚠️ ACTIONS REQUISES AVANT TESTS LIVE

### 1. Vérifier/Mettre à Jour Configuration Agents Mistral Console 🔴 CRITIQUE

**Problème** : Les agents doivent être configurés sur Mistral Console avec les prompts à jour.

**Agents Requis** :
1. **JARVIS_Maître** (orchestrateur)
2. **BASE** (worker générique)
3. **CODEUR** (worker code) - OPTIONNEL
4. **VALIDATEUR** (validator) - OPTIONNEL

**Variables d'Environnement Requises** :
```bash
MISTRAL_API_KEY=<votre_clé_api>
USE_MISTRAL_AGENT_API=1
JARVIS_MAITRE_AGENT_ID=<agent_id_mistral>
JARVIS_BASE_AGENT_ID=<agent_id_mistral>
JARVIS_CODEUR_AGENT_ID=<agent_id_mistral>  # Optionnel
JARVIS_VALIDATEUR_AGENT_ID=<agent_id_mistral>  # Optionnel
```

**Fichiers de Configuration Disponibles** :
- ✅ `config_mistral/agents/JARVIS_MAITRE.md` (5418 bytes)
- ✅ `config_mistral/agents/BASE.md` (4002 bytes)
- ✅ `config_mistral/agents/CODEUR.md` (6535 bytes)
- ✅ `config_mistral/agents/CODEUR_SIMPLIFIE.md` (9506 bytes) ⭐ RECOMMANDÉ
- ✅ `config_mistral/agents/VALIDATEUR.md` (2465 bytes)

**Actions** :

#### 1.1. Vérifier Fichier `.env` ⚠️

**Commande** :
```bash
# Vérifier si .env existe
ls .env

# Si n'existe pas, créer depuis template
cp .env.example .env
```

**Contenu Minimum Requis** :
```bash
# API Mistral
MISTRAL_API_KEY=votre_clé_api_ici
USE_MISTRAL_AGENT_API=1

# Agents (à remplir avec vos Agent IDs depuis Mistral Console)
JARVIS_MAITRE_AGENT_ID=ag_019c514a04a874159a21135b856a40e3
JARVIS_BASE_AGENT_ID=ag_votre_base_agent_id
```

#### 1.2. Vérifier Configuration Mistral Console 🌐

**URL** : https://console.mistral.ai/

**Étapes** :

1. **Se connecter à Mistral Console**
   - Aller sur https://console.mistral.ai/
   - Se connecter avec votre compte

2. **Vérifier Agent JARVIS_Maître**
   - Aller dans "Agents"
   - Chercher agent avec ID `ag_019c514a04a874159a21135b856a40e3`
   - **Vérifier le prompt** : Doit correspondre à `config_mistral/agents/JARVIS_MAITRE.md`
   - **Vérifier les paramètres** :
     - Temperature : 0.3
     - Max tokens : 4096
     - **Functions : 0 (AUCUNE)** ⚠️ IMPORTANT

3. **Vérifier Agent BASE**
   - Chercher votre agent BASE
   - **Vérifier le prompt** : Doit correspondre à `config_mistral/agents/BASE.md`
   - **Vérifier les paramètres** :
     - Temperature : 0.7
     - Max tokens : 4096
     - **Functions : Activées** (get_project_file, get_project_structure, etc.)

4. **Si Agents Pas à Jour : Mettre à Jour**

   **Pour JARVIS_Maître** :
   - Ouvrir `config_mistral/agents/JARVIS_MAITRE.md`
   - Copier tout le contenu
   - Aller dans Mistral Console → Agents → JARVIS_Maître → Edit
   - Coller le nouveau prompt
   - **IMPORTANT** : Désactiver toutes les functions (0 functions)
   - Sauvegarder
   - Attendre 2-3 minutes (propagation)

   **Pour BASE** :
   - Ouvrir `config_mistral/agents/BASE.md`
   - Copier tout le contenu
   - Aller dans Mistral Console → Agents → BASE → Edit
   - Coller le nouveau prompt
   - **IMPORTANT** : Activer les functions (get_project_file, get_project_structure, etc.)
   - Sauvegarder
   - Attendre 2-3 minutes (propagation)

---

### 2. Vérifier Backend Démarré 🔴 CRITIQUE

**Commande** :
```bash
# Démarrer le backend
uvicorn backend.app:app --reload --port 8000
```

**Vérification** :
- Ouvrir http://localhost:8000/docs
- Vérifier que l'API Swagger s'affiche
- Tester endpoint `/agents` → Doit retourner 2 agents (BASE, JARVIS_Maître)

---

### 3. Créer Projet de Test 🟡 RECOMMANDÉ

**Commande** :
```bash
# Créer dossier test
mkdir D:\Coding\TEST\test_live_jarvis
```

**Ou** : Utiliser un projet existant avec dette technique (pour tester workflow confirmation)

---

## 🧪 TESTS LIVE DISPONIBLES

### Option A : Tests Manuels (Interface Web) ⭐ RECOMMANDÉ

**Avantages** :
- Teste l'interface complète
- Workflow réel utilisateur
- Facile à debugger

**Étapes** :
1. Démarrer backend : `uvicorn backend.app:app --reload --port 8000`
2. Ouvrir frontend : `frontend/index.html` dans navigateur
3. Créer projet : "Test Live JARVIS"
4. Envoyer message : "Créer une calculatrice Python simple avec tests"
5. Vérifier délégation JARVIS_Maître → BASE
6. Vérifier fichiers créés

### Option B : Tests Automatisés (pytest) ⚠️ NÉCESSITE SETUP

**Fichiers de Test Live** :
- `tests/test_minimal_delegation.py` (déplacé dans `tests/`)
- `tests/test_live_projects.py` (3 tests : Calculatrice, TODO, MiniBlog)

**Problème Actuel** : Ces tests sont ignorés car ils nécessitent :
- Backend démarré
- API Mistral réelle
- Agents configurés

**Commande** :
```bash
# Exécuter tests live (après setup)
pytest tests/test_live_projects.py -v
```

**Résultats Attendus** :
- ✅ Calculatrice : 4 fichiers, 5/5 tests
- ⚠️ TODO : 6 fichiers, 10/11 tests (1 bug CODEUR mineur)
- ⚠️ MiniBlog : 6 fichiers, erreur Pydantic (bug CODEUR)

---

## 📋 CHECKLIST AVANT TESTS LIVE

### Configuration

- [ ] Fichier `.env` existe et contient `MISTRAL_API_KEY`
- [ ] Variable `JARVIS_MAITRE_AGENT_ID` définie dans `.env`
- [ ] Variable `JARVIS_BASE_AGENT_ID` définie dans `.env`
- [ ] Agent JARVIS_Maître configuré sur Mistral Console (prompt à jour)
- [ ] Agent BASE configuré sur Mistral Console (prompt à jour)
- [ ] Agent JARVIS_Maître : **0 functions** activées ⚠️
- [ ] Agent BASE : **Functions activées** (get_project_file, etc.)

### Backend

- [ ] Backend démarré : `uvicorn backend.app:app --reload --port 8000`
- [ ] API Swagger accessible : http://localhost:8000/docs
- [ ] Endpoint `/agents` retourne 2 agents (BASE, JARVIS_Maître)

### Frontend

- [ ] Frontend ouvert : `frontend/index.html`
- [ ] Interface charge correctement
- [ ] Connexion backend OK

### Projet Test

- [ ] Projet de test créé : `D:\Coding\TEST\test_live_jarvis`
- [ ] Ou projet existant avec dette technique identifié

---

## 🚀 COMMANDES RAPIDES

### Démarrer Backend
```bash
cd "D:\Coding\AppWindows\Jarvis 2.0"
uvicorn backend.app:app --reload --port 8000
```

### Ouvrir Frontend
```bash
# Ouvrir dans navigateur
start frontend/index.html
```

### Vérifier Configuration
```bash
# Vérifier .env existe
ls .env

# Vérifier agents configurés
curl http://localhost:8000/agents
```

### Exécuter Tests Live (Optionnel)
```bash
# Après setup complet
pytest tests/test_live_projects.py::test_live_calculatrice -v -s
```

---

## ⚠️ PROBLÈMES CONNUS

### 1. Agent JARVIS_Maître avec Functions Activées

**Symptôme** : JARVIS_Maître ne délègue pas, essaie d'exécuter lui-même.

**Solution** : Désactiver toutes les functions pour JARVIS_Maître sur Mistral Console.

**Référence** : `docs/history/20260216_RESOLUTION_DELEGATION_COMPLETE.md`

### 2. Timeout API Mistral

**Symptôme** : Timeout après 120s sur projets complexes.

**Solution** : Déjà implémenté (timeout adaptatif 120-300s dans `mistral_client.py`).

### 3. Quota API Mistral

**Symptôme** : Erreur 429 (Too Many Requests).

**Solution** : Attendre quelques minutes entre les tests.

---

## 📊 RÉSULTATS ATTENDUS TESTS LIVE

### Test Calculatrice (Simple)

**Commande** : "Créer une calculatrice Python simple avec tests"

**Résultat Attendu** :
- ✅ 4 fichiers créés :
  - `calculator.py` (fonctions add, subtract, multiply, divide)
  - `test_calculator.py` (tests unitaires)
  - `main.py` (exemple utilisation)
  - `README.md` (documentation)
- ✅ 5/5 tests passent
- ✅ Temps : ~25-30s

### Test TODO (Moyen)

**Commande** : "Créer une application TODO en Python avec SQLite"

**Résultat Attendu** :
- ✅ 6 fichiers créés :
  - `src/models.py`
  - `src/storage.py`
  - `src/todo.py`
  - `tests/test_todo.py`
  - `main.py`
  - `README.md`
- ⚠️ 10/11 tests passent (1 bug CODEUR mineur)
- ✅ Temps : ~45-60s

### Test MiniBlog (Complexe)

**Commande** : "Créer un mini blog avec FastAPI et SQLite"

**Résultat Attendu** :
- ✅ 6 fichiers créés
- ⚠️ Erreur Pydantic v1/v2 (bug CODEUR)
- ⚠️ Nécessite correction manuelle
- ✅ Temps : ~60-90s

---

## 🎯 PROCHAINES ÉTAPES

### Étape 1 : Configuration (15-30 min)

1. Vérifier/créer fichier `.env`
2. Vérifier agents sur Mistral Console
3. Mettre à jour prompts si nécessaire
4. Attendre 2-3 min (propagation)

### Étape 2 : Démarrage (2 min)

1. Démarrer backend : `uvicorn backend.app:app --reload --port 8000`
2. Ouvrir frontend : `frontend/index.html`
3. Vérifier `/agents` retourne 2 agents

### Étape 3 : Test Simple (5 min)

1. Créer projet "Test Live"
2. Envoyer : "Créer une calculatrice Python simple"
3. Vérifier délégation JARVIS_Maître → BASE
4. Vérifier fichiers créés

### Étape 4 : Test Workflow Confirmation (10 min)

1. Créer projet avec dette technique
2. Envoyer : "Ajouter fonction double()"
3. Vérifier challenge sécurité affiché
4. Confirmer action
5. Vérifier exécution

---

## 📝 NOTES IMPORTANTES

### Agents Actuellement Configurés

**Selon `agent_config.py`** :
- ✅ **BASE** : Worker générique (env: `JARVIS_BASE_AGENT_ID`)
- ✅ **JARVIS_Maître** : Orchestrateur (env: `JARVIS_MAITRE_AGENT_ID`)
- ⚠️ **CODEUR** : Worker code (env: `JARVIS_CODEUR_AGENT_ID`) - OPTIONNEL
- ⚠️ **VALIDATEUR** : Validator (env: `JARVIS_VALIDATEUR_AGENT_ID`) - OPTIONNEL

**Minimum Requis pour Tests Live** :
- ✅ JARVIS_Maître
- ✅ BASE

**CODEUR et VALIDATEUR** : Optionnels, non utilisés actuellement (architecture simplifiée).

### Prompts Recommandés

**JARVIS_Maître** : `config_mistral/agents/JARVIS_MAITRE.md` ✅  
**BASE** : `config_mistral/agents/BASE.md` ✅  
**CODEUR** : `config_mistral/agents/CODEUR_SIMPLIFIE.md` ⭐ (si utilisé)

---

## 🆘 EN CAS DE PROBLÈME

### Backend ne démarre pas

**Vérifier** :
```bash
# Vérifier dépendances
pip install -r requirements.txt

# Vérifier .env existe
ls .env

# Tester import
python -c "from backend.app import app; print('OK')"
```

### Agents non trouvés

**Vérifier** :
```bash
# Vérifier variables d'environnement
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('JARVIS_MAITRE_AGENT_ID'))"
```

### Délégation ne fonctionne pas

**Vérifier** :
1. Agent JARVIS_Maître : **0 functions** activées
2. Agent BASE : **Functions activées**
3. Prompts à jour sur Mistral Console
4. Attendre 2-3 min après mise à jour

---

**Document créé** : 2026-02-17  
**Statut** : Prêt pour tests live après configuration agents
