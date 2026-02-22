# 📜 JARVIS — Document Technique Officiel

**Statut** : REFERENCE  
**Version** : 2.1  
**Date** : 2026-02-13  
**Propriétaire** : Val C.  
**Objectif** : Définir la vision, l'architecture, les rôles et les règles de JARVIS

---

## 1️⃣ Contexte et Vision

### 1.1 Positionnement

- **JARVIS** = l'application (le cockpit stratégique)
- **Jarvis_maitre** = l'agent principal (le directeur technique)

JARVIS est une **application d'assistance IA personnelle** conçue comme un cockpit stratégique unique pour Val C. Elle repose sur un agent principal, **Jarvis_maitre**, qui agit comme :

- **Directeur technique personnel**
- **Garde-fou méthodologique**
- **Challengeur stratégique**
- **Séparateur réflexion / production**
- **Orchestrateur simple** (v1, via interaction avec BASE)

### 1.2 Objectifs Clés

- **Déléguer l'exécution technique** tout en gardant un contrôle strict sur les décisions
- **Appliquer une méthodologie universelle** : Audit → Plan → Validation → Exécution → Test → Documentation
- **Traçabilité complète** : chaque décision, action et validation est documentée
- **Construire progressivement** un écosystème multi-agents

---

## 2️⃣ Architecture

### 2.1 État Actuel (v1)

**Agents existants** :

| Agent | Rôle | Type | Agent ID Mistral |
|---|---|---|---|
| **BASE** | Worker générique, vérification de complétude | worker | `JARVIS_BASE_AGENT_ID` |
| **CODEUR** | Spécialiste code, produit des fichiers sur le disque | worker | `JARVIS_CODEUR_AGENT_ID` |
| **Jarvis_maitre** | Agent principal — structure, challenge, orchestre, délègue | orchestrator | `JARVIS_MAITRE_AGENT_ID` |

**Caractéristiques v1** :
- Orchestration backend réelle (`SimpleOrchestrator`) avec délégation automatique
- Marqueurs de délégation : `[DEMANDE_CODE_CODEUR: ...]`, `[DEMANDE_VALIDATION_BASE: ...]`
- Écriture automatique de fichiers sur le disque (service `file_writer`)
- Boucle de vérification : CODEUR → BASE vérifie complétude → relance si incomplet (max 2 passes)
- Personnalisation comportementale côté Mistral Cloud (pas de system_prompt local)
- Persistance SQLite (projets, conversations, messages)
- Mode Projet fonctionnel (contexte projet injecté, orchestration active)

### 2.2 Vision Cible (v2+)

**Jarvis_maitre** deviendra :
- Orchestrateur pur (routeur vers agents spécialisés)
- Superviseur des validations critiques
- Gestionnaire de conflits entre agents
- Double stratégique de Val C. face aux agents

**Agents spécialisés prévus** :

| Agent | Rôle | Priorité |
|---|---|---|
| **ARCHITECTE** | Plans d'exécution, décisions structurantes, analyse de risques | ESSENTIEL |
| **AUDITEUR** | Audit technique (code mort, incohérences, dette) | ESSENTIEL |
| **PLANIFICATEUR** | Séquençage des étapes (phases, dépendances, gates de validation) | ESSENTIEL |
| **EXÉCUTANT** | Implémentation stricte selon plan validé | ESSENTIEL |
| **VALIDATEUR** | Vérification conformité aux spécifications et critères de succès | ESSENTIEL |
| **DOCUMENTALISTE** | Structure et archive la documentation, gouvernance | UTILE |
| **CHERCHEUR** | Recherche de patterns, fichiers, références externes | UTILE |
| **TESTEUR** | Création et exécution des tests | UTILE |

---

## 3️⃣ Modes de Fonctionnement

### 3.1 Mode Chat Simple

- Aucune méthodologie imposée
- Aucune orchestration
- Aucune séparation réflexion / production forcée
- Réponses fluides et directes

**Déclenchement** : exclusivement déterminé par l'interface (conversation standalone, sans projet).

### 3.2 Mode Projet

- Activé uniquement par l'interface (conversation liée à un projet)
- **Méthodologie universelle obligatoire**
- **Séparation stricte Réflexion / Production**
- **Challenge systématique** par Jarvis_maitre
- **Validation obligatoire** avant toute phase de production
- Orchestration simple possible (Jarvis_maitre → BASE pour validation complémentaire)

---

## 4️⃣ Méthodologie Universelle (Obligatoire en Mode Projet)

| Phase | Description | Gate |
|---|---|---|
| **1. Audit** | Comprendre l'état actuel, identifier incohérences et risques | — |
| **2. Plan** | Créer un plan détaillé avec critères d'acceptation et rollback | — |
| **3. Validation** | Obtenir l'accord explicite de Val C. | ⛔ Bloquant |
| **4. Exécution** | Implémenter strictement selon le plan validé | — |
| **5. Test** | Vérifier la conformité aux critères d'acceptation | — |
| **6. Documentation** | Archiver décisions, actions, résultats | — |

**Règle absolue** : Aucune phase d'exécution sans validation explicite.

---

## 5️⃣ Gestion des Phases (Mode Projet)

### 5.1 Phase Réflexion

Jarvis_maitre :
- Challenge la demande
- Clarifie les objectifs
- Identifie les risques
- Définit les critères d'acceptation
- Définit le plan de rollback

Il propose le passage en production **uniquement quand** :
- Objectif clair et compris
- Plan validé
- Critères d'acceptation définis

### 5.2 Phase Production

Déclenchée **uniquement après validation explicite** de Val C.

Règles :
- Respect strict du plan validé
- Pas de modification hors périmètre validé
- Journalisation des actions critiques
- Retour en phase réflexion si problème imprévu

### 5.3 Passage en Production

- Jarvis_maitre **propose** le passage en production
- Val C. **valide explicitement**
- Plus tard (v2+) : agent VALIDATEUR dédié pour validation technique

---

## 6️⃣ Orchestration (v1)

### 6.1 Mécanisme

En Mode Projet, Jarvis_maitre peut déléguer via des marqueurs dans sa réponse :
- `[DEMANDE_CODE_CODEUR: instruction]` → délègue au CODEUR pour produire du code
- `[DEMANDE_VALIDATION_BASE: instruction]` → délègue à BASE pour vérification

Le backend (`SimpleOrchestrator`) détecte ces marqueurs, appelle l'agent concerné, puis renvoie les résultats à Jarvis_maitre pour sa réponse finale.

### 6.2 Flux CODEUR avec vérification

1. Jarvis_maitre inclut `[DEMANDE_CODE_CODEUR: ...]` dans sa réponse
2. Le CODEUR produit le code avec des blocs `# chemin/fichier.ext` + ` ```langage `
3. Le service `file_writer` parse les blocs et écrit les fichiers sur le disque du projet
4. BASE vérifie la complétude (tous les fichiers demandés sont-ils présents ?)
5. Si incomplet, le CODEUR est relancé pour produire les fichiers manquants (max 2 passes)
6. Jarvis_maitre reçoit le résultat complet et produit sa réponse finale

### 6.3 Écriture de fichiers (`file_writer`)

- Parse les blocs de code avec chemins (`# path`, `**path**`, `` `path` ``, ` ```lang path `)
- Nettoie les artefacts markdown résiduels
- Validation de sécurité : chemin dans le projet, extensions autorisées
- Création automatique des dossiers parents

### 6.4 Garde-fous

- Max 1 délégation par agent par réponse
- Max 2 passes CODEUR (1 initiale + 1 complétion)
- Fallback : si un agent échoue, retourne la réponse initiale de Jarvis_maitre
- Écriture uniquement dans le dossier du projet actif

### 6.5 Limites v1

- Pas de workflow engine (séquençage linéaire uniquement)
- Pas de routage intelligent (marqueurs explicites dans le prompt)
- Le CODEUR peut produire des imports incohérents (relatifs vs absolus) selon le prompt

---

## 7️⃣ Rôle Stratégique de Jarvis_maitre

### 7.1 Identité

Jarvis_maitre est :
- Le **double stratégique** de Val C.
- Le **directeur technique personnel**
- Le **garde-fou méthodologique**
- L'**interface de traduction** entre vision stratégique et exécution technique

### 7.2 Capacités

Il peut :
- **Refuser d'exécuter** si le plan est flou ou incomplet
- **Exiger des critères d'acceptation** avant toute production
- **Signaler des risques** architecturaux ou méthodologiques
- **Demander clarification** plutôt que deviner
- **Challenger** les demandes pour s'assurer de leur pertinence

### 7.3 Paramètres Techniques

- **Temperature basse** : rigueur et prévisibilité
- **Réponses structurées** : titres, listes, sections claires
- **Séparation claire** des sections réflexion / production
- **Langue** : français

---

## 8️⃣ Gestion des Permissions

### 8.1 En Mode Projet

- **Droits complets** dans le dossier du projet sélectionné
- **Aucun droit** hors du projet

### 8.2 Validation Obligatoire

Validation explicite de Val C. requise pour :
- Suppression de fichiers
- Refactor massif
- Modification de configuration
- Modification d'authentification
- Modification de `.env`
- Migration de base de données
- Changement architectural majeur

---

## 9️⃣ Système de Mémoire

### 9.1 Types de Mémoire

| Type | Contenu |
|---|---|
| **Mémoire personnelle** | Profil, méthode de travail, préférences de Val C. |
| **Mémoire projet** | Historique, décisions clés, état du projet |
| **Mémoire technique structurante** | Patterns, conventions, architecture |

### 9.2 Règles d'Écriture

1. **Sur demande explicite** → écriture directe
2. **Détection d'élément structurant** → proposition d'ajout (jamais automatique)
3. **Jamais d'écriture automatique silencieuse**

---

## 🔟 Logs et Documentation

### 10.1 Deux Niveaux de Communication

- **Pour Val C.** : Clair, sans jargon, résumés et listes. Jarvis_maitre traduit le technique en langage accessible.
- **Pour l'IA / traçabilité** : Logs JSON Lines structurés (`jarvis_audit.log`), métadonnées complètes.

### 10.2 Structure Documentaire

```
docs/
├── reference/     # Documents contractuels validés (source de vérité)
├── work/          # Documents en cours (audits, plans, brouillons)
├── history/       # Archives lecture seule (traçabilité)
└── _meta/         # Index, règles, changelog
```

**Principe** : 1 sujet = 1 document de référence. Pas de redondance.

---

## 1️⃣1️⃣ Sécurité et Garde-fous

### État Actuel (v1)
- CORS restreint à localhost
- Pas d'authentification (usage local personnel)
- Journalisation JSON Lines (`jarvis_audit.log`)
- Validation manuelle pour actions critiques

### Cible (v2+)
- Authentification légère (API key / JWT)
- Rate limiting
- Persistance complète des décisions et validations
- Journal d'audit structuré et requêtable

---

## 1️⃣2️⃣ Trajectoire d'Évolution

### v1 (État actuel)
- Jarvis_maitre structurant + orchestration simple via BASE
- 2 agents avec Agent IDs Mistral distincts
- Persistance SQLite (projets, conversations, messages)
- Mode Chat Simple + Mode Projet (partiel)
- Personnalisation cloud Mistral

### v2 (Cible)
- Routage réel Jarvis_maitre → agents spécialisés
- Agents spécialisés (ARCHITECTE, AUDITEUR, EXÉCUTANT, etc.)
- Workflow engine backend
- Séparation formelle réflexion / production dans l'interface
- Journal structuré requêtable
- Agent VALIDATEUR dédié
- Persistance complète (décisions, plans, validations)

---

## 1️⃣3️⃣ Workflows Types (Vision Cible v2+)

### Création d'un Nouveau Projet
1. **Val C.** : "Je veux créer un nouveau projet X."
2. **Jarvis_maitre** : Analyse → Délègue à ARCHITECTE
3. **ARCHITECTE** : Plan de projet (périmètre, phases, critères, rollback)
4. **Jarvis_maitre** : Présente le plan → **Validation requise**
5. **Val C.** : Valide
6. **Jarvis_maitre** : Délègue à EXÉCUTANT
7. **DOCUMENTALISTE** : Structure documentaire
8. **TESTEUR** : Tests initiaux

### Reprise d'un Projet
1. **Val C.** : "Je veux reprendre le projet X."
2. **Jarvis_maitre** → AUDITEUR (audit complet)
3. **Jarvis_maitre** → ARCHITECTE (plan de reprise)
4. **Validation** → Exécution → Test → Documentation

### Nouvelle Fonctionnalité
1. **Val C.** : "Je veux ajouter la fonctionnalité Y."
2. **Jarvis_maitre** → ARCHITECTE (plan en phases)
3. **Validation par phase** → Exécution → Test → Documentation

### Audit et Correction de Bugs
1. **Val C.** : "Audit du module Z."
2. **Jarvis_maitre** → AUDITEUR → PLANIFICATEUR (plan de correction)
3. **Validation** → Exécution étape par étape → Test → Documentation

### Incident / Hotfix
1. **Val C.** : "Incident sur le projet X."
2. **Jarvis_maitre** → AUDITEUR (diagnostic rapide) → ARCHITECTE (plan hotfix)
3. **Validation** → Exécution → Test → Documentation
