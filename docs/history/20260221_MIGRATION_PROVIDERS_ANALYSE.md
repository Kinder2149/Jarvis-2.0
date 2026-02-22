# Analyse Migration vers Architecture Hybride Gemini/OpenRouter

**Date** : 2026-02-21
**Statut** : WORK - Analyse en cours
**Objectif** : Remplacer complètement Mistral par Gemini (JARVIS_Maître) + OpenRouter (workers)

---

## 1. FICHIERS À SUPPRIMER (Mistral uniquement)

### Backend
- `backend/ia/mistral_client.py` (405 lignes) — Client Mistral complet
- `backend/logs/mistral_api.log` (30159+ lignes) — Logs API Mistral

### Configuration
- `config_mistral/` (dossier complet) — Prompts agents Mistral
  - `config_mistral/README.md`
  - `config_mistral/agents/BASE.md`
  - `config_mistral/agents/CODEUR.md`
  - `config_mistral/agents/JARVIS_MAITRE.md`
  - `config_mistral/agents/VALIDATEUR.md`
  - `config_mistral/tools/` (3 fichiers)

### Tests
- `tests/test_mistral_client_optimize.py`
- `tests/manual/test_config_mistral.py`
- `tests/__pycache__/test_mistral_client_optimize.*.pyc` (3 fichiers)
- `tests/manual/__pycache__/test_config_mistral.*.pyc`

---

## 2. FICHIERS À MODIFIER (Dépendances Mistral)

### Configuration
- `requirements.txt` : Supprimer `mistralai==1.2.6`, ajouter `google-generativeai`, `openai`
- `.env.example` : Remplacer variables Mistral par Gemini + OpenRouter

### Backend Core
- `backend/agents/base_agent.py` (L5, L44-48) : Import + instanciation MistralClient
- `backend/agents/agent_factory.py` (L45-60) : Instanciation agents avec MistralClient
- `backend/agents/agent_config.py` (L106-113) : Référence `config_mistral/agents/`

### API & Services
- `backend/api.py` (3 mentions) : Logs/commentaires Mistral
- `backend/logging_config.py` (4 mentions) : Logger `mistral_api`
- `backend/services/function_executor.py` (1 mention) : Commentaire
- `backend/services/project_context.py` (1 mention) : Commentaire

### Database
- `backend/db/migrations.py` (1 mention) : Commentaire historique

---

## 3. FICHIERS À CRÉER (Nouvelle Architecture)

### Providers
- `backend/ia/providers/__init__.py`
- `backend/ia/providers/base_provider.py` — Interface abstraite
- `backend/ia/providers/gemini_provider.py` — Provider Google Gemini
- `backend/ia/providers/openrouter_provider.py` — Provider OpenRouter
- `backend/ia/providers/provider_factory.py` — Factory sélection provider

### Services (Sécurité/Contexte)
- `backend/services/context_selector.py` — Sélection contexte intelligent
- `backend/services/data_redaction.py` — Redaction données sensibles

### Configuration Agents (Nouveaux Prompts)
- `config_agents/` (nouveau dossier, remplace config_mistral)
  - `config_agents/README.md`
  - `config_agents/BASE.md` — Prompt BASE (provider-agnostic)
  - `config_agents/CODEUR.md` — Prompt CODEUR (provider-agnostic)
  - `config_agents/VALIDATEUR.md` — Prompt VALIDATEUR (provider-agnostic)
  - `config_agents/JARVIS_MAITRE.md` — Prompt JARVIS_Maître (provider-agnostic)

### Tests
- `tests/test_providers.py` — Tests unitaires providers
- `tests/test_gemini_provider.py` — Tests spécifiques Gemini
- `tests/test_openrouter_provider.py` — Tests spécifiques OpenRouter
- `tests/test_context_selector.py` — Tests sélection contexte
- `tests/test_data_redaction.py` — Tests redaction

---

## 4. VARIABLES .ENV (Avant/Après)

### AVANT (Mistral)
```env
MISTRAL_API_KEY=...
MISTRAL_MODEL=mistral-small-latest
JARVIS_BASE_AGENT_ID=ag_019ba8ca8eaa76288371e13fb962d1ed
JARVIS_MAITRE_AGENT_ID=ag_019c514a04a874159a21135b856a40e3
JARVIS_CODEUR_AGENT_ID=...
JARVIS_VALIDATEUR_AGENT_ID=...
USE_MISTRAL_AGENT_API=1
```

### APRÈS (Gemini + OpenRouter)
```env
# Provider Gemini (JARVIS_Maître uniquement)
GEMINI_API_KEY=...
GEMINI_MODEL=gemini-1.5-flash-latest

# Provider OpenRouter (BASE/CODEUR/VALIDATEUR)
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_PRIVACY=true

# Mapping agents → providers
JARVIS_MAITRE_PROVIDER=gemini
BASE_PROVIDER=openrouter
CODEUR_PROVIDER=openrouter
VALIDATEUR_PROVIDER=openrouter

# Contexte & Sécurité
MAX_CONTEXT_TOKENS=50000
ENABLE_REDACTION=true
```

---

## 5. ARCHITECTURE CIBLE

### Structure Providers
```
backend/ia/
├── __init__.py
└── providers/
    ├── __init__.py
    ├── base_provider.py          # ABC avec send_message(), format_functions(), extract_tool_calls()
    ├── gemini_provider.py        # Implémentation Google Gemini
    ├── openrouter_provider.py    # Implémentation OpenRouter
    └── provider_factory.py       # Factory: create(agent_name) -> BaseProvider
```

### Injection Provider dans Agents
```python
# backend/agents/base_agent.py (AVANT)
from backend.ia.mistral_client import MistralClient
self.client = MistralClient(agent_id, temperature, max_tokens)

# backend/agents/base_agent.py (APRÈS)
from backend.ia.providers.provider_factory import ProviderFactory
self.provider = ProviderFactory.create(agent_name=name)
```

---

## 6. TOOL CALLING (Mapping Functions)

### Format Mistral (ACTUEL)
```json
{
  "type": "object",
  "properties": {
    "filepath": {"type": "string", "description": "..."}
  },
  "required": ["filepath"]
}
```

### Format Gemini (CIBLE pour JARVIS_Maître)
```python
# google.generativeai.protos.FunctionDeclaration
{
  "name": "get_project_file",
  "description": "...",
  "parameters": {
    "type": "OBJECT",
    "properties": {
      "filepath": {"type": "STRING", "description": "..."}
    },
    "required": ["filepath"]
  }
}
```

### Format OpenRouter (CIBLE pour BASE/CODEUR/VALIDATEUR)
```json
{
  "type": "function",
  "function": {
    "name": "get_project_file",
    "description": "...",
    "parameters": {
      "type": "object",
      "properties": {
        "filepath": {"type": "string", "description": "..."}
      },
      "required": ["filepath"]
    }
  }
}
```

---

## 7. RISQUES IDENTIFIÉS

### Risque 1 : Incompatibilité Tool Calling
- **Probabilité** : MOYENNE
- **Impact** : CRITIQUE
- **Mitigation** : Tests unitaires mapping functions avant migration complète

### Risque 2 : Régression Qualité Code
- **Probabilité** : MOYENNE
- **Impact** : ÉLEVÉ
- **Mitigation** : Tests live (calculatrice/TODO/miniblog) avant validation

### Risque 3 : Coûts API Explosifs
- **Probabilité** : FAIBLE
- **Impact** : ÉLEVÉ
- **Mitigation** : Monitoring tokens + limite contexte + caching

### Risque 4 : Perte Orchestration
- **Probabilité** : FAIBLE
- **Impact** : CRITIQUE
- **Mitigation** : Marqueurs délégation indépendants du provider

---

## 8. PLAN D'EXÉCUTION (5 Étapes)

### Étape 1 : Analyse Existant ✅ EN COURS
- [x] Cartographie fichiers Mistral
- [x] Identification dépendances
- [ ] Validation architecture cible

### Étape 2 : Abstraction Provider
- [ ] Créer `BaseProvider` (ABC)
- [ ] Implémenter `GeminiProvider`
- [ ] Implémenter `OpenRouterProvider`
- [ ] Créer `ProviderFactory`
- [ ] Tests unitaires providers (mock)

### Étape 3 : Migration JARVIS_Maître
- [ ] Modifier `agent_factory.py` pour injection provider
- [ ] Modifier `base_agent.py` pour utiliser provider
- [ ] Créer `config_agents/JARVIS_MAITRE.md`
- [ ] Tester tool calling Gemini
- [ ] Test live simple (hello.py)

### Étape 4 : Migration Workers
- [ ] Migrer BASE vers OpenRouter
- [ ] Migrer CODEUR vers OpenRouter
- [ ] Migrer VALIDATEUR vers OpenRouter
- [ ] Créer prompts `config_agents/*.md`
- [ ] Tests live (calculatrice/TODO)

### Étape 5 : Nettoyage & Validation
- [ ] Supprimer `backend/ia/mistral_client.py`
- [ ] Supprimer `config_mistral/`
- [ ] Supprimer tests Mistral
- [ ] Nettoyer `requirements.txt`
- [ ] Mettre à jour `.env.example`
- [ ] Valider tous tests (238+ passent)
- [ ] Documentation migration

---

## 9. QUESTIONS EN SUSPENS

1. **Modèle Gemini** : gemini-1.5-pro-latest (cher) ou gemini-1.5-flash-latest (rapide) ?
2. **Modèle OpenRouter Phase 1** : anthropic/claude-3.5-sonnet ou autre ?
3. **Redaction** : Phase 1 ou Phase 2 ?
4. **Contexte sélectif** : Embedding (précis) ou Regex (rapide) ?
5. **Rollback** : Garder Mistral comme fallback ou supprimer complètement ?
6. **Monitoring** : Logs simples ou intégration Langfuse/Helicone ?
7. **Budget API** : Limite mensuelle ?
8. **Tests live** : Nouveau test "migration" ou réutiliser existants ?

---

## 10. PROCHAINES ACTIONS IMMÉDIATES

1. Créer structure `backend/ia/providers/`
2. Implémenter `BaseProvider` (interface)
3. Implémenter `GeminiProvider` (avec tool calling)
4. Implémenter `OpenRouterProvider` (avec tool calling)
5. Créer `ProviderFactory`
6. Tests unitaires providers

**Critère de succès Étape 2** : 3 providers implémentés + tests passent (mock)
