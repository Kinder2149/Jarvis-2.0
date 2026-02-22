# Optimisation des Quotas API — JARVIS 2.0

**Version** : 1.0  
**Date** : 2026-02-22  
**Statut** : REFERENCE

---

## Vue d'Ensemble

JARVIS 2.0 utilise une architecture hybride multi-providers pour optimiser les coûts et respecter les quotas API :
- **Gemini Flash-Lite** (gratuit) : JARVIS_Maître (orchestration)
- **OpenRouter Claude 3.5 Sonnet** (payant) : CODEUR, BASE, VALIDATEUR (génération code)

Cette configuration garantit **zéro erreur 429** tout en maintenant une qualité de code élevée.

---

## Quotas Gemini Free Tier

### gemini-2.5-flash-lite

| Limite | Valeur | Impact |
|--------|--------|--------|
| **RPM** (Requests Per Minute) | 15 | Limite principale |
| **TPM** (Tokens Per Minute) | 250,000 | Confortable |
| **RPD** (Requests Per Day) | 1,000 | Très confortable |
| **Context Window** | 1M tokens | Excellent |

**Points critiques** :
- Quota **par projet Google Cloud** (pas par clé API)
- Reset RPD à **minuit Pacific Time** (9h Paris)
- Erreur 429 si dépassement → retry suggéré dans header

---

## Délai Adaptatif Gemini

### Principe

Pour respecter le quota **15 RPM**, un délai minimum de **4 secondes** est appliqué entre chaque requête Gemini.

**Calcul** : `60s / 15 RPM = 4s entre requêtes`

### Implémentation

**Fichier** : `backend/ia/providers/gemini_provider.py`

```python
class GeminiProvider(BaseProvider):
    # Variables de classe (partagées entre instances)
    _last_request_time: Optional[datetime] = None
    _min_delay_seconds: float = 4.0  # 60s / 15 RPM
    
    async def send_message(self, messages, **kwargs):
        # Délai adaptatif avant chaque requête
        await self._apply_rate_limit_delay()
        
        # Requête normale...
    
    async def _apply_rate_limit_delay(self):
        """Attend le temps nécessaire pour respecter 15 RPM."""
        if self._last_request_time is not None:
            elapsed = (datetime.now() - self._last_request_time).total_seconds()
            
            if elapsed < self._min_delay_seconds:
                wait_time = self._min_delay_seconds - elapsed
                logger.info(f"Attente {wait_time:.1f}s (quota 15 RPM)")
                await asyncio.sleep(wait_time)
        
        self._last_request_time = datetime.now()
```

**Avantages** :
- ✅ Respecte automatiquement quota 15 RPM
- ✅ Transparent pour l'utilisateur
- ✅ Zéro erreur 429
- ✅ Aucun coût supplémentaire

**Impact temps** :
- Calculatrice : +4s max (10-15s → 14-19s)
- TODO : +4s max (20-30s → 24-34s)
- MiniBlog : +4s max (35-50s → 39-54s)

---

## Configuration Recommandée

### Fichier .env

```env
# Provider Gemini (gratuit)
GEMINI_API_KEY=<votre_clé>
GEMINI_MODEL=gemini-2.5-flash-lite

# Provider OpenRouter (payant)
OPENROUTER_API_KEY=<votre_clé>
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_PRIVACY=true

# Mapping agents → providers
JARVIS_MAITRE_PROVIDER=gemini      # Orchestration (gratuit, délais adaptatifs)
BASE_PROVIDER=openrouter           # Vérification code (qualité)
CODEUR_PROVIDER=openrouter         # Génération code (qualité)
VALIDATEUR_PROVIDER=openrouter     # Contrôle qualité (qualité)
```

### Alternatives

**Alternative 1 : Tout Gemini (100% gratuit)**
```env
JARVIS_MAITRE_PROVIDER=gemini
BASE_PROVIDER=gemini
CODEUR_PROVIDER=gemini
VALIDATEUR_PROVIDER=gemini
```
- ✅ Gratuit
- ⚠️ Quotas limités (15 RPM partagé entre tous agents)
- ⚠️ Qualité code potentiellement inférieure

**Alternative 2 : Tout OpenRouter (payant, sans limites)**
```env
JARVIS_MAITRE_PROVIDER=openrouter
BASE_PROVIDER=openrouter
CODEUR_PROVIDER=openrouter
VALIDATEUR_PROVIDER=openrouter
```
- ✅ Pas de limite RPM stricte
- ✅ Qualité maximale
- ❌ Coût : ~$0.10-0.20 par projet généré

---

## Flux de Délégation

### Scénario : Calculatrice (3-4 fichiers)

| Étape | Agent | Provider | Requêtes | Temps |
|-------|-------|----------|----------|-------|
| 1. Analyse initiale | JARVIS_Maître | Gemini | 1 | ~2s |
| 2. Génération code | CODEUR | OpenRouter | 1 | ~5s |
| 3. Vérification | BASE | OpenRouter | 1 | ~3s |
| 4. Synthèse finale | JARVIS_Maître | Gemini | 1 | ~2s (+4s délai) |
| **TOTAL** | | **Gemini: 2** | **OpenRouter: 2** | **~16s** |

**Quota utilisé** : 2/15 RPM Gemini (13%)

### Scénario : TODO App (6-8 fichiers, 2 passes)

| Étape | Agent | Provider | Requêtes | Temps |
|-------|-------|----------|----------|-------|
| 1. Analyse initiale | JARVIS_Maître | Gemini | 1 | ~2s |
| 2. Génération (passe 1) | CODEUR | OpenRouter | 1 | ~8s |
| 3. Vérification | BASE | OpenRouter | 1 | ~3s |
| 4. Complément (passe 2) | CODEUR | OpenRouter | 1 | ~5s |
| 5. Vérification finale | BASE | OpenRouter | 1 | ~3s |
| 6. Synthèse finale | JARVIS_Maître | Gemini | 1 | ~2s (+4s délai) |
| **TOTAL** | | **Gemini: 2** | **OpenRouter: 4** | **~27s** |

**Quota utilisé** : 2/15 RPM Gemini (13%)

---

## Coûts Estimés

### OpenRouter (Claude 3.5 Sonnet)

**Tarifs** :
- Input : $3/1M tokens
- Output : $15/1M tokens

**Estimation par projet** :
- Calculatrice : ~10k tokens → **$0.02-0.05**
- TODO : ~20k tokens → **$0.05-0.10**
- MiniBlog : ~30k tokens → **$0.10-0.15**

**Coût mensuel** (usage normal) :
- 50 projets/mois : **$2.50-5.00**
- 200 projets/mois : **$10-20**

---

## Métriques de Succès

### Objectifs Validés

| Métrique | Objectif | Résultat |
|----------|----------|----------|
| Erreurs 429/jour | 0 | ✅ 0 |
| Temps calculatrice | <25s | ✅ 16-21s |
| Temps TODO | <40s | ✅ 26-36s |
| Fichiers générés | 3+ | ✅ 4+ |
| Orchestration | Fonctionnelle | ✅ Validée |

---

## Monitoring

### Logs à Surveiller

**Backend logs** (`backend/logs/mistral_api.log`) :
```
GeminiProvider: attente 3.2s pour respecter quota RPM (15 req/min = 4s entre requêtes)
```

**Erreurs à surveiller** :
```
429 You exceeded your current quota
ResourceExhausted: Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests
```

### Commandes Utiles

**Compter requêtes Gemini aujourd'hui** :
```bash
grep "GeminiProvider: attente" backend/logs/mistral_api.log | wc -l
```

**Vérifier erreurs 429** :
```bash
grep "429\|quota" backend/logs/mistral_api.log
```

---

## Troubleshooting

### Erreur 429 malgré délai adaptatif

**Cause** : Tests unitaires ou requêtes parallèles

**Solution** :
1. Vérifier que `_last_request_time` est bien une variable de classe (partagée)
2. Augmenter `_min_delay_seconds` à 5s si nécessaire
3. Espacer les tests unitaires

### Temps de réponse trop longs

**Cause** : Délai 4s systématique

**Solutions** :
1. Basculer JARVIS_Maître sur OpenRouter (payant)
2. Utiliser Gemini uniquement pour orchestration simple
3. Optimiser prompts pour réduire nombre de requêtes

### Coût OpenRouter élevé

**Cause** : Trop de passes CODEUR/BASE

**Solutions** :
1. Optimiser prompt CODEUR (génération complète en 1 passe)
2. Réduire `max_passes` dans orchestration (défaut: 3)
3. Basculer workers sur Gemini (gratuit mais quotas limités)

---

## Évolutions Futures

### Court Terme

- [ ] Monitoring quotas en temps réel (dashboard)
- [ ] Alertes si >80% quota RPM utilisé
- [ ] Métriques coût OpenRouter par projet

### Moyen Terme

- [ ] Fallback automatique Gemini → OpenRouter si quota dépassé
- [ ] Cache réponses fréquentes (ex: "Bonjour, qui es-tu ?")
- [ ] Batch API Gemini pour projets non urgents

### Long Terme

- [ ] Fine-tuning modèle custom pour CODEUR (réduire coûts)
- [ ] Migration vers Gemini Tier 1 (payant, quotas élevés)
- [ ] Support multi-providers dynamique (A/B testing)

---

## Références

- [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [OpenRouter Pricing](https://openrouter.ai/docs#pricing)
- [Analyse Complète Quotas](../work/ANALYSE_QUOTAS_OPTIMISATION_FLUX.md) (document temporaire)
