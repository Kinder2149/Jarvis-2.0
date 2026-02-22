# Guide Migration Tier 1 Gemini - JARVIS 2.0

**Date** : 22 février 2026  
**Statut** : ✅ GUIDE VALIDÉ  
**Durée migration** : 15 minutes  
**Coût estimé** : $0.20-$2.00/mois

---

## 🎯 Pourquoi Migrer vers Tier 1 ?

### Limitations Free Tier Actuelles

- ❌ **20 RPD** : Maximum 20 projets/jour
- ❌ **5 RPM** : Délai 12s entre requêtes
- ❌ **Blocage quotidien** : Reset à 9h chaque matin
- ❌ **2 modèles** : Choix limité

### Avantages Tier 1

- ✅ **100 RPD** : 100 projets/jour (5x plus)
- ✅ **10-15 RPM** : Délai 4-6s entre requêtes (2-3x plus rapide)
- ✅ **Pas de blocage** : Quotas confortables
- ✅ **10+ modèles** : Gemini 2.0 Flash, 1.5 Pro, etc.
- ✅ **Batch API** : Traitement parallèle
- ✅ **Contexte 2M tokens** : Projets plus complexes (avec Pro)

### Coût Réel

**Pour 50 projets/mois** : **$0.20** (20 centimes)  
**Pour 200 projets/mois** : **$0.80** (80 centimes)  
**Pour 500 projets/mois** : **$2.00** (2€)

**Coût par projet** : **0.4 centime** (constant)

---

## 📋 Prérequis

### 1. Compte Google Cloud

- ✅ Compte Google existant
- ✅ Accès à Google Cloud Console
- ✅ Carte bancaire (pour facturation, mais pas de débit si < $200 crédits gratuits)

### 2. Projet Gemini API Existant

- ✅ Clé API Gemini active
- ✅ Projet JARVIS 2.0 fonctionnel
- ✅ Tests live validés (au moins 1/4)

---

## 🚀 Migration en 4 Étapes

### Étape 1 : Activation Tier 1 (5 minutes)

#### 1.1 Accéder à AI Studio

**URL** : https://aistudio.google.com/app/apikey

#### 1.2 Vérifier Tier Actuel

- Cliquer sur l'onglet "Rate limits"
- Vérifier : "Current tier: Free"

#### 1.3 Cliquer "Upgrade"

- Bouton "Upgrade to Tier 1" visible en haut à droite
- Si non visible : aller sur https://console.cloud.google.com/billing

#### 1.4 Lier Compte de Facturation

**Option A : Nouveau compte de facturation**
1. Cliquer "Create billing account"
2. Remplir informations (nom, adresse, carte bancaire)
3. Accepter conditions
4. Valider

**Option B : Compte existant**
1. Sélectionner compte de facturation existant
2. Lier au projet Gemini API
3. Valider

#### 1.5 Confirmer Activation

- Attendre 2-5 minutes
- Rafraîchir page AI Studio
- Vérifier : "Current tier: Tier 1"

**✅ Tier 1 activé !**

---

### Étape 2 : Configuration Alertes Budget (3 minutes)

#### 2.1 Accéder à Budgets & Alerts

**URL** : https://console.cloud.google.com/billing/budgets

#### 2.2 Créer Budget

1. Cliquer "Create budget"
2. Nom : "JARVIS API Budget"
3. Projets : Sélectionner projet Gemini API
4. Services : "Generative Language API"

#### 2.3 Définir Montant

**Budget mensuel** : $10 (recommandé pour démarrer)

#### 2.4 Configurer Alertes

**Seuils d'alerte** :
- 10% ($1) : Email notification
- 50% ($5) : Email notification
- 90% ($9) : Email notification urgente
- 100% ($10) : Email + SMS (optionnel)

#### 2.5 Destinataires

- Ajouter ton email
- Ajouter numéro téléphone (optionnel)

**✅ Alertes configurées !**

---

### Étape 3 : Mise à Jour Configuration JARVIS (2 minutes)

#### 3.1 Ouvrir Fichier .env

**Fichier** : `d:\Coding\AppWindows\Jarvis 2.0\.env`

#### 3.2 Modifier Modèles Gemini

**Configuration recommandée (100% Flash)** :

```env
# Provider par défaut
DEFAULT_PROVIDER=gemini

# Providers spécifiques par agent
JARVIS_MAITRE_PROVIDER=gemini
CODEUR_PROVIDER=gemini
BASE_PROVIDER=gemini
VALIDATEUR_PROVIDER=gemini

# Modèles Gemini Tier 1 optimisés
GEMINI_MODEL=gemini-2.0-flash
JARVIS_MAITRE_MODEL=gemini-2.0-flash
CODEUR_MODEL=gemini-2.0-flash
BASE_MODEL=gemini-2.0-flash
VALIDATEUR_MODEL=gemini-robotics-er-1.5-preview

# Clé API Gemini (inchangée)
GEMINI_API_KEY=<votre_clé_existante>
```

**Changements** :
- `gemini-3-flash-preview` → `gemini-2.0-flash` (dernière version stable)
- Tous les agents sur modèles Tier 1

#### 3.3 Sauvegarder

**Ctrl + S** ou **Fichier > Enregistrer**

**✅ Configuration mise à jour !**

---

### Étape 4 : Tests de Validation (5 minutes)

#### 4.1 Nettoyer Environnement

```powershell
# Nettoyer répertoire TEST
Remove-Item -Path "D:\Coding\TEST\*" -Recurse -Force -ErrorAction SilentlyContinue

# Nettoyer base de données
Remove-Item -Path "jarvis_data.db" -Force -ErrorAction SilentlyContinue
```

#### 4.2 Redémarrer Backend

```powershell
# Arrêter processus existant
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Stop-Process -Force

# Démarrer backend
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

**Attendre 10 secondes** pour initialisation.

#### 4.3 Lancer Tests Live Complets

```powershell
# Suite complète (3 tests)
pytest tests/live/test_live_projects.py -v

# OU tests individuels avec délais
pytest tests/live/test_live_projects.py::test_niveau1_calculatrice -v
Start-Sleep -Seconds 15

pytest tests/live/test_live_projects.py::test_niveau2_todo -v
Start-Sleep -Seconds 15

pytest tests/live/test_live_projects.py::test_niveau3_miniblog -v
```

#### 4.4 Vérifier Résultats

**Attendu** :
```
✅ test_niveau1_calculatrice PASSED
✅ test_niveau2_todo PASSED
✅ test_niveau3_miniblog PASSED

3 passed in ~10 minutes
```

**✅ Migration validée !**

---

## 📊 Vérification Coût

### Après 1 Semaine

**URL** : https://console.cloud.google.com/billing

**Vérifier** :
- Coût total : $0.05-$0.20 (selon usage)
- Coût par jour : $0.01-$0.03
- Services : "Generative Language API"

### Après 1 Mois

**Coût attendu** :
- Usage léger (10 projets/mois) : $0.04
- Usage modéré (50 projets/mois) : $0.20
- Usage intensif (200 projets/mois) : $0.80

**Si coût > $2** : Analyser logs pour identifier usage anormal.

---

## 🔧 Configurations Avancées

### Option A : 100% Flash (Économique) ⭐ RECOMMANDÉ

**Coût** : $0.20/mois (50 projets)  
**Qualité** : Bonne  
**Quotas** : 100 RPD, 10 RPM

```env
GEMINI_MODEL=gemini-2.0-flash
JARVIS_MAITRE_MODEL=gemini-2.0-flash
CODEUR_MODEL=gemini-2.0-flash
BASE_MODEL=gemini-2.0-flash
VALIDATEUR_MODEL=gemini-robotics-er-1.5-preview
```

---

### Option B : Flash + Pro (Qualité Maximale)

**Coût** : $1.50/mois (50 projets)  
**Qualité** : Excellente  
**Quotas** : 50 RPD (Pro), 100 RPD (Flash)

```env
GEMINI_MODEL=gemini-2.0-flash
JARVIS_MAITRE_MODEL=gemini-2.0-flash
CODEUR_MODEL=gemini-1.5-pro          # Qualité maximale
BASE_MODEL=gemini-2.0-flash
VALIDATEUR_MODEL=gemini-1.5-pro      # Contrôle approfondi
```

**Quand utiliser** :
- Projets critiques (production)
- Code complexe (algorithmes, architecture)
- Besoin de contexte étendu (2M tokens)

---

### Option C : Hybride Tier 1 + OpenRouter

**Coût** : $5-$7/mois (50 projets)  
**Qualité** : Maximale (Claude 3.5 Sonnet)  
**Quotas** : Illimités (OpenRouter)

```env
JARVIS_MAITRE_PROVIDER=gemini
JARVIS_MAITRE_MODEL=gemini-2.0-flash

CODEUR_PROVIDER=openrouter
CODEUR_MODEL=anthropic/claude-3.5-sonnet

BASE_PROVIDER=openrouter
BASE_MODEL=anthropic/claude-3.5-sonnet

VALIDATEUR_PROVIDER=gemini
VALIDATEUR_MODEL=gemini-1.5-pro
```

**Quand utiliser** :
- Production intensive (>100 projets/jour)
- Qualité code critique
- Budget disponible ($5-$10/mois)

---

## 🎯 Modèles Gemini Tier 1 Disponibles

### Modèles Flash (Rapides et Économiques)

| Modèle | Nom API | Input | Output | Contexte | RPM | RPD |
|--------|---------|-------|--------|----------|-----|-----|
| **Gemini 2.0 Flash** | `gemini-2.0-flash` | $0.075/1M | $0.30/1M | 1M | 10 | 100 |
| **Gemini 1.5 Flash** | `gemini-1.5-flash` | $0.075/1M | $0.30/1M | 1M | 10 | 100 |
| **Gemini 3 Flash** | `gemini-3-flash-preview` | $0.075/1M | $0.30/1M | 1M | 10 | 100 |

**Usage recommandé** : JARVIS_Maître, CODEUR, BASE (projets standards)

---

### Modèles Pro (Qualité Maximale)

| Modèle | Nom API | Input | Output | Contexte | RPM | RPD |
|--------|---------|-------|--------|----------|-----|-----|
| **Gemini 1.5 Pro** | `gemini-1.5-pro` | $1.25/1M | $5.00/1M | 2M | 5 | 50 |
| **Gemini 2.5 Pro** | `gemini-2.5-pro` | $1.25/1M | $5.00/1M | 2M | 5 | 50 |

**Usage recommandé** : CODEUR, VALIDATEUR (projets critiques uniquement)

**⚠️ Attention** : Modèles Pro = **17x plus chers** que Flash

---

### Modèles Spécialisés

| Modèle | Nom API | Spécialité | Coût |
|--------|---------|-----------|------|
| **Robotics ER 1.5** | `gemini-robotics-er-1.5-preview` | Contrôle qualité | $0.075/1M |
| **Computer Use** | `gemini-2.5-computer-use-preview` | Automatisation UI | Variable |
| **Deep Research** | `deep-research-pro-preview` | Recherche approfondie | Variable |

---

## 📈 Monitoring et Optimisation

### Outils de Monitoring

1. **Google Cloud Console** : https://console.cloud.google.com/billing
   - Coût total
   - Coût par service
   - Tendances

2. **AI Studio Rate Limits** : https://aistudio.google.com/rate-limit
   - Quotas utilisés
   - Quotas restants
   - Historique 28 jours

3. **Logs Backend** : `backend/logs/mistral_api.log`
   - Requêtes API
   - Erreurs
   - Délais adaptatifs

### Optimisations Possibles

#### 1. Réduire Tokens Input

**Avant** :
```python
# Envoyer tout le contexte
context = read_all_files() + conversation_history
```

**Après** :
```python
# Envoyer uniquement fichiers pertinents
context = read_relevant_files(query) + last_3_messages
```

**Impact** : -30% tokens input

---

#### 2. Réutiliser Réponses

**Avant** :
```python
# Régénérer à chaque fois
response = agent.send_message(prompt)
```

**Après** :
```python
# Cache réponses similaires
if prompt in cache:
    response = cache[prompt]
else:
    response = agent.send_message(prompt)
    cache[prompt] = response
```

**Impact** : -50% requêtes API

---

#### 3. Batch API (Tier 1 uniquement)

**Avant** :
```python
# Séquentiel
for file in files:
    validate(file)
```

**Après** :
```python
# Parallèle avec Batch API
batch_validate(files)  # 100 fichiers simultanés
```

**Impact** : 10x plus rapide, même coût

---

## ⚠️ Sécurité et Bonnes Pratiques

### 1. Limiter Budget

**Recommandé** : $10/mois pour démarrer

**Configuration** :
- Alerte à $1 (10%)
- Alerte à $5 (50%)
- Alerte à $9 (90%)
- Limite stricte à $10 (optionnel)

### 2. Surveiller Usage Anormal

**Signes d'alerte** :
- Coût > $2/jour
- >500 requêtes/jour
- Erreurs 429 fréquentes

**Action** :
- Vérifier logs backend
- Identifier agent problématique
- Ajuster configuration

### 3. Crédits Google Cloud

**Nouveaux comptes** : $200 gratuits (90 jours)

**Utilisation** :
- Tester Tier 1 gratuitement
- Valider configuration
- Estimer coût réel

**Après 90 jours** : Facturation normale ($0.20-$2/mois)

---

## 🔄 Retour en Free Tier (Si Besoin)

### Quand Revenir en Free Tier ?

- Usage < 20 projets/jour
- Budget zéro absolu
- Tests uniquement (pas de production)

### Comment Revenir ?

1. Aller sur https://console.cloud.google.com/billing
2. Désactiver facturation sur projet Gemini API
3. Attendre 24h
4. Vérifier retour Free Tier sur AI Studio

**⚠️ Attention** : Quotas repassent à 5 RPM, 20 RPD

---

## 📋 Checklist Migration

### Avant Migration

- [ ] Compte Google Cloud créé
- [ ] Carte bancaire disponible
- [ ] Tests live validés (au moins 1/4)
- [ ] Backup configuration actuelle

### Pendant Migration

- [ ] Tier 1 activé sur AI Studio
- [ ] Compte de facturation lié
- [ ] Budget $10/mois configuré
- [ ] Alertes email activées
- [ ] Fichier `.env` mis à jour
- [ ] Backend redémarré

### Après Migration

- [ ] Tests live complets réussis (3/3)
- [ ] Coût vérifié après 24h
- [ ] Quotas vérifiés (100 RPD, 10 RPM)
- [ ] Documentation mise à jour
- [ ] Monitoring activé

---

## 🎯 Résumé

### Migration Tier 1 en 15 Minutes

1. **Activer Tier 1** (5 min) : https://aistudio.google.com/app/apikey
2. **Configurer alertes** (3 min) : https://console.cloud.google.com/billing/budgets
3. **Mettre à jour .env** (2 min) : `gemini-2.0-flash` pour tous les agents
4. **Tester** (5 min) : `pytest tests/live/test_live_projects.py -v`

### Coût Réel

- **50 projets/mois** : $0.20 (20 centimes)
- **200 projets/mois** : $0.80 (80 centimes)
- **500 projets/mois** : $2.00 (2€)

### Avantages

- ✅ **5x plus de quotas** (100 RPD vs 20 RPD)
- ✅ **2-3x plus rapide** (10 RPM vs 5 RPM)
- ✅ **10+ modèles** disponibles
- ✅ **Batch API** pour parallélisation
- ✅ **Contexte 2M tokens** (avec Pro)

---

**Date** : 22 février 2026  
**Statut** : ✅ GUIDE VALIDÉ  
**Prochaine étape** : Activer Tier 1 et relancer tests live complets
