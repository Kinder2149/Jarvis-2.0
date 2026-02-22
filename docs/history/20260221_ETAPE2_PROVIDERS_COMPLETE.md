# Étape 2 : Abstraction Provider - COMPLÉTÉE

**Date** : 2026-02-21
**Statut** : ✅ COMPLÉTÉ - Prêt pour tests

---

## Fichiers Créés

### Providers (backend/ia/providers/)
- ✅ `__init__.py` - Exports publics
- ✅ `base_provider.py` - Interface abstraite BaseProvider
- ✅ `gemini_provider.py` - Implémentation Google Gemini
- ✅ `openrouter_provider.py` - Implémentation OpenRouter
- ✅ `provider_factory.py` - Factory de sélection provider

### Tests
- ✅ `tests/test_providers.py` - Tests unitaires complets (mock)

---

## Fichiers Modifiés

### Configuration
- ✅ `requirements.txt` - Ajout google-generativeai, openai, httpx
- ✅ `.env.example` - Nouvelle configuration Gemini + OpenRouter

### Backend Agents
- ✅ `backend/agents/base_agent.py` - Utilise ProviderFactory au lieu de MistralClient
- ✅ `backend/agents/agent_factory.py` - Suppression dépendance Agent IDs Mistral
- ✅ `backend/agents/agent_config.py` - Suppression env_var (Agent IDs)

### Services
- ✅ `backend/services/function_executor.py` - Ajout get_available_functions()

---

## Architecture Provider Implémentée

### Interface BaseProvider
```python
class BaseProvider(ABC):
    @abstractmethod
    async def send_message(messages, functions, temperature, max_tokens) -> Dict
    
    @abstractmethod
    def format_functions(functions: List[Dict]) -> Any
    
    @abstractmethod
    def extract_tool_calls(response: Dict) -> List[Dict]
    
    @abstractmethod
    def format_tool_result(tool_call_id, function_name, result) -> Dict
    
    def validate_messages(messages: List[Dict]) -> None
```

### GeminiProvider
- **API** : Google Generative AI (google-generativeai)
- **Modèle par défaut** : gemini-1.5-flash-latest
- **Tool Calling** : FunctionDeclaration natif
- **Conversion** : JSON Schema → Gemini Schema (types MAJUSCULES)
- **Contexte** : 1M-2M tokens selon modèle

### OpenRouterProvider
- **API** : OpenRouter (compatible OpenAI)
- **Modèle par défaut** : anthropic/claude-3.5-sonnet
- **Tool Calling** : Format OpenAI standard
- **Privacy** : ZDR activé par défaut (transforms: ["middle-out"])
- **Headers** : HTTP-Referer + X-Title pour opt-out training

### ProviderFactory
- **Sélection** : Basée sur variables .env (JARVIS_MAITRE_PROVIDER, BASE_PROVIDER, etc.)
- **Cache** : Instances providers mises en cache
- **Validation** : Vérification clés API au démarrage

---

## Configuration .env Requise

```env
# Provider Gemini (JARVIS_Maître)
GEMINI_API_KEY=<ta_clé_google_ai_studio>
GEMINI_MODEL=gemini-1.5-flash-latest

# Provider OpenRouter (BASE/CODEUR/VALIDATEUR)
OPENROUTER_API_KEY=<ta_clé_openrouter>
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
OPENROUTER_PRIVACY=true

# Mapping agents → providers
JARVIS_MAITRE_PROVIDER=gemini
BASE_PROVIDER=openrouter
CODEUR_PROVIDER=openrouter
VALIDATEUR_PROVIDER=openrouter

# Sécurité & Contexte
MAX_CONTEXT_TOKENS=50000
ENABLE_REDACTION=true
```

---

## Tool Calling - Mapping Functions

### Format JARVIS (Standard)
```json
{
  "name": "get_project_file",
  "description": "Lit le contenu d'un fichier",
  "parameters": {
    "type": "object",
    "properties": {
      "file_path": {"type": "string", "description": "..."}
    },
    "required": ["file_path"]
  }
}
```

### Format Gemini (Converti)
```python
FunctionDeclaration(
  name="get_project_file",
  description="Lit le contenu d'un fichier",
  parameters={
    "type": "OBJECT",
    "properties": {
      "file_path": {"type": "STRING", "description": "..."}
    },
    "required": ["file_path"]
  }
)
```

### Format OpenRouter (Converti)
```json
{
  "type": "function",
  "function": {
    "name": "get_project_file",
    "description": "Lit le contenu d'un fichier",
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {"type": "string", "description": "..."}
      },
      "required": ["file_path"]
    }
  }
}
```

---

## Tests Unitaires

### Couverture
- ✅ BaseProvider.validate_messages()
- ✅ GeminiProvider.format_functions()
- ✅ GeminiProvider._convert_schema_to_gemini()
- ✅ GeminiProvider.send_message() (mock)
- ✅ OpenRouterProvider.format_functions()
- ✅ OpenRouterProvider.send_message() (mock)
- ✅ OpenRouterProvider.privacy activé
- ✅ ProviderFactory.create() Gemini
- ✅ ProviderFactory.create() OpenRouter
- ✅ ProviderFactory cache
- ✅ ProviderFactory erreurs (env manquante, API key manquante, provider inconnu)

### Commande
```bash
pytest tests/test_providers.py -v
```

---

## Prochaines Actions (Étape 3)

### AVANT de passer à l'étape 3, tu dois :

1. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

2. **Créer ton fichier .env**
   - Copier `.env.example` → `.env`
   - Renseigner `GEMINI_API_KEY` (obtenir sur https://aistudio.google.com/apikey)
   - Renseigner `OPENROUTER_API_KEY` (obtenir sur https://openrouter.ai/keys)
   - Vérifier les variables PROVIDER

3. **Lancer les tests providers**
   ```bash
   pytest tests/test_providers.py -v
   ```
   **Résultat attendu** : Tous les tests passent (mock)

4. **Valider que tu as bien les clés API**
   - Google AI Studio : https://aistudio.google.com/apikey
   - OpenRouter : https://openrouter.ai/keys

---

## Risques Identifiés

### ⚠️ Risque 1 : Gemini async non supporté
- **Probabilité** : FAIBLE
- **Impact** : BLOQUANT
- **Mitigation** : Vérifier version google-generativeai >= 0.8.0

### ⚠️ Risque 2 : OpenRouter rate limit
- **Probabilité** : MOYENNE
- **Impact** : MOYEN
- **Mitigation** : Retry logic déjà implémenté dans BaseAgent

### ⚠️ Risque 3 : Incompatibilité tool calling
- **Probabilité** : FAIBLE
- **Impact** : CRITIQUE
- **Mitigation** : Tests live étape 3 valideront

---

## Critères de Succès Étape 2

- [x] Interface BaseProvider définie
- [x] GeminiProvider implémenté
- [x] OpenRouterProvider implémenté
- [x] ProviderFactory implémenté
- [x] Tests unitaires créés
- [x] Configuration .env.example mise à jour
- [x] requirements.txt mis à jour
- [x] BaseAgent utilise providers
- [ ] Tests unitaires passent (à valider par utilisateur)
- [ ] Clés API configurées (à faire par utilisateur)

---

## Notes Importantes

1. **Pas de code Mistral supprimé** : On garde mistral_client.py pour rollback si besoin
2. **config_mistral/ conservé** : Sera supprimé à l'étape 5 après validation complète
3. **Agent IDs symboliques** : Les agents utilisent `provider_{agent_name}` comme ID
4. **Function calling** : Géré nativement par chaque provider
5. **Orchestration** : Reste inchangée (marqueurs textuels indépendants du provider)

---

## Prochaine Étape

**Étape 3 : Migration JARVIS_Maître vers Gemini**
- Créer prompt provider-agnostic
- Tester tool calling Gemini
- Valider orchestration fonctionne
- Test live simple (hello.py)
