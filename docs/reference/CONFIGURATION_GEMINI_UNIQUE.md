# Configuration Gemini Unique - JARVIS 2.0

**Date** : 22 février 2026  
**Version** : 1.0  
**Statut** : RÉFÉRENCE - Configuration validée

---

## 📋 Vue d'Ensemble

JARVIS 2.0 utilise **exclusivement Google Gemini** comme provider IA pour tous les agents.

**Architecture** :
- **Provider unique** : Gemini (Google AI)
- **4 agents** : JARVIS_Maître, CODEUR, BASE, VALIDATEUR
- **2 modèles Gemini** : gemini-2.5-pro, gemini-3.1-pro-preview
- **Configuration** : Tier 1 (compte Google Cloud avec facturation)

---

## 🔑 Prérequis

### 1. Compte Google Cloud

1. Créer un compte Google Cloud : https://console.cloud.google.com/
2. Activer la facturation (carte bancaire requise)
3. Créer un projet (ex: "jarvis-ai-project")

### 2. Clé API Gemini

1. Accéder à Google AI Studio : https://aistudio.google.com/app/apikey
2. Créer une clé API
3. Copier la clé (format : `AIzaSy...`)

### 3. Activation Tier 1

**Automatique** : Dès que la facturation est activée sur le projet Google Cloud, vous passez en Tier 1.

**Vérification** :
- Accéder à : https://aistudio.google.com/rate-limit
- Vérifier les quotas : RPM > 15, RPD > 50 = Tier 1 actif

---

## ⚙️ Configuration .env

### Fichier .env Complet

```env
# ============================================
# PROVIDER GEMINI (Google AI)
# ============================================

# Clé API Gemini (obtenir sur https://aistudio.google.com/app/apikey)
GEMINI_API_KEY=AIzaSy...votre_clé_ici

# Modèle par défaut
GEMINI_MODEL=gemini-2.5-pro

# ============================================
# CONFIGURATION AGENTS → MODÈLES GEMINI
# ============================================

# JARVIS_Maître : Orchestrateur, délégation
JARVIS_MAITRE_PROVIDER=gemini
JARVIS_MAITRE_MODEL=gemini-2.5-pro

# BASE : Validation, rapports
BASE_PROVIDER=gemini
BASE_MODEL=gemini-2.5-pro

# CODEUR : Génération code
CODEUR_PROVIDER=gemini
CODEUR_MODEL=gemini-2.5-pro

# VALIDATEUR : Contrôle qualité
VALIDATEUR_PROVIDER=gemini
VALIDATEUR_MODEL=gemini-3.1-pro-preview

# ============================================
# SÉCURITÉ & CONTEXTE
# ============================================

# Limite de tokens pour le contexte projet
MAX_CONTEXT_TOKENS=50000

# Activer la redaction de données sensibles
ENABLE_REDACTION=true
```

### Variables Obligatoires

| Variable | Valeur | Description |
|----------|--------|-------------|
| `GEMINI_API_KEY` | `AIzaSy...` | Clé API Google Gemini |
| `GEMINI_MODEL` | `gemini-2.5-pro` | Modèle par défaut |
| `JARVIS_MAITRE_PROVIDER` | `gemini` | Provider JARVIS_Maître |
| `JARVIS_MAITRE_MODEL` | `gemini-2.5-pro` | Modèle JARVIS_Maître |
| `BASE_PROVIDER` | `gemini` | Provider BASE |
| `BASE_MODEL` | `gemini-2.5-pro` | Modèle BASE |
| `CODEUR_PROVIDER` | `gemini` | Provider CODEUR |
| `CODEUR_MODEL` | `gemini-2.5-pro` | Modèle CODEUR |
| `VALIDATEUR_PROVIDER` | `gemini` | Provider VALIDATEUR |
| `VALIDATEUR_MODEL` | `gemini-3.1-pro-preview` | Modèle VALIDATEUR |

---

## 🎯 Modèles Gemini Utilisés

### gemini-2.5-pro

**Utilisé par** : JARVIS_Maître, BASE, CODEUR

**Caractéristiques** :
- **Contexte** : 2M tokens
- **Quotas Tier 1** : 150 RPM, 2M TPM, 1K RPD
- **Qualité** : Excellente (modèle Pro)
- **Coût** : $1.25/1M tokens input, $5.00/1M tokens output

**Usage** :
- Orchestration (JARVIS_Maître)
- Génération code (CODEUR)
- Validation (BASE)

### gemini-3.1-pro-preview

**Utilisé par** : VALIDATEUR

**Caractéristiques** :
- **Contexte** : 5M tokens
- **Quotas Tier 1** : 25 RPM, 5M TPM, 255 RPD
- **Qualité** : Très élevée (modèle 3.1 Pro)
- **Coût** : Similaire à 2.5 Pro

**Usage** :
- Contrôle qualité final
- Validation tests

---

## 📊 Quotas Tier 1

### Quotas par Modèle

| Modèle | RPM | TPM | RPD | Statut |
|--------|-----|-----|-----|--------|
| gemini-2.5-pro | 150 | 2M | 1K | ✅ Disponible |
| gemini-3.1-pro-preview | 25 | 5M | 255 | ✅ Disponible |

**Total cumulé** : 175 RPM, 7M TPM

### Estimation Consommation

**Par projet généré** (moyenne) :
- Input : ~15,000 tokens
- Output : ~6,000 tokens
- Coût : ~$0.05 par projet

**Quotas suffisants pour** :
- 150 projets/heure (RPM)
- 1000 projets/jour (RPD)

---

## 🚀 Installation et Démarrage

### 1. Cloner le Projet

```bash
cd "d:\Coding\AppWindows\Jarvis 2.0"
```

### 2. Installer les Dépendances

```bash
pip install -r requirements.txt
```

**Dépendances Gemini** :
- `google-generativeai==0.8.3`

### 3. Configurer .env

```bash
# Copier le template
cp .env.example .env

# Éditer .env avec votre clé Gemini
# GEMINI_API_KEY=AIzaSy...
```

### 4. Lancer le Backend

```bash
uvicorn backend.app:app --reload --port 8000
```

### 5. Ouvrir le Frontend

```
Ouvrir frontend/index.html dans un navigateur
```

---

## ✅ Validation Configuration

### Test 1 : Vérifier Clé API

```python
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Lister modèles disponibles
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
```

**Résultat attendu** : Liste de modèles Gemini affichée

### Test 2 : Tester Modèles Configurés

```bash
python test_tier1_models.py
```

**Résultat attendu** : `4/4 modèles OK`

### Test 3 : Test Live Calculatrice

```bash
pytest tests/live/test_live_projects.py::test_niveau1_calculatrice -v -s
```

**Résultat attendu** :
- 4 fichiers générés
- 9/9 tests passants
- Durée : ~2 minutes

---

## 🔧 Dépannage

### Erreur 404 : Model not found

**Symptôme** : `404 models/gemini-2.0-flash is not found`

**Cause** : Modèle non disponible pour nouveaux utilisateurs

**Solution** : Utiliser `gemini-2.5-pro` à la place

### Erreur 429 : Quota exceeded

**Symptôme** : `429 Resource has been exhausted`

**Cause** : Quotas RPM ou RPD dépassés

**Solutions** :
1. Attendre 1 minute (reset RPM)
2. Vérifier quotas : https://aistudio.google.com/rate-limit
3. Répartir sur plusieurs modèles

### Erreur 401 : Invalid API Key

**Symptôme** : `401 API key not valid`

**Cause** : Clé API incorrecte ou expirée

**Solutions** :
1. Vérifier `GEMINI_API_KEY` dans `.env`
2. Régénérer clé sur AI Studio
3. Vérifier que la clé est bien copiée (pas d'espace)

---

## 📈 Monitoring

### Surveiller Quotas

**URL** : https://aistudio.google.com/rate-limit

**Vérifier** :
- RPM utilisés vs disponibles
- RPD utilisés vs disponibles
- Modèles avec quotas épuisés

### Surveiller Coûts

**URL** : https://console.cloud.google.com/billing

**Configurer alertes** :
- 10% du budget
- 50% du budget
- 90% du budget

**Budget recommandé** : $10/mois (largement suffisant)

---

## 🎯 Bonnes Pratiques

### 1. Gestion Quotas

- ✅ Utiliser modèles différents par agent (quotas séparés)
- ✅ Surveiller quotas quotidiennement (7 premiers jours)
- ✅ Configurer alertes budget Google Cloud

### 2. Optimisation Coûts

- ✅ Limiter contexte projet (MAX_CONTEXT_TOKENS=50000)
- ✅ Éviter requêtes inutiles
- ✅ Utiliser cache provider (déjà implémenté)

### 3. Qualité Code

- ✅ Utiliser gemini-2.5-pro pour génération code
- ✅ Utiliser gemini-3.1-pro-preview pour validation
- ✅ Vérifier tests générés systématiquement

---

## 📚 Références

### Documentation Gemini

- API Reference : https://ai.google.dev/gemini-api/docs
- Rate Limits : https://ai.google.dev/gemini-api/docs/rate-limits
- Pricing : https://ai.google.dev/pricing
- Models : https://ai.google.dev/models/gemini

### Google Cloud

- Console : https://console.cloud.google.com/
- Billing : https://console.cloud.google.com/billing
- Budgets : https://console.cloud.google.com/billing/budgets

### AI Studio

- API Keys : https://aistudio.google.com/app/apikey
- Rate Limits : https://aistudio.google.com/rate-limit

---

## 🔄 Changelog

### Version 1.0 (22 février 2026)
- Configuration Gemini unique validée
- Tier 1 opérationnel
- Tests live réussis (3/3)
- Guide complet créé

---

**Date** : 22 février 2026  
**Statut** : ✅ VALIDÉ - Configuration opérationnelle  
**Auteur** : Cascade AI
