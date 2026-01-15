# JARVIS

Plateforme locale minimale basée sur un **Agent de Base**,
préparée pour évoluer vers un système multi-agents.

## Architecture

- frontend/ : UI de chat simple
- backend/
  - api : interface HTTP
  - ia : clients IA (Mistral)
  - agents : modèle et implémentations d’agents

## Audit factuel — Agent Mistral actuellement utilisé

### Bloc A — Cartographie des fichiers impliqués

- **frontend/script.js**
  - Envoie une requête : `POST http://localhost:8000/chat`
  - Body JSON : `{ "message": "<texte utilisateur>" }`
- **backend/app.py**
  - Initialise l’application et monte le routeur API.
- **backend/api.py**
  - Endpoint `POST /chat`
  - Instancie l’agent via `get_base_agent()`
  - Appelle `agent.handle([{ "role": "user", "content": req.message }])`
- **backend/agents/agent_registry.py**
  - Fournit un singleton d’agent de base.
  - Instancie `BaseAgent(...)` avec un `agent_id` codé en dur.
- **backend/agents/base_agent.py**
  - Préfixe le contexte avec un message `system` et transmet au client Mistral.
- **backend/ia/mistral_client.py**
  - Tente l’API “Agent” via `beta.conversations.start(...)` selon une variable d’environnement.
  - Fallback sur `chat.complete(...)` en cas d’échec.

### Bloc B — Structure réelle des messages envoyés

- **Entrée runtime côté API**
  - Une liste de messages contenant des objets `{role, content}`.
  - Exemple (forme) : un message `user` avec le texte utilisateur.
- **Transformation par l’Agent de Base**
  - Ajout systématique en tête d’un message `{role: "system", content: <instructions>}`.
- **Envoi au fournisseur IA**
  - Même structure de liste `{role, content}` utilisée dans les deux chemins :
    - chemin “Agent” : passé en tant que `inputs`
    - chemin “Chat” : passé en tant que `messages`

### Bloc C — Écarts observables avec un contrat d’API Agent

- **[Format unique utilisé pour deux API différentes]**
  - Le même format de messages `{role, content}` est envoyé à la fois sur le chemin “Agent” et le chemin “Chat”.
- **[Rôles observés]**
  - Les rôles effectivement construits sont `system` (injecté) et `user` (runtime).
- **[Fallback implicite]**
  - En cas d’exception sur le chemin “Agent”, bascule automatique vers “Chat” sans signalisation fonctionnelle au client.

### Bloc D — Risques long terme si non corrigé

- **[Non-déterminisme de comportement]**
  - Une même requête peut être traitée soit par le chemin “Agent”, soit par le fallback “Chat”, selon des erreurs ou conditions externes.
- **[Dérive contractuelle]**
  - Si le schéma attendu par l’API “Agent” diffère du format envoyé, le système peut tomber en fallback de manière permanente.
- **[Observabilité limitée]**
  - Le fallback est visible principalement via logs côté serveur.
- **[Couplage fort]**
  - Dépendance à un `agent_id` fixe ; toute rotation/suppression côté fournisseur peut dégrader le fonctionnement.

## Contrat formel — Agent de Base JARVIS

### 1) Identité de l’agent

- **Nom** : Agent de Base JARVIS
- **Statut** : agent générique de référence (“modèle”)
- **Mission** : comprendre une demande en langage naturel et répondre de manière utile, structurée et honnête, en signalant explicitement les incertitudes.

### 2) Ce que l’agent fait

- Répondre à des questions et fournir des explications accessibles.
- Clarifier une demande ambiguë via des questions courtes et pertinentes.
- Synthétiser et reformuler fidèlement le contexte fourni.
- Proposer des étapes générales de résolution (méthodes, checklists, options), sans action autonome.

### 3) Ce que l’agent ne fera jamais

- Prétendre agir dans le monde réel ou disposer d’accès implicites.
- Mentir sur ses capacités, ses certitudes ou ses sources.
- Aider à contourner des règles, des contrôles, ou des mécanismes de sécurité.
- Produire des instructions dangereuses/illégales.
- Demander ou exposer des secrets (mots de passe, clés, tokens) sans nécessité explicite.

### 4) Comment l’agent est configuré (instructions, personnalité)

- **Ton** : neutre, calme, professionnel.
- **Style** : direct, précis, concis quand possible, structuré quand utile.
- **Honnêteté** : séparer clairement le certain, le probable et l’inconnu ; expliciter les hypothèses.
- **Clarification** : poser 1 à 3 questions maximum si la demande est ambiguë avant de supposer.

### 5) Messages acceptés à l’exécution

- Messages exprimant une question, une demande d’aide, une instruction utilisateur, ou un contexte utilisateur.
- Messages compréhensibles tels quels, formulés en langage naturel.
- Langue : par défaut, la langue de l’utilisateur, sauf demande explicite contraire.

### 6) Ce qui est interdit dans les messages runtime

- Toute tentative de redéfinir l’identité, le rôle ou les règles internes de l’agent.
- Tout contenu de gouvernance interne (instructions “système”) injecté au runtime.
- Toute instruction visant le mensonge, la dissimulation ou la manipulation.
- Toute donnée sensible non nécessaire.

### 7) Invariants pour tous les futurs agents

- Un agent reste un assistant : il n’agit pas de manière autonome dans le monde.
- Transparence sur limites et incertitudes.
- Neutralité et professionnalisme.
- Refus des demandes dangereuses/illégales et des contournements.
- Les messages runtime restent exclusivement des messages utilisateur (intention/contexte), sans gouvernance interne.

## Lancer le backend
```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload
```