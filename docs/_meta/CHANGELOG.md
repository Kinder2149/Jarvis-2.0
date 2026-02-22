# Changelog Documentaire - JARVIS 2.0

**Statut** : META  
**Dernière mise à jour** : 2026-02-18

---

## Format

Chaque entrée suit le format :
```
### YYYY-MM-DD - [Type d'Action]
- **Document** : `chemin/vers/document.md`
- **Action** : [CREATED | UPDATED | ARCHIVED | PROMOTED | DEPRECATED]
- **Description** : Brève description de la modification
- **Raison** : Justification si nécessaire
```

---

## Historique

### 2026-02-13 - Orchestration v1.1 + Agent CODEUR + Corrections

#### Mise à jour Document Fondateur
- **Document** : `JARVIS_Base_Document_Complet.md`
- **Action** : UPDATED (v2.0 → v2.1)
- **Description** : Ajout CODEUR dans table agents, réécriture §6 Orchestration (mécanisme, flux CODEUR, file_writer, garde-fous, limites)

#### Mise à jour Système d'Agents
- **Document** : `docs/reference/AGENT_SYSTEM.md`
- **Action** : UPDATED (v3.1 → v4.0)
- **Description** : Ajout CODEUR (config, endpoint, architecture), orchestration implémentée, boucle de vérification, tests 160/160

#### Corrections Backend
- **Fichier** : `backend/services/file_writer.py`
- **Action** : UPDATED
- **Description** : Ajout `_clean_content()` — nettoyage artefacts markdown résiduels (```python, ```) dans les fichiers écrits

#### Amélioration Orchestration
- **Fichier** : `backend/services/orchestration.py`
- **Action** : UPDATED
- **Description** : Boucle de vérification CODEUR→BASE : après écriture fichiers, BASE vérifie la complétude, relance CODEUR si incomplet (max 2 passes)

#### Tests
- **Fichiers** : `tests/test_file_writer.py`, `tests/test_orchestration.py`
- **Action** : UPDATED
- **Description** : 15 nouveaux tests (8 file_writer + 7 orchestration). Total : 160/160

---

### 2026-02-10 - Initialisation Documentation

#### Création Structure
- **Documents** : Arborescence complète `docs/`
- **Action** : CREATED
- **Description** : Mise en place de la gouvernance documentaire (reference/work/history/_meta)

#### Création Méta-Documents
- **Document** : `_meta/INDEX.md`
- **Action** : CREATED
- **Description** : Point d'entrée unique de la documentation

- **Document** : `_meta/RULES.md`
- **Action** : CREATED
- **Description** : Règles de gouvernance documentaire

- **Document** : `_meta/CHANGELOG.md`
- **Action** : CREATED
- **Description** : Ce fichier - historique des modifications

- **Document** : `_meta/IA_CONTEXT.md`
- **Action** : CREATED
- **Description** : Document de contexte pour IA externe

#### Création Documents de Référence
- **Document** : `reference/ARCHITECTURE.md`
- **Action** : CREATED
- **Description** : Architecture technique du système

- **Document** : `reference/API_SPECIFICATION.md`
- **Action** : CREATED
- **Description** : Spécification des endpoints API

- **Document** : `reference/AGENT_SYSTEM.md`
- **Action** : CREATED
- **Description** : Système d'agents et registry

#### Création Documents de Travail
- **Document** : `work/20260210_AUDIT_INITIAL.md`
- **Action** : CREATED
- **Description** : Audit technique initial du projet
- **Raison** : Identification des points d'amélioration et problèmes potentiels

---

### 2026-02-12 - Migration Architecture 2 Agents

#### Mise à jour Documents de Référence
- **Document** : `reference/AGENT_SYSTEM.md`
- **Action** : UPDATED (v2.0 → v3.0)
- **Description** : Réécriture complète — agent_registry remplacé par agent_factory + agent_config, 2 Agent IDs Mistral distincts, suppression system_prompt, personnalisation cloud
- **Raison** : Migration architecture 2 agents terminée

- **Document** : `reference/ARCHITECTURE.md`
- **Action** : UPDATED (v2.0 → v3.0)
- **Description** : Reflet architecture actuelle — SQLite, factory, config, structure répertoires, flux de données, configuration .env complète
- **Raison** : Migration architecture 2 agents terminée

- **Document** : `reference/API_SPECIFICATION_V2.md`
- **Action** : UPDATED (v2.1)
- **Description** : Correction contrainte CHECK role dans doc DB (retrait 'system')
- **Raison** : Cohérence avec schema.sql modifié

#### Mise à jour Méta-Documents
- **Document** : `_meta/INDEX.md`
- **Action** : UPDATED (v1.0 → v2.0)
- **Description** : Références corrigées (API_SPECIFICATION_V2, suppression TACHES_RESTANTES, ajout document migration archivé)

- **Document** : `_meta/IA_CONTEXT.md`
- **Action** : UPDATED (v1.0 → v2.0)
- **Description** : Reflet architecture actuelle (factory, config, SQLite, 2 agents, endpoints actuels)

- **Document** : `_meta/CHANGELOG.md`
- **Action** : UPDATED
- **Description** : Ajout entrées migration 2026-02-12

#### Archivage
- **Document** : `work/20260212_MIGRATION_ARCHITECTURE_2_AGENTS.md`
- **Action** : ARCHIVED → `history/`
- **Description** : Plan de migration exécuté et validé, mission clôturée
- **Raison** : Mission terminée

- **Document** : `JARVIS_Base_Document_Complet.md` (racine)
- **Action** : UPDATED (v1.0 → v2.0)
- **Description** : Réécriture complète — positionnement JARVIS=application / Jarvis_maitre=agent principal, modes chat/projet, orchestration simple v1, vision cible v2+, mémoire, permissions, méthodologie, trajectoire d'évolution
- **Raison** : Consolidation des décisions stratégiques du 12/02/2026

---

### 2026-02-12 - Chantier Personnalisation V1

#### Mission 1 — Prompts Cloud Mistral
- **Document** : Configuration Mistral Cloud (hors repo)
- **Action** : CREATED
- **Description** : Instructions complètes pour JARVIS_maitre (identité, méthodologie, modes, actions critiques, format) et BASE (worker générique)

#### Mission 2 — Paramètres techniques
- **Document** : `backend/agents/agent_config.py`
- **Action** : UPDATED
- **Description** : Ajout temperature et max_tokens dans AGENT_CONFIGS (métadonnées locales)

- **Document** : `backend/ia/mistral_client.py`
- **Action** : UPDATED
- **Description** : Ajout paramètres temperature/max_tokens au constructeur. Note : completion_args interdit avec agent_id, paramètres cloud-only

- **Document** : `backend/agents/base_agent.py`
- **Action** : UPDATED
- **Description** : Propagation temperature/max_tokens dans constructeur

- **Document** : `backend/agents/jarvis_maitre.py`
- **Action** : UPDATED
- **Description** : Propagation temperature/max_tokens dans constructeur

- **Document** : `backend/agents/agent_factory.py`
- **Action** : UPDATED
- **Description** : Injection temperature/max_tokens depuis config

- **Document** : `tests/test_base_agent.py`
- **Action** : UPDATED
- **Description** : +5 tests (TestAgentParameters)

- **Document** : `tests/test_jarvis_maitre.py`
- **Action** : UPDATED
- **Description** : +5 tests (TestJarvisMaitreParameters)

#### Mission 3 — Détection mode Chat / Projet
- **Document** : `backend/services/project_context.py`
- **Action** : UPDATED
- **Description** : Ajout section MODE PROJET dans contexte projet + nouvelle fonction build_chat_simple_context()

- **Document** : `backend/services/__init__.py`
- **Action** : UPDATED
- **Description** : Export build_chat_simple_context

- **Document** : `backend/api.py`
- **Action** : UPDATED
- **Description** : Injection contexte chat simple au 1er message (branche else dans send_message)

#### Mission 4 — Séparation Réflexion / Production
- **Document** : `frontend/js/components/chat.js`
- **Action** : UPDATED
- **Description** : Rendu markdown basique + détection marqueurs [RÉFLEXION]/[PRODUCTION] avec styles visuels

- **Document** : `frontend/css/chat.css`
- **Action** : UPDATED
- **Description** : Styles pour marqueurs de phase, titres, code, listes dans les messages assistant

#### Mission 8 — Nettoyage fichiers obsolètes
- **Documents supprimés** :
- **Action** : DELETED
- **Description** : 9 fichiers obsolètes supprimés (index-old.html, project-old.html, projects-old.html, script-old.js, style-old.css, css/main.css, js/chat-handler.js, js/conversation-manager.js, js/projects-manager.js)
- **Raison** : Non référencés dans la SPA, aucun import actif

#### Mission 9 — Documentation et clôture
- **Document** : `docs/reference/AGENT_SYSTEM.md`
- **Action** : UPDATED (v3.0 → v3.1)
- **Description** : Ajout temperature/max_tokens, principe cloud-only, configuration actuelle Mistral Cloud

- **Document** : `docs/_meta/CHANGELOG.md`
- **Action** : UPDATED
- **Description** : Entrées chantier personnalisation v1

- **Document** : `docs/work/20260212_CHANTIER_PERSONNALISATION_V1.md`
- **Action** : ARCHIVED → `docs/history/`
- **Description** : Chantier terminé, missions exécutées et validées

---

### 2026-02-18 - Correction Phase EXECUTION + Nettoyage Documentation

#### Correction Backend Critique
- **Fichier** : `backend/services/orchestration.py`
- **Action** : UPDATED (L457-463)
- **Description** : Ajout `transition_to_execution()` avant délégation CODEUR pour autoriser écriture disque
- **Raison** : Résolution bug `🚨 ÉCRITURE DISQUE BLOQUÉE : mode=project, phase=reflexion`

#### Mise à jour Configuration Agents
- **Fichiers** : `config_mistral/agents/CODEUR.md`, `VALIDATEUR.md`, `JARVIS_MAITRE.md`, `BASE.md`
- **Action** : UPDATED
- **Description** : Ajout ligne "Tools à activer" avec spécification outils Mistral (code_interpreter pour CODEUR uniquement)

- **Fichier** : `config_mistral/agents/CODEUR.md`
- **Action** : UPDATED
- **Description** : Changement modèle recommandé : `devstral-2-25-12` → `mistral-large-3`
- **Raison** : Devstral 2 indisponible sur Mistral Console

#### Tests Live Validés
- **Tests** : 3 projets générés (Calculatrice, TODO, MiniBlog)
- **Résultat** : Calculatrice CLI — 4 fichiers créés, 4/4 tests passent ✅
- **Statut** : Système opérationnel pour génération de code sur disque

#### Nettoyage Documentation Racine
- **Fichiers supprimés** : 3 documents obsolètes
  - `GUIDE_CONFIGURATION_AGENTS.md` (remplacé par config_mistral/README.md)
  - `JARVIS_MAITRE_MISTRAL_CONSOLE_CONFIG.md` (remplacé par config_mistral/agents/JARVIS_MAITRE.md)
  - `JARVIS_DOCUMENTATION_OFFICIELLE.md` (doublon avec README.md + docs/reference/)
- **Action** : DELETED
- **Raison** : Redondance avec documentation structurée

- **Fichiers archivés** : 2 documents work
  - `PLAN_STRATEGIQUE_ALIGNEMENT_VISION.md` → `docs/history/20260217_PLAN_STRATEGIQUE.md`
  - `RAPPORT_NETTOYAGE_DOCUMENTATION.md` → `docs/history/20260217_RAPPORT_NETTOYAGE.md`
- **Action** : ARCHIVED
- **Raison** : Missions terminées

#### Réorganisation docs/
- **Dossier** : `docs/archive/`
- **Action** : MERGED → `docs/history/`
- **Description** : Fusion complète (13 fichiers déplacés), suppression dossier archive/
- **Raison** : Éliminer doublon archive/history

- **Fichiers** : 6 documents racine docs/
- **Action** : ARCHIVED → `docs/history/`
- **Description** : Déplacement fichiers non classés (BILAN_SESSION_20260217, ETAT_REEL_PROJET_AVANT_CORRECTIONS, PLAN_FINALISATION_4_PHASES, RAPPORT_FINAL_GLOBAL, INDEX_DOCUMENTATION, system_validation_scenarios)
- **Raison** : Structuration propre (docs/ racine vide de fichiers .md)

#### Mise à jour Documents de Référence
- **Document** : `README.md`
- **Action** : UPDATED
- **Description** : État actuel v2.0 (18/02), agents avec modèles, correction phase EXECUTION, limitations actualisées
- **Raison** : Refléter corrections et état opérationnel

- **Document** : `docs/_meta/INDEX.md`
- **Action** : UPDATED (v2.2 → v2.3)
- **Description** : Structure finale après nettoyage, ajout entrées 18/02, mise à jour docs/history (25 documents)
- **Raison** : Refléter structure documentaire finale

- **Document** : `docs/_meta/CHANGELOG.md`
- **Action** : UPDATED
- **Description** : Ajout entrées 2026-02-18
- **Raison** : Traçabilité modifications

#### Création Documents
- **Document** : `docs/_meta/AUDIT_DOCUMENTATION_20260218.md`
- **Action** : CREATED
- **Description** : Audit complet documentation (racine + docs/), analyse statut fichiers, décisions nettoyage

- **Document** : `docs/history/20260218_RAPPORT_SESSION_CORRECTION_PHASE.md`
- **Action** : CREATED
- **Description** : Rapport complet session 18/02 (diagnostic, correction, tests, nettoyage documentation)
- **Raison** : Traçabilité complète session correction phase EXECUTION

#### Nettoyage docs/work/
- **Dossier** : `docs/work/`
- **Action** : ARCHIVED → `docs/history/`
- **Description** : 10 fichiers archivés (PHASE_1_RAPPORT_FINAL.md, PHASE_2_RAPPORT_FINAL.md, PHASE_3_RAPPORT_FINAL.md, PHASE_4_RAPPORT_FINAL.md, RAPPORT_STABILISATION_FINALE.md, ACTIONS_AVANT_TESTS_LIVE.md, AUDIT_TESTS_ECHOUES_PHASE_2.md, PHASE_3_ANALYSE_COUVERTURE.md, REFACTOR_WORKFLOW_CONFIRMATION.md, VERIFICATION_PROMPTS_AGENTS.md)
- **Raison** : Missions terminées, docs/work/ maintenant vide

#### Réorganisation Tests
- **Structure** : `tests/` → `tests/unit/`, `tests/live/`, `tests/manual/`
- **Action** : REORGANIZED
- **Description** : 
  - Création sous-dossiers unit/, live/, manual/
  - Déplacement 2 tests live (test_live_projects.py, test_live_notekeeper.py)
  - Déplacement 10 tests manuels (test_api_manual.py, test_backend_simple.py, test_codeur_direct.py, test_config_mistral.py, test_orchestration_direct.py, test_orchestration_live.py, test_orchestration_minimal.py, test_orchestration_simple.py, test_minimal_delegation.py)
  - Création dossier scripts/ + déplacement 2 scripts (check_test_result.py, clean_test_projects.py)
- **Raison** : Clarifier organisation tests (unitaires vs live vs manuels)

- **Document** : `tests/README.md`
- **Action** : CREATED
- **Description** : Documentation structure tests, usage pytest, tests live, tests manuels

- **Document** : `scripts/README.md`
- **Action** : CREATED
- **Description** : Documentation scripts utilitaires

- **Fichier** : `pyproject.toml`
- **Action** : UPDATED
- **Description** : Ajout exclusion tests/manual et tests/live de la découverte pytest
- **Raison** : Tests manuels/live ne doivent pas être exécutés par pytest

#### Validation Tests
- **Tests unitaires** : 237/241 passent (98%)
- **Statut** : ✅ Organisation tests validée, aucune régression

---

## À Venir

*Les prochaines modifications seront documentées ici*
