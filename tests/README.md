# Tests — JARVIS 2.0

**Organisation** : Structure claire par catégorie  
**Date** : 2026-02-18

---

## 📁 Structure

```
tests/
├── unit/                    # Tests unitaires (pytest)
│   ├── test_*.py           # 18 fichiers de tests unitaires
│   └── conftest.py         # Configuration pytest
├── live/                    # Tests live end-to-end
│   ├── test_live_projects.py       # Tests orchestration complète (Calculatrice, TODO, MiniBlog)
│   └── test_live_notekeeper.py     # Test incrémental NoteKeeper
└── manual/                  # Tests manuels/diagnostics
    ├── test_api_manual.py              # Tests API manuels
    ├── test_backend_simple.py          # Tests backend simples
    ├── test_codeur_direct.py           # Test direct agent CODEUR
    ├── test_config_mistral.py          # Vérification config Mistral
    ├── test_orchestration_direct.py    # Test orchestration direct
    ├── test_orchestration_live.py      # Test orchestration live
    ├── test_orchestration_minimal.py   # Test orchestration minimal
    └── test_orchestration_simple.py    # Test orchestration simple
```

---

## ✅ Tests Unitaires (`tests/unit/`)

**Commande** : `pytest tests/`

**Fichiers** (18) :
- `test_base_agent.py` — Tests agent de base
- `test_jarvis_maitre.py` — Tests agent JARVIS_Maître
- `test_agent_factory.py` — Tests factory agents
- `test_mistral_client.py` — Tests client Mistral
- `test_database.py` — Tests couche base de données
- `test_file_writer.py` — Tests écriture fichiers
- `test_orchestration.py` — Tests orchestration
- `test_project_context.py` — Tests contexte projet
- `test_language_detector.py` — Tests détection langage
- `test_session_state.py` — Tests gestion état session
- `test_api_*.py` — Tests endpoints API
- Et autres...

**Statut** : **193/193 tests passent** ✅

**Couverture** : ~74%

---

## 🚀 Tests Live (`tests/live/`)

Tests end-to-end complets avec génération de code réelle.

### `test_live_projects.py`

**Description** : Tests orchestration complète sur 3 projets de complexité croissante.

**Projets testés** :
1. **Calculatrice CLI** (niveau 1) — 4 fichiers attendus
2. **Gestionnaire TODO** (niveau 2) — 6+ fichiers attendus
3. **API REST Mini-Blog** (niveau 3) — 6+ fichiers attendus

**Validation** :
- ✅ Fichiers créés sur disque
- ✅ Structure projet respectée (src/, tests/)
- ✅ Contenu fichiers (imports, classes, fonctions)
- ✅ Pas d'artefacts markdown
- ✅ Exécution tests pytest sur code généré

**Commande** :
```bash
python tests/live/test_live_projects.py
```

**Résultats dernière exécution (18/02/2026)** :
- Calculatrice : ✅ 4 fichiers, 4/4 tests passent
- TODO : ⚠️ 8 fichiers créés, tests échouent (bug qualité code CODEUR)
- MiniBlog : ⚠️ 5 fichiers créés, tests échouent (bug qualité code CODEUR)

### `test_live_notekeeper.py`

**Description** : Test incrémental sur 5 étapes (NoteKeeper).

**Commande** :
```bash
python tests/live/test_live_notekeeper.py
```

---

## 🔧 Tests Manuels (`tests/manual/`)

Tests de diagnostic et vérification manuelle. Ne sont pas exécutés par pytest.

### Tests API
- `test_api_manual.py` — Tests manuels endpoints API

### Tests Backend
- `test_backend_simple.py` — Tests simples backend

### Tests Agents
- `test_codeur_direct.py` — Test direct agent CODEUR (diagnostic format sortie)
- `test_config_mistral.py` — Vérification configuration Mistral

### Tests Orchestration
- `test_orchestration_direct.py` — Test orchestration direct
- `test_orchestration_live.py` — Test orchestration live
- `test_orchestration_minimal.py` — Test orchestration minimal (hello.py)
- `test_orchestration_simple.py` — Test orchestration simple

**Usage** : Exécuter individuellement selon besoin
```bash
python tests/manual/test_codeur_direct.py
```

---

## 📊 Exécution Tests

### Tests unitaires (rapide)
```bash
pytest tests/
```

### Tests unitaires avec couverture
```bash
pytest tests/ --cov=backend --cov-report=html
```

### Tests live (lent, ~5-10 min)
```bash
python tests/live/test_live_projects.py
```

### Test spécifique
```bash
pytest tests/test_orchestration.py -v
```

---

## 🎯 Statut Actuel

**Tests unitaires** : ✅ 193/193 passent (100%)  
**Tests live** : ⚠️ 1/3 succès complet (Calculatrice)  
**Couverture** : ~74%

**Problèmes connus** :
- Qualité code CODEUR sur projets complexes (TODO, MiniBlog)
- Format sortie CODEUR parfois incorrect (réponses courtes)

**Recommandations** :
- Projets simples : Utiliser JARVIS (Calculatrice fonctionne parfaitement)
- Projets complexes : Vérifier code généré manuellement

---

## 📝 Notes

- Tests unitaires dans `tests/` sont découverts automatiquement par pytest
- Tests live dans `tests/live/` doivent être exécutés manuellement
- Tests manual dans `tests/manual/` sont pour diagnostic uniquement
- Configuration pytest : `pyproject.toml` (racine)
