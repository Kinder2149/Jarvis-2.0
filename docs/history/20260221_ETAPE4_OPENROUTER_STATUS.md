# Étape 4 : Migration BASE/CODEUR/VALIDATEUR vers OpenRouter - BLOQUÉE

**Date** : 2026-02-21
**Statut** : ⚠️ BLOQUÉ - Crédits OpenRouter requis

---

## Objectif

Migrer BASE, CODEUR et VALIDATEUR de Mistral vers OpenRouter (Claude 3.5 Sonnet) avec support complet du tool calling.

---

## Travail Effectué

### ✅ Prompts Provider-Agnostic Créés

**Fichiers créés** :
- `config_agents/BASE.md` (v3.0) - Prompt sans références Mistral
- `config_agents/CODEUR.md` (v3.0) - Règles absolues + patterns
- `config_agents/VALIDATEUR.md` (v2.0) - Format de validation strict

### ✅ Configuration Mise à Jour

**Modifications** :
- `backend/agents/agent_config.py` : Ajout `prompt_file` pour BASE, CODEUR, VALIDATEUR
- Chargement dynamique des prompts via `BaseAgent._load_system_prompt()`

### ✅ Tests d'Intégration Créés

**Fichier** : `tests/test_openrouter_integration.py`
- `test_base_openrouter_simple` : Communication basique BASE
- `test_codeur_openrouter_simple` : Génération code simple
- `test_validateur_openrouter_simple` : Validation code

---

## Problème Identifié

### ❌ Erreur OpenRouter : 402 Insufficient Credits

**Message d'erreur** :
```
Error code: 402 - {'error': {'message': 'Insufficient credits. This account never purchased credits. Make sure your key is on the correct account or org, and if so, purchase more at https://openrouter.ai/settings/credits', 'code': 402}}
```

**Cause** :
- OpenRouter est un service **payant**
- Le compte `OPEN_ROUTER_JARVIS` n'a jamais acheté de crédits
- Impossible de tester les agents sans crédits

---

## Solutions Possibles

### Option 1 : Acheter Crédits OpenRouter ⭐ RECOMMANDÉ

**Avantages** :
- Accès à Claude 3.5 Sonnet (meilleur modèle pour code)
- Privacy ZDR (Zero Data Retention)
- Tarification à l'usage (pay-as-you-go)

**Coût estimé** :
- Claude 3.5 Sonnet : ~$3/M input tokens, ~$15/M output tokens
- Pour tests : $5-10 suffisent
- Pour usage régulier : $20-50/mois

**Procédure** :
1. Aller sur https://openrouter.ai/settings/credits
2. Acheter crédits (minimum $5)
3. Relancer les tests

---

### Option 2 : Utiliser Gemini pour Tous les Agents

**Avantages** :
- Gratuit (quotas généreux)
- Déjà configuré et fonctionnel
- Gemini 2.5 Flash performant

**Inconvénients** :
- Pas de séparation orchestrateur/workers
- Quotas partagés entre tous les agents
- Moins optimal pour génération code (vs Claude)

**Modifications requises** :
```env
# Tous les agents sur Gemini
JARVIS_MAITRE_PROVIDER=gemini
BASE_PROVIDER=gemini
CODEUR_PROVIDER=gemini
VALIDATEUR_PROVIDER=gemini
```

---

### Option 3 : Rester sur Mistral (Rollback)

**Avantages** :
- Déjà payé et fonctionnel
- Configuration existante validée
- Aucun coût supplémentaire

**Inconvénients** :
- Pas d'architecture hybride
- Abandon de l'objectif initial
- Retour en arrière

---

## Recommandation

### ⭐ Option 1 : Acheter Crédits OpenRouter

**Justification** :
1. **Architecture hybride optimale** :
   - Gemini (orchestration) : Gratuit, excellent pour raisonnement
   - Claude 3.5 Sonnet (code) : Payant, meilleur pour génération code

2. **Coût raisonnable** :
   - $5-10 pour tests complets
   - $20-50/mois pour usage régulier
   - ROI élevé (qualité code supérieure)

3. **Privacy** :
   - ZDR activé (données non stockées)
   - Conforme RGPD

4. **Flexibilité** :
   - Accès à 100+ modèles via OpenRouter
   - Changement de modèle facile

---

## État Actuel du Code

### ✅ Prêt pour OpenRouter

**Architecture** :
- ✅ Abstraction provider fonctionnelle
- ✅ OpenRouterProvider implémenté
- ✅ Prompts provider-agnostic créés
- ✅ Configuration agents mise à jour
- ✅ Tests d'intégration écrits

**Manque uniquement** :
- ❌ Crédits OpenRouter pour tester

---

## Prochaines Actions

### Si Option 1 (OpenRouter) ✅ RECOMMANDÉ

1. **Acheter crédits OpenRouter**
   ```
   URL : https://openrouter.ai/settings/credits
   Montant : $10 (suffisant pour tests + usage initial)
   ```

2. **Tester BASE**
   ```bash
   pytest tests/test_openrouter_integration.py::test_base_openrouter_simple -v -s
   ```

3. **Tester CODEUR**
   ```bash
   pytest tests/test_openrouter_integration.py::test_codeur_openrouter_simple -v -s
   ```

4. **Tester VALIDATEUR**
   ```bash
   pytest tests/test_openrouter_integration.py::test_validateur_openrouter_simple -v -s
   ```

5. **Test orchestration complète**
   ```bash
   # Test délégation JARVIS_Maître → CODEUR
   pytest tests/test_live_projects.py::test_calculatrice -v -s
   ```

---

### Si Option 2 (Gemini pour tous)

1. **Modifier .env**
   ```env
   BASE_PROVIDER=gemini
   CODEUR_PROVIDER=gemini
   VALIDATEUR_PROVIDER=gemini
   ```

2. **Tester avec Gemini**
   ```bash
   pytest tests/test_openrouter_integration.py -v -s
   ```

3. **Valider orchestration**
   ```bash
   pytest tests/test_live_projects.py::test_calculatrice -v -s
   ```

---

## Fichiers Créés (Étape 4)

### Prompts
- `config_agents/BASE.md` (v3.0)
- `config_agents/CODEUR.md` (v3.0)
- `config_agents/VALIDATEUR.md` (v2.0)

### Tests
- `tests/test_openrouter_integration.py`

### Documentation
- `docs/work/20260221_ETAPE4_OPENROUTER_STATUS.md` (ce fichier)

---

## Critères de Succès Étape 4

- [x] Prompts provider-agnostic créés
- [x] Configuration agents mise à jour
- [x] Tests d'intégration écrits
- [ ] **Crédits OpenRouter achetés** ⚠️ BLOQUANT
- [ ] Tests BASE/CODEUR/VALIDATEUR passent
- [ ] Orchestration complète validée

---

## Notes Importantes

### OpenRouter vs Gemini

**OpenRouter (Claude 3.5 Sonnet)** :
- ✅ Meilleur pour génération code
- ✅ Privacy ZDR
- ✅ Accès 100+ modèles
- ❌ Payant ($3-15/M tokens)

**Gemini 2.5 Flash** :
- ✅ Gratuit (quotas généreux)
- ✅ Excellent pour orchestration
- ✅ Bon pour code (mais < Claude)
- ❌ Quotas partagés

### Architecture Hybride Optimale

```
JARVIS_Maître (Gemini)
    ↓ délègue
CODEUR (Claude 3.5 Sonnet via OpenRouter)
    ↓ produit code
VALIDATEUR (Claude 3.5 Sonnet via OpenRouter)
    ↓ valide
BASE (Claude 3.5 Sonnet via OpenRouter)
    ↓ rapport
JARVIS_Maître (Gemini)
```

**Coût estimé** : $0.50-2/projet (selon complexité)

---

## Commandes Utiles

### Vérifier crédits OpenRouter
```bash
curl https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

### Tester connexion OpenRouter
```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -d '{
    "model": "anthropic/claude-3.5-sonnet",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### Lister modèles OpenRouter
```bash
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```
