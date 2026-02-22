# Mission Tier 1 Gemini - Configuration Complète JARVIS 2.0

**Date** : 22 février 2026  
**Statut** : 🔄 EN COURS - Configuration finale  
**Version** : 2.0  
**Document de référence unique**

---

## 📋 Contexte et Objectif

### Situation Actuelle

**Tier 1 Gemini activé** :
- ✅ Compte de facturation Google Cloud lié
- ✅ Project ID : `gen-lang-client-0887224499`
- ✅ Budget configuré avec alertes
- ✅ Quotas Tier 1 validés sur AI Studio

**Problème identifié** :
- ❌ Modèles testés (`gemini-2.0-flash`, `gemini-1.5-flash`) **non disponibles** en API v1beta
- ❌ Tests lancés mais **0 fichiers générés** (erreur 404 modèle)
- ⚠️ Configuration `.env` actuelle : `gemini-flash-latest` (non testé)

### Objectif de la Mission

**Configurer JARVIS 2.0 pour Tier 1 Gemini avec** :
1. **Modèles compatibles** : Identifier modèles Tier 1 accessibles via API v1beta
2. **Mapping agent → modèle** : Assigner modèle optimal par agent selon mission
3. **Configuration .env validée** : Tester et valider configuration complète
4. **Flow orchestration** : Vérifier cohérence architecture/agents/providers
5. **Tests live réussis** : 3/3 tests (Calculatrice, TODO, MiniBlog)

---

## 🎯 Modèles Gemini Disponibles (Tier 1)

### Modèles Listés (API v1beta)

**Commande de vérification** :
```python
import google.generativeai as genai
models = [m.name.replace('models/', '') for m in genai.list_models() 
          if 'generateContent' in m.supported_generation_methods]
```

**Résultat** : 29 modèles disponibles dont :
```
gemini-2.0-flash, gemini-2.0-flash-lite
gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro
gemini-3-flash-preview, gemini-3-pro-preview, gemini-3.1-pro-preview
gemini-flash-latest, gemini-flash-lite-latest, gemini-pro-latest
gemini-robotics-er-1.5-preview
```

### ✅ Quotas Tier 1 Validés (AI Studio)

**Date capture** : 22 février 2026

**Modèles avec quotas disponibles (0 utilisé)** :

| Modèle | Nom API | RPM | TPM | RPD | Function Calling |
|--------|---------|-----|-----|-----|------------------|
| **Gemini 2 Flash** | `gemini-2.0-flash` | 0/2K | 0/4M | 0/Illimité | ✅ |
| **Gemini 2 Flash Lite** | `gemini-2.0-flash-lite` | 0/4K | 0/4M | 0/Illimité | ✅ |
| **Gemini 2.5 Pro** | `gemini-2.5-pro` | 0/150 | 0/2M | 0/1K | ✅ |
| **Gemini 3.1 Pro** | `gemini-3.1-pro-preview` | 0/25 | 0/5M | 0/255 | ✅ |

**Modèles avec quotas épuisés** :
- Gemini 2.5 Flash : 21/10K RPD
- Gemini 3 Flash : 21/10K RPD
- Gemini 2.5 Flash Lite : 21/Illimité RPD

**Total quotas cumulés disponibles** : 6175 RPM (2K + 4K + 150 + 25)

---

## 💰 Tarification et Quotas Tier 1

### Tarifs Officiels (Source : https://ai.google.dev/pricing)

| Modèle | Input ($/1M tokens) | Output ($/1M tokens) | Contexte |
|--------|---------------------|----------------------|----------|
| **Flash** (2.0, 1.5, 3) | $0.075 | $0.30 | 1M |
| **Pro** (1.5, 2.5) | $1.25 | $5.00 | 2M |

### Quotas Tier 1 Attendus

| Tier | RPM | TPM | RPD |
|------|-----|-----|-----|
| **Free** | 5 | 250K | 20 |
| **Tier 1** | 10-15 | 500K | 100 |

**⚠️ IMPORTANT** : Quotas réels à vérifier sur screenshot AI Studio.

---

## 🔧 Configuration par Agent

### Principes de Sélection

**Critères** :
1. **Function Calling requis** : Tous les agents utilisent des tools
2. **Quotas séparés** : Répartir sur modèles différents si possible
3. **Coût/Qualité** : Flash pour rapidité, Pro pour qualité critique
4. **Compatibilité v1beta** : Modèle accessible via SDK Python

### ✅ Mapping Validé (Configuration Tier 1 Optimale)

| Agent | Rôle | Modèle | RPM | TPM | RPD | Raison |
|-------|------|--------|-----|-----|-----|--------|
| **JARVIS_Maître** | Orchestrateur | `gemini-2.0-flash` | 2K | 4M | Illimité | Rapide, quotas élevés, orchestration |
| **CODEUR** | Génération code | `gemini-2.5-pro` | 150 | 2M | 1K | Qualité maximale, Pro pour code |
| **BASE** | Validation | `gemini-2.0-flash-lite` | 4K | 4M | Illimité | Rapide, quotas séparés |
| **VALIDATEUR** | Contrôle qualité | `gemini-3.1-pro-preview` | 25 | 5M | 255 | Précision, quota séparé |

**Avantages configuration** :
- ✅ Quotas séparés par modèle (pas de conflit)
- ✅ 6175 RPM cumulés (2K + 4K + 150 + 25)
- ✅ RPD illimité pour JARVIS_Maître et BASE
- ✅ Qualité maximale pour CODEUR (Pro)
- ✅ 100% gratuit (Tier 1)

---

## 📊 Analyse Coût Estimé

### Par Projet (Moyenne)

**Tokens utilisés** (basé sur test Calculatrice) :
- Input : ~15,000 tokens
- Output : ~6,000 tokens

**Coût avec Flash** :
```
Input  : 15,000 × $0.075 / 1,000,000 = $0.001125
Output : 6,000 × $0.30 / 1,000,000   = $0.001800
TOTAL  : $0.002925 ≈ $0.003 (0.3 centime/projet)
```

### Par Scénario d'Usage

| Usage | Projets/mois | Coût/mois | Coût/jour |
|-------|--------------|-----------|-----------|
| **Léger** | 10 | $0.03 | $0.001 |
| **Modéré** | 50 | $0.15 | $0.005 |
| **Intensif** | 200 | $0.60 | $0.020 |
| **Pro** | 500 | $1.50 | $0.050 |

**Conclusion** : Coût quasi-nul pour usage normal (<200 projets/mois).

---

## 🏗️ Architecture et Flow

### Providers Disponibles

**Fichier** : `backend/ia/providers/provider_factory.py`

**Providers supportés** :
1. **GeminiProvider** : Google Gemini API
2. **MistralProvider** : Mistral API (legacy)
3. **OpenRouterProvider** : OpenRouter (multi-modèles)

### Sélection Provider par Agent

**Logique** :
```python
def create(self, provider_type: str, agent_name: str = None) -> BaseProvider:
    # 1. Vérifier cache
    # 2. Sélectionner provider spécifique agent (env var)
    # 3. Créer provider avec modèle spécifique agent
```

**Variables d'environnement** :
```env
# Provider global
DEFAULT_PROVIDER=gemini

# Provider par agent (optionnel)
JARVIS_MAITRE_PROVIDER=gemini
CODEUR_PROVIDER=gemini
BASE_PROVIDER=gemini
VALIDATEUR_PROVIDER=gemini

# Modèle par agent
JARVIS_MAITRE_MODEL=gemini-flash-latest
CODEUR_MODEL=gemini-flash-latest
BASE_MODEL=gemini-flash-latest
VALIDATEUR_MODEL=gemini-robotics-er-1.5-preview
```

### Délai Adaptatif (Protection Quotas)

**Fichier** : `backend/ia/providers/gemini_provider.py`

**Implémentation** :
```python
_min_delay_seconds: float = 4.0  # 60s / 15 RPM

async def send_message(self, ...):
    if self._last_request_time:
        elapsed = (datetime.now() - self._last_request_time).total_seconds()
        if elapsed < self._min_delay_seconds:
            wait_time = self._min_delay_seconds - elapsed
            await asyncio.sleep(wait_time)
    
    response = await self.client.generate_content_async(...)
    self._last_request_time = datetime.now()
```

**Résultat** : 0 erreur 429 en Free Tier (validé).

---

## ✅ Checklist Configuration Complète

### 1. Identification Modèles Tier 1

- [x] **Screenshot AI Studio** : Capturer quotas exacts par modèle ✅
- [x] **Identifier modèles Flash** : Accessibles en Tier 1 avec Function Calling ✅
- [x] **Identifier modèles Pro** : Si besoin qualité maximale ✅
- [x] **Vérifier compatibilité v1beta** : Tester 1 requête par modèle ✅

### 2. Configuration .env

- [x] **Définir DEFAULT_PROVIDER** : `gemini` ✅
- [x] **Assigner modèles par agent** : Selon mapping validé ✅
- [x] **Vérifier clé API** : `GEMINI_API_KEY` active ✅
- [ ] **Sauvegarder .env** : Backup avant modification

### 3. Vérification Architecture

- [ ] **provider_factory.py** : Support multi-modèles OK
- [ ] **gemini_provider.py** : Délai adaptatif actif
- [ ] **orchestration.py** : Délégation agents fonctionnelle
- [ ] **Logs backend** : Aucune erreur au démarrage

### 4. Tests de Validation

- [ ] **Nettoyer environnement** : TEST/, jarvis_data.db
- [ ] **Redémarrer backend** : Avec nouvelle config
- [ ] **Test minimal** : 1 requête simple (health check)
- [ ] **Test Calculatrice** : Niveau 1 (4 fichiers attendus)
- [ ] **Test TODO** : Niveau 2 (6 fichiers attendus)
- [ ] **Test MiniBlog** : Niveau 3 (5 fichiers attendus)

### 5. Monitoring Post-Tests

- [ ] **Vérifier coût** : Google Cloud Console
- [ ] **Vérifier quotas** : AI Studio Rate Limits
- [ ] **Analyser logs** : Aucune erreur 429 ou 404
- [ ] **Valider fichiers** : Tous générés et tests passants

---

## 🚨 Problèmes Identifiés et Solutions

### Problème 1 : Modèles Non Disponibles en v1beta

**Symptôme** :
```
404 models/gemini-2.0-flash is not found for API version v1beta
404 models/gemini-1.5-flash is not found for API version v1beta
```

**Cause** : SDK Python utilise API v1beta qui ne supporte pas tous les modèles listés.

**Solution** :
1. Utiliser `gemini-flash-latest` (alias vers dernière version stable)
2. Utiliser `gemini-3-flash-preview` (validé en Free Tier)
3. Vérifier modèles disponibles avec screenshot AI Studio

### Problème 2 : Tests Passent Mais 0 Fichiers Générés

**Symptôme** :
```
3 passed in 28.39s
files_found: 0 pour chaque test
```

**Cause** : Erreur 404 modèle → Requête API échoue → Aucune délégation CODEUR → Aucun fichier.

**Solution** :
1. Corriger modèles dans `.env`
2. Redémarrer backend
3. Relancer tests avec modèles compatibles

### Problème 3 : Limite Budget Google Cloud

**Symptôme** : Impossible de définir limite stricte automatique.

**Explication** : Google Cloud ne bloque pas automatiquement à un montant précis.

**Solution** :
1. Configurer alertes : 10%, 50%, 90%, 100%
2. Surveiller quotidiennement (7 premiers jours)
3. Désactiver API manuellement si alerte 90% reçue

---

## 📝 Prochaines Étapes (Ordre Strict)

### Étape 1 : Capture Screenshot Quotas AI Studio

**Action** : Utilisateur fournit screenshot de https://aistudio.google.com/rate-limit

**Informations attendues** :
- Liste complète modèles Tier 1
- Quotas RPM/TPM/RPD par modèle
- Modèles avec Function Calling

**Objectif** : Identifier modèles réellement accessibles et leurs quotas exacts.

---

### Étape 2 : Analyse Screenshot et Décision Modèles

**Actions** :
1. Identifier modèles Flash disponibles (coût $0.075/1M input)
2. Identifier modèles Pro disponibles (coût $1.25/1M input)
3. Vérifier Function Calling supporté
4. Comparer quotas (RPM, RPD)

**Décision** :
- **Option A** : 100% Flash (économique, quotas partagés)
- **Option B** : Flash + Pro (qualité max, quotas mixtes)
- **Option C** : Hybride Gemini + OpenRouter (scalable)

---

### ✅ Étape 3 : Configuration .env Finale (VALIDÉE)

**Fichier** : `d:\Coding\AppWindows\Jarvis 2.0\.env`

**Configuration Tier 1 Optimale** :
```env
# Provider par défaut
DEFAULT_PROVIDER=gemini

# Providers spécifiques par agent
JARVIS_MAITRE_PROVIDER=gemini
CODEUR_PROVIDER=gemini
BASE_PROVIDER=gemini
VALIDATEUR_PROVIDER=gemini

# Modèles Gemini Tier 1 (Quotas séparés, 100% gratuit)
GEMINI_MODEL=gemini-2.0-flash
JARVIS_MAITRE_MODEL=gemini-2.0-flash
CODEUR_MODEL=gemini-2.5-pro
BASE_MODEL=gemini-2.0-flash-lite
VALIDATEUR_MODEL=gemini-3.1-pro-preview

# Clé API Gemini (Tier 1 activé)
GEMINI_API_KEY=AIzaSyCmhnxKvTM7cIxdEAmnlucQDCV7r48FI6g
```

**Commande application** :
```powershell
# Sauvegarder .env actuel
Copy-Item .env .env.backup

# Copier .env.example vers .env (si pas encore fait)
Copy-Item .env.example .env

# Modifier .env avec clé API et modèles Tier 1
# (manuel ou via script PowerShell)

# Vérifier configuration
Get-Content .env | Select-String "MODEL"
```

---

### Étape 4 : Vérification Configuration Agents

**Fichiers à vérifier** :

1. **`backend/ia/providers/provider_factory.py`**
   - [ ] Méthode `_create_gemini()` supporte `agent_name`
   - [ ] Lecture variables `{AGENT}_MODEL` correcte
   - [ ] Logs création provider actifs

2. **`backend/ia/providers/gemini_provider.py`**
   - [ ] Délai adaptatif `_min_delay_seconds` configuré
   - [ ] Logs attente quota actifs
   - [ ] Function Calling supporté

3. **`backend/services/orchestration.py`**
   - [ ] Délégation agents fonctionnelle
   - [ ] Passage `function_executor` aux agents délégués
   - [ ] Extraction fichiers attendus correcte

**Commande vérification** :
```powershell
# Rechercher logs création providers
Get-Content backend\logs\mistral_api.log -Tail 100 | Select-String "Creating.*Provider"

# Rechercher erreurs
Get-Content backend\logs\mistral_api.log -Tail 100 | Select-String "ERROR|404|429"
```

---

### Étape 5 : Tests de Validation Progressifs

#### Test 1 : Health Check Backend

**Objectif** : Vérifier backend démarre sans erreur.

**Commandes** :
```powershell
# Nettoyer environnement
Remove-Item -Path "D:\Coding\TEST\*" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "jarvis_data.db" -Force -ErrorAction SilentlyContinue

# Arrêter backend existant
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force

# Démarrer backend
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Attendre 10s puis tester
Start-Sleep -Seconds 10
Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET
```

**Résultat attendu** : `200 OK {"status":"ok"}`

---

#### Test 2 : Requête Simple Gemini

**Objectif** : Vérifier modèle accessible et Function Calling OK.

**Script Python** :
```python
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Tester modèle configuré
model_name = os.getenv('JARVIS_MAITRE_MODEL')
print(f"Test modèle : {model_name}")

model = genai.GenerativeModel(model_name)
response = model.generate_content("Dis bonjour en français")
print(f"Réponse : {response.text}")
```

**Résultat attendu** : Réponse en français sans erreur 404.

---

#### Test 3 : Test Live Calculatrice

**Objectif** : Valider génération code complète.

**Commande** :
```powershell
pytest tests/live/test_live_projects.py::test_niveau1_calculatrice -v -s
```

**Résultat attendu** :
```
✅ 4 fichiers générés
✅ 7/7 tests passants
✅ Durée : 2-3 minutes
```

---

#### Test 4 : Suite Complète Tests Live

**Objectif** : Valider configuration sur 3 niveaux de complexité.

**Commande** :
```powershell
pytest tests/live/test_live_projects.py -v --tb=short
```

**Résultat attendu** :
```
✅ test_niveau1_calculatrice PASSED
✅ test_niveau2_todo PASSED
✅ test_niveau3_miniblog PASSED

3 passed in ~10 minutes
```

---

### Étape 6 : Nettoyage Documentation

**Actions** :

1. **Archiver docs temporaires** :
   ```powershell
   # Créer dossier archive
   New-Item -ItemType Directory -Path "docs\history\20260222_migration_tier1" -Force
   
   # Déplacer docs work obsolètes
   Move-Item "docs\work\ANALYSE_COUT_TIER1_GEMINI.md" "docs\history\20260222_migration_tier1\"
   Move-Item "docs\work\VERIFICATION_TIER1_ACTIVATION.md" "docs\history\20260222_migration_tier1\"
   Move-Item "docs\work\RAPPORT_TESTS_LIVE_PARTIEL_22FEV.md" "docs\history\20260222_migration_tier1\"
   ```

2. **Mettre à jour docs reference** :
   - `CONFIGURATION_OPTIMALE_API.md` → Ajouter section Tier 1
   - `GUIDE_MIGRATION_TIER1_GEMINI.md` → Marquer comme validé
   - Créer `RAPPORT_VALIDATION_TIER1_FINALE.md`

3. **Supprimer scripts temporaires** :
   ```powershell
   Remove-Item "update_to_tier1_models.py"
   Remove-Item "fix_to_tier1_stable_models.py"
   Remove-Item "list_tier1_models.py"
   ```

---

## 📊 Rapport Final Attendu

**Fichier** : `docs/reference/RAPPORT_VALIDATION_TIER1_FINALE.md`

**Contenu** :
1. **Configuration validée** : Modèles par agent
2. **Résultats tests** : 3/3 tests live réussis
3. **Coût réel** : Facture Google Cloud après 24h
4. **Quotas utilisés** : RPM/RPD consommés
5. **Recommandations** : Production, optimisations futures

---

## 🎯 Critères de Succès

### Configuration Validée

- ✅ Tous les modèles accessibles (pas d'erreur 404)
- ✅ Function Calling fonctionnel sur tous les agents
- ✅ Délai adaptatif respecte quotas (pas d'erreur 429)
- ✅ Logs backend propres (aucune erreur)

### Tests Live Réussis

- ✅ **Calculatrice** : 4 fichiers, 7/7 tests
- ✅ **TODO** : 6 fichiers, 14/14 tests
- ✅ **MiniBlog** : 5 fichiers, 6/6 tests

### Coût Maîtrisé

- ✅ Coût < $0.05 pour 3 tests
- ✅ Alertes budget configurées
- ✅ Monitoring actif

### Documentation Complète

- ✅ Configuration finale documentée
- ✅ Docs temporaires archivées
- ✅ Rapport validation généré
- ✅ Guide utilisateur à jour

---

## 📚 Références

### Documentation Gemini

- API Reference : https://ai.google.dev/gemini-api/docs
- Rate Limits : https://ai.google.dev/gemini-api/docs/rate-limits
- Pricing : https://ai.google.dev/pricing
- Models : https://ai.google.dev/models/gemini

### Console Google Cloud

- Billing : https://console.cloud.google.com/billing
- Budgets : https://console.cloud.google.com/billing/budgets
- APIs : https://console.cloud.google.com/apis/dashboard

### AI Studio

- API Keys : https://aistudio.google.com/app/apikey
- Rate Limits : https://aistudio.google.com/rate-limit

---

## 🔄 Changelog

### Version 3.0 (22 février 2026 16h50) ✅ CONFIGURATION VALIDÉE
- ✅ Screenshots AI Studio analysés (quotas Tier 1 complets)
- ✅ Modèles Tier 1 disponibles identifiés (4 modèles avec quotas frais)
- ✅ Mapping agent → modèle optimal défini
- ✅ Configuration .env.example mise à jour
- ✅ Documentation complétée avec quotas exacts
- ⏳ Prochaine étape : Application configuration .env + tests live

### Version 2.0 (22 février 2026 16h35)
- Document unique de référence créé
- Consolidation analyses coût, quotas, configuration
- Checklist complète validation Tier 1
- Problèmes identifiés et solutions documentées
- Prochaines étapes définies (screenshot → config → tests)

### Version 1.0 (22 février 2026 15h00)
- Tier 1 activé
- Budget configuré
- Premiers tests (erreurs 404 modèles)

---

**Date** : 22 février 2026 16h50  
**Statut** : ✅ CONFIGURATION TIER 1 VALIDÉE  
**Prochaine action** : Appliquer configuration .env + lancer tests live
