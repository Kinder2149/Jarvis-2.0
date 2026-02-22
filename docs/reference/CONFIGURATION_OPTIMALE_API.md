# Configuration Optimale API - JARVIS 2.0

**Date de validation** : 22 février 2026  
**Statut** : ✅ RÉFÉRENCE VALIDÉE  
**Version** : 1.0

---

## Configuration Validée (100% Gemini Free Tier)

### Variables d'Environnement (.env)

```env
# Provider par défaut
DEFAULT_PROVIDER=gemini

# Providers spécifiques par agent
JARVIS_MAITRE_PROVIDER=gemini
CODEUR_PROVIDER=gemini
BASE_PROVIDER=gemini
VALIDATEUR_PROVIDER=gemini

# Modèles Gemini spécifiques
GEMINI_MODEL=gemini-3-flash-preview
JARVIS_MAITRE_MODEL=gemini-3-flash-preview
CODEUR_MODEL=gemini-3-flash-preview
BASE_MODEL=gemini-3-flash-preview
VALIDATEUR_MODEL=gemini-robotics-er-1.5-preview

# Clé API Gemini
GEMINI_API_KEY=<votre_clé>
```

### Mapping Agent → Modèle

| Agent | Provider | Modèle | RPM | RPD | Raison |
|-------|----------|--------|-----|-----|--------|
| **JARVIS_Maître** | gemini | `gemini-3-flash-preview` | 5 | 20 | Orchestration rapide, Function Calling |
| **CODEUR** | gemini | `gemini-3-flash-preview` | 5 | 20 | Génération code, quotas partagés |
| **BASE** | gemini | `gemini-3-flash-preview` | 5 | 20 | Validation rapide, quotas partagés |
| **VALIDATEUR** | gemini | `gemini-robotics-er-1.5-preview` | 10 | 20 | Contrôle qualité, quota séparé |

**Quotas cumulés théoriques** : 15 RPM (5 + 10), 40 RPD (20 + 20)

---

## Résultats Validation (Tests Live)

### Test 1 : Calculatrice CLI (Niveau 1)
- ✅ 4 fichiers générés
- ✅ 7/7 tests passants
- ✅ Durée : 2min 44s
- ✅ Qualité : Structure propre, gestion erreurs, tests complets

### Test 2 : Gestionnaire TODO (Niveau 2)
- ✅ 7 fichiers générés
- ✅ 14/14 tests passants
- ✅ Durée : 3min 10s
- ✅ Qualité : Architecture modulaire, persistence JSON, CLI fonctionnel

### Test 3 : API REST Mini-Blog (Niveau 3)
- ✅ 5 fichiers générés
- ✅ 6/6 tests passants
- ✅ Durée : 3min 16s
- ✅ Qualité : FastAPI + SQLAlchemy, modèles Pydantic, tests API

**Total** : 16 fichiers, 27/27 tests (100%), ~9 minutes, 0 erreur 429

---

## Modèles Gemini Disponibles

### Modèles avec Function Calling (Utilisables)

| Nom Console | Nom API | Input Tokens | RPM (Free) | RPD (Free) |
|-------------|---------|--------------|------------|------------|
| Gemini 3 Flash | `gemini-3-flash-preview` | 1M | 5 | 20 |
| Gemini 3 Pro | `gemini-3-pro-preview` | 1M | 0 | 0 |
| Gemini 3.1 Pro | `gemini-3.1-pro-preview` | 1M | 0 | 0 |
| Gemini Robotics ER 1.5 | `gemini-robotics-er-1.5-preview` | 1M | 10 | 20 |
| Gemini 2.5 Flash | `gemini-2.5-flash` | 1M | 5 | 20 |
| Gemini 2.5 Pro | `gemini-2.5-pro` | 1M | 0 | 0 |
| Gemini 2.0 Flash | `gemini-2.0-flash` | 1M | 0 | 0 |

**Note** : Modèles avec "0 RPM" nécessitent Tier 1+ (Cloud Billing activé)

### Modèles SANS Function Calling (Inutilisables)

| Nom Console | Nom API | Input Tokens | RPM (Free) |
|-------------|---------|--------------|------------|
| Gemma 3 27B | `gemma-3-27b-it` | 131K | 30 |
| Gemma 3 12B | `gemma-3-12b-it` | 32K | 30 |
| Gemma 3 4B | `gemma-3-4b-it` | 32K | 30 |
| Gemma 3 1B | `gemma-3-1b-it` | 32K | 30 |

**Raison exclusion** : Les agents JARVIS utilisent des tools (`get_project_file`, `get_library_document`, etc.) qui nécessitent Function Calling.

---

## Système de Rate Limits Gemini

### Dimensions

1. **RPM** (Requests Per Minute) : Requêtes par minute
2. **TPM** (Tokens Per Minute) : Tokens par minute (input)
3. **RPD** (Requests Per Day) : Requêtes par jour (reset minuit Pacific Time)

**Important** : Les limites s'appliquent **par projet**, pas par clé API. Dépasser UNE SEULE limite déclenche une erreur 429.

### Tiers d'Usage

| Tier | Qualifications | Quotas Estimés |
|------|---------------|----------------|
| **Free** | Pays éligibles | 5-10 RPM, 20 RPD |
| **Tier 1** | Cloud Billing activé | 10-15 RPM, 50-100 RPD |
| **Tier 2** | Dépense > $250 + 30j | 50+ RPM, 500+ RPD |
| **Tier 3** | Dépense > $1,000 + 30j | 100+ RPM, 1000+ RPD |

**Upgrade** : https://aistudio.google.com/app/apikey

---

## Délai Adaptatif (Protection Quotas)

### Implémentation

**Fichier** : `backend/ia/providers/gemini_provider.py`

```python
class GeminiProvider(BaseProvider):
    _last_request_time: Optional[datetime] = None
    _min_delay_seconds: float = 4.0  # 60s / 15 RPM
    
    async def send_message(self, ...):
        # Attente adaptative
        if self._last_request_time:
            elapsed = (datetime.now() - self._last_request_time).total_seconds()
            if elapsed < self._min_delay_seconds:
                wait_time = self._min_delay_seconds - elapsed
                logger.info(f"GeminiProvider: attente {wait_time:.1f}s pour respecter quota RPM")
                await asyncio.sleep(wait_time)
        
        # Requête API
        response = await self.client.generate_content_async(...)
        self._last_request_time = datetime.now()
        return response
```

**Résultat** : 0 erreur 429 observée lors des tests

---

## Configurations Alternatives

### Configuration Hybride (Recommandée si Budget)

```env
# Orchestration gratuite
JARVIS_MAITRE_PROVIDER=gemini
JARVIS_MAITRE_MODEL=gemini-3-flash-preview

# Workers payants (qualité supérieure)
CODEUR_PROVIDER=openrouter
CODEUR_MODEL=anthropic/claude-3.5-sonnet

BASE_PROVIDER=openrouter
BASE_MODEL=anthropic/claude-3.5-sonnet

VALIDATEUR_PROVIDER=openrouter
VALIDATEUR_MODEL=anthropic/claude-3.5-sonnet

# Clés API
GEMINI_API_KEY=<votre_clé>
OPENROUTER_API_KEY=<votre_clé>
```

**Avantages** :
- Qualité code maximale (Claude 3.5 Sonnet)
- Pas de limite RPM stricte
- JARVIS_Maître gratuit (économie)

**Coût estimé** : $5-10/mois (50-100 projets)

### Configuration Tier 1 Gemini

**Action** : Activer Cloud Billing sur projet Google Cloud

**Quotas estimés** :
- RPM : 10-15 (au lieu de 5)
- RPD : 50-100 (au lieu de 20)
- Batch API : 100 requêtes concurrentes

**Coût** : Variable selon usage (facturation Google Cloud)

---

## Support Multi-Modèles

### Implémentation

**Fichier** : `backend/ia/providers/provider_factory.py`

```python
def _create_gemini(self, agent_name: str = None) -> BaseProvider:
    """Créer provider Gemini avec modèle spécifique par agent"""
    
    # Sélection modèle spécifique par agent
    model = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash-latest')
    if agent_name:
        agent_model_key = f"{agent_name.upper()}_MODEL"
        model = os.getenv(agent_model_key, model)
    
    logger.info(f"Creating GeminiProvider for {agent_name or 'default'}: model={model}")
    
    return GeminiProvider(
        api_key=self.gemini_api_key,
        model=model
    )
```

**Permet** : Assigner un modèle différent à chaque agent pour optimiser quotas et coûts

---

## Recommandations d'Usage

### Pour Usage Personnel (<20 projets/jour)

✅ **Configuration actuelle (100% Gemini Free Tier)**
- 100% gratuit
- Qualité suffisante
- Aucune erreur bloquante
- Délai adaptatif efficace

**Action** : Continuer avec configuration validée

### Pour Usage Intensif (>20 projets/jour)

**Option 1** : Upgrade Tier 1 Gemini
- Quotas augmentés (10-15 RPM, 50-100 RPD)
- 100% Gemini (pas de dépendance externe)
- Coût variable selon usage

**Option 2** : Configuration Hybride ⭐ RECOMMANDÉ
- Qualité code maximale (Claude 3.5 Sonnet)
- Pas de limite RPM stricte
- Coût prévisible ($5-10/mois)

### Pour Production Critique

**Configuration Hybride + Tier 1 Gemini**
- JARVIS_Maître : Gemini Tier 1 (quotas élevés)
- Workers : OpenRouter Claude 3.5 Sonnet (qualité)
- Redondance et résilience maximales

---

## Monitoring et Maintenance

### Vérification Quotas

**Console AI Studio** : https://aistudio.google.com/rate-limit

**Fréquence recommandée** : Quotidienne si usage intensif

### Logs Backend

**Fichier** : `backend/logs/mistral_api.log`

**Recherche erreurs quotas** :
```bash
Get-Content backend\logs\mistral_api.log | Select-String -Pattern "429|quota|rate limit"
```

### Demande Augmentation Quotas

**Formulaire Google** : https://forms.gle/ETzX94k8jf7iSotH9

**Note** : Pas de garantie d'approbation, dépend de l'usage et du tier

---

## Références

- Documentation Gemini API : https://ai.google.dev/gemini-api/docs
- Rate Limits : https://ai.google.dev/gemini-api/docs/rate-limits
- Modèles disponibles : https://ai.google.dev/models/gemini
- OpenRouter : https://openrouter.ai/docs
- Tests validation : `docs/work/PERFORMANCES_CONFIG_GEMINI_100PCT.md`

---

## Changelog

### Version 1.0 (22 février 2026)
- Configuration initiale validée
- Tests live 3/3 réussis (Calculatrice, TODO, MiniBlog)
- Support multi-modèles implémenté
- Délai adaptatif validé (0 erreur 429)
- Documentation complète créée
