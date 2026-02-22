/**
 * Library View - JARVIS 2.0
 * Page Librairie — Knowledge Base pour les agents et l'utilisateur
 * Affiche les documents organisés par catégorie avec prévisualisation
 */

import { createElement, clearContainer } from '../utils/dom.js';

const API_BASE = 'http://localhost:8000';

/**
 * Structure de la librairie
 * Chaque catégorie contient des items avec nom, description, tags, contenu
 */
const LIBRARY_CATEGORIES = [
    {
        id: 'libraries',
        name: 'Librairies & Frameworks',
        icon: '\uD83D\uDCDA',
        cssClass: 'libraries',
        description: 'Documentation de référence des librairies Python, Flutter, JS, etc.',
        items: [
            {
                id: 'python-fastapi',
                name: 'FastAPI',
                icon: '\u26A1',
                description: 'Framework web Python async — routes, modèles Pydantic, middleware',
                tags: ['python', 'web', 'api'],
                agents: ['CODEUR', 'BASE'],
                content: `# FastAPI — Référence rapide

## Installation
pip install fastapi uvicorn

## App de base
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    description: str | None = None

@app.get("/")
async def root():
    return {"message": "Hello"}

@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    return item

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in db:
        raise HTTPException(status_code=404, detail="Not found")
    return db[item_id]

## Middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

## Query params
@app.get("/items/")
async def list_items(skip: int = 0, limit: int = 10, search: str = None):
    ...

## Fichiers statiques
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="static"), name="static")

## Tests
from fastapi.testclient import TestClient
client = TestClient(app)
response = client.get("/")
assert response.status_code == 200`
            },
            {
                id: 'python-pytest',
                name: 'Pytest',
                icon: '\uD83E\uDDEA',
                description: 'Framework de tests Python — fixtures, parametrize, tmp_path',
                tags: ['python', 'testing'],
                agents: ['CODEUR', 'BASE'],
                content: `# Pytest — Référence rapide

## Installation
pip install pytest

## Test basique
def test_addition():
    assert 1 + 1 == 2

def test_exception():
    import pytest
    with pytest.raises(ValueError):
        int("not_a_number")

## Fixtures
import pytest

@pytest.fixture
def sample_data():
    return {"key": "value"}

def test_with_fixture(sample_data):
    assert sample_data["key"] == "value"

## tmp_path (fichiers temporaires)
def test_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello")
    assert f.read_text() == "hello"

## Parametrize
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_double(input, expected):
    assert input * 2 == expected

## Lancer
pytest tests/ -v --tb=short`
            },
            {
                id: 'python-pydantic',
                name: 'Pydantic',
                icon: '\uD83D\uDCCB',
                description: 'Validation de données Python — BaseModel, Field, validators',
                tags: ['python', 'validation'],
                agents: ['CODEUR'],
                content: `# Pydantic v2 — Référence rapide

## Modèle de base
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str = Field(min_length=1, max_length=100)
    email: str
    age: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.now)

## Utilisation
user = User(id=1, name="Val", email="val@test.com")
user_dict = user.model_dump()
user_json = user.model_dump_json()

## Depuis dict
user = User.model_validate({"id": 1, "name": "Val", "email": "val@test.com"})

## Modèle avec champs optionnels (pour update)
class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None

## Validators
from pydantic import field_validator

class Product(BaseModel):
    price: float

    @field_validator('price')
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v`
            },
            {
                id: 'python-aiosqlite',
                name: 'aiosqlite',
                icon: '\uD83D\uDDC3\uFE0F',
                description: 'SQLite async pour Python — requêtes, transactions',
                tags: ['python', 'database', 'async'],
                agents: ['CODEUR'],
                content: `# aiosqlite — Référence rapide

## Installation
pip install aiosqlite

## Connexion et requêtes
import aiosqlite

async def example():
    async with aiosqlite.connect("data.db") as db:
        db.row_factory = aiosqlite.Row

        # Créer table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        """)
        await db.commit()

        # Insert
        await db.execute(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            ("Val", "val@test.com")
        )
        await db.commit()

        # Select
        async with db.execute("SELECT * FROM users WHERE id = ?", (1,)) as cursor:
            row = await cursor.fetchone()
            if row:
                print(dict(row))

        # Select all
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]`
            },
            {
                id: 'flutter-base',
                name: 'Flutter',
                icon: '\uD83D\uDC26',
                description: 'Framework mobile/web — widgets, state, navigation',
                tags: ['flutter', 'dart', 'mobile'],
                agents: ['CODEUR'],
                content: `# Flutter — Référence rapide

## Nouveau projet
flutter create my_app
cd my_app
flutter run

## Widget Stateless
class MyWidget extends StatelessWidget {
  const MyWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return const Text('Hello Flutter');
  }
}

## Widget Stateful
class Counter extends StatefulWidget {
  const Counter({super.key});
  @override
  State<Counter> createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int _count = 0;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Count: \$_count'),
        ElevatedButton(
          onPressed: () => setState(() => _count++),
          child: const Text('Increment'),
        ),
      ],
    );
  }
}

## Navigation
Navigator.push(context, MaterialPageRoute(builder: (_) => NextPage()));
Navigator.pop(context);

## HTTP
import 'package:http/http.dart' as http;
final response = await http.get(Uri.parse('https://api.example.com/data'));`
            }
        ]
    },
    {
        id: 'methodologies',
        name: 'Méthodologies',
        icon: '\uD83D\uDCCB',
        cssClass: 'methodologies',
        description: 'Processus de travail, audits, plans d\'exécution',
        items: [
            {
                id: 'methodo-audit-plan',
                name: 'Audit > Plan > Exécution',
                icon: '\uD83C\uDFAF',
                description: 'Méthodologie principale JARVIS — cycle complet de travail',
                tags: ['process', 'core'],
                agents: ['JARVIS_Maitre'],
                content: `# Méthodologie : Audit > Plan > Validation > Exécution > Documentation

## 1. AUDIT
- Analyser l'existant (code, docs, architecture)
- Identifier les incohérences, la dette technique
- Lister les fichiers impactés
- Produire un rapport factuel

## 2. PLAN
- Décomposer en étapes ordonnées
- Pour chaque étape : fichiers, modifications, dépendances
- Estimer la complexité
- Identifier les risques

## 3. VALIDATION
- Présenter le plan à l'utilisateur
- Attendre validation explicite
- Ne JAMAIS exécuter sans accord

## 4. EXÉCUTION
- Suivre le plan étape par étape
- Un fichier = une modification complète
- Tester après chaque étape
- Signaler tout écart par rapport au plan

## 5. DOCUMENTATION
- Mettre à jour les docs impactées
- Archiver les docs obsolètes
- Mettre à jour le CHANGELOG
- Mettre à jour INDEX.md`
            },
            {
                id: 'methodo-doc-governance',
                name: 'Gouvernance documentaire',
                icon: '\uD83D\uDCC1',
                description: 'Règles de gestion des documents — reference/work/history',
                tags: ['process', 'documentation'],
                agents: ['JARVIS_Maitre', 'BASE'],
                content: `# Gouvernance documentaire

## Arborescence
- docs/reference/ : documents contractuels validés (source de vérité)
- docs/work/ : documents en cours (audits, analyses, brouillons)
- docs/history/ : archive lecture seule (traçabilité)
- docs/_meta/ : index, règles, templates, changelog

## Règles d'entrée/sortie
- work -> reference : doc complet + revue + versioning + MAJ index
- reference -> history : ancienne version, avec indication du remplaçant
- work -> history : mission terminée ou doc périmé
- history : pas de modification

## Conventions
- reference : NOM_SPECIFICATION.md
- work : YYYYMMDD_NOM.md
- history : conserver nom original

## Principe clé
1 sujet = 1 document de référence (éviter redondances)`
            },
            {
                id: 'methodo-code-review',
                name: 'Revue de code',
                icon: '\uD83D\uDD0D',
                description: 'Checklist de vérification du code produit par les agents',
                tags: ['process', 'quality'],
                agents: ['BASE'],
                content: `# Checklist revue de code

## Structure
- [ ] Fichiers complets et autonomes
- [ ] Imports absolus simples (pas de relatifs)
- [ ] Pas d'artefacts markdown dans le code
- [ ] Newline en fin de fichier

## Qualité
- [ ] Pas de code mort
- [ ] Gestion des erreurs (try/except, if/else)
- [ ] Types cohérents
- [ ] Nommage clair et cohérent

## Tests
- [ ] Tests présents pour chaque module
- [ ] Cas nominaux couverts
- [ ] Cas d'erreur couverts
- [ ] Fixtures utilisées (pas de données en dur)

## Complétude
- [ ] Tous les fichiers demandés sont présents
- [ ] requirements.txt à jour
- [ ] Aucun TODO ou placeholder`
            }
        ]
    },
    {
        id: 'prompts',
        name: 'Prompts & Templates',
        icon: '\uD83D\uDCAC',
        cssClass: 'prompts',
        description: 'Prompts récurrents pour les tâches courantes et la communication inter-agents',
        items: [
            {
                id: 'prompt-delegation-codeur',
                name: 'Délégation au CODEUR',
                icon: '\u27A1\uFE0F',
                description: 'Template de marqueur pour déléguer du code au CODEUR',
                tags: ['inter-agent', 'delegation'],
                agents: ['JARVIS_Maitre'],
                content: `# Template : Délégation au CODEUR

## Format du marqueur
[DEMANDE_CODE_CODEUR: <instruction complète>]

## Règles
- L'instruction doit être COMPLÈTE et AUTONOME
- Lister TOUS les fichiers à produire avec leur chemin
- Préciser le format de chaque fichier (classe, fonctions, etc.)
- Préciser les imports et dépendances
- Max 1 marqueur CODEUR par réponse

## Exemple
[DEMANDE_CODE_CODEUR: Crée les fichiers suivants :
- src/models.py : classe User avec id (int), name (str), email (str), méthodes to_dict() et from_dict()
- src/storage.py : classe JsonStorage avec load() et save(data)
- tests/test_models.py : tests pytest pour User
- requirements.txt : pytest
Imports absolus simples, fichiers complets.]`
            },
            {
                id: 'prompt-verification-base',
                name: 'Vérification par BASE',
                icon: '\u2705',
                description: 'Template pour demander une vérification de complétude à BASE',
                tags: ['inter-agent', 'verification'],
                agents: ['JARVIS_Maitre'],
                content: `# Template : Vérification par BASE

## Format du marqueur
[DEMANDE_VALIDATION_BASE: <instruction de vérification>]

## Réponse attendue de BASE
- COMPLET : tous les fichiers sont présents et conformes
- INCOMPLET: liste des fichiers manquants ou problèmes

## Exemple
[DEMANDE_VALIDATION_BASE: Vérifie que le code produit contient bien :
- src/models.py avec classe User
- src/storage.py avec classe JsonStorage
- tests/test_models.py avec au moins 3 tests
- requirements.txt]`
            },
            {
                id: 'prompt-new-project',
                name: 'Création de projet',
                icon: '\uD83C\uDD95',
                description: 'Template de prompt pour demander la création d\'un nouveau projet',
                tags: ['user', 'project'],
                agents: ['JARVIS_Maitre'],
                content: `# Template : Demande de création de projet

## Structure du prompt
Crée un projet [NOM] en [LANGAGE] avec :
- [fichier 1] : [description précise des classes/fonctions]
- [fichier 2] : [description précise]
- tests/[test_fichier].py : tests pytest couvrant [cas à tester]
- requirements.txt : [dépendances]

Utilise des imports absolus simples. Chaque fichier doit être complet et autonome.

## Conseils
- Être EXPLICITE sur les noms de fichiers et chemins
- Décrire les classes ET leurs méthodes
- Préciser les cas d'erreur à gérer
- Mentionner les dépendances exactes`
            }
        ]
    },
    {
        id: 'personal',
        name: 'Données personnelles',
        icon: '\uD83D\uDC64',
        cssClass: 'personal',
        description: 'Préférences, conventions, informations spécifiques à Val C.',
        items: [
            {
                id: 'personal-conventions',
                name: 'Conventions de code',
                icon: '\uD83D\uDCDD',
                description: 'Règles de style et conventions suivies dans tous les projets',
                tags: ['style', 'rules'],
                agents: ['CODEUR', 'JARVIS_Maitre', 'BASE'],
                content: `# Conventions de code — Val C.

## Python
- Imports absolus simples (pas de from src.xxx)
- Classes en PascalCase, fonctions/variables en snake_case
- Docstrings pour les classes et fonctions publiques
- Type hints sur les signatures de fonctions
- Fichiers complets et autonomes
- Newline en fin de fichier
- Pas de commentaires inutiles

## JavaScript
- ES6 modules (import/export)
- camelCase pour variables/fonctions
- PascalCase pour classes
- const par défaut, let si nécessaire, jamais var
- Template literals pour les strings dynamiques

## Structure projet
- src/ : code source
- tests/ : tests
- docs/ : documentation
- requirements.txt ou package.json à la racine

## Tests
- pytest pour Python
- Nommage : test_[module].py
- Fixtures pour les données de test
- tmp_path pour les fichiers temporaires`
            },
            {
                id: 'personal-stack',
                name: 'Stack technique',
                icon: '\uD83D\uDEE0\uFE0F',
                description: 'Technologies utilisées et préférées',
                tags: ['tech', 'preferences'],
                agents: ['JARVIS_Maitre', 'CODEUR'],
                content: `# Stack technique — Val C.

## Backend
- Python 3.11+
- FastAPI (web framework)
- SQLite + aiosqlite (base de données)
- Pydantic v2 (validation)
- Mistral AI (LLM)

## Frontend
- HTML/CSS/JavaScript vanilla
- Pas de framework JS (pas de React/Vue/Angular)
- ES6 modules
- CSS custom properties (variables)
- Design sombre (dark theme)

## Mobile
- Flutter / Dart (en apprentissage)

## Outils
- Git
- pytest
- VS Code / Windsurf
- Windows

## Hébergement
- Local uniquement (pas de cloud)
- localhost:8000 pour le backend`
            }
        ]
    }
];

class LibraryView {
    constructor() {
        this.container = null;
        this.categories = LIBRARY_CATEGORIES;
        this.activeFilter = 'all';
    }

    /**
     * Rend la vue Librairie
     * @param {HTMLElement} container
     */
    async render(container) {
        this.container = container;
        clearContainer(container);

        const view = createElement('div', { className: 'library-view fade-in' });
        container.appendChild(view);

        this.renderContent(view);
    }

    /**
     * Rend le contenu principal
     * @param {HTMLElement} container
     */
    renderContent(container) {
        clearContainer(container);

        // Header
        container.appendChild(this.renderHeader());

        // Stats
        container.appendChild(this.renderStats());

        // Filtres
        container.appendChild(this.renderFilters());

        // Grille des catégories
        container.appendChild(this.renderGrid());
    }

    /**
     * Rend le header
     * @returns {HTMLElement}
     */
    renderHeader() {
        return createElement('div', { className: 'library-header' }, [
            createElement('h1', {}, '\uD83D\uDCDA Librairie'),
            createElement('p', {}, 'Base de connaissances pour les agents et l\'utilisateur')
        ]);
    }

    /**
     * Rend les statistiques
     * @returns {HTMLElement}
     */
    renderStats() {
        const totalItems = this.categories.reduce((sum, cat) => sum + cat.items.length, 0);
        const totalAgentTags = new Set();
        this.categories.forEach(cat => {
            cat.items.forEach(item => {
                (item.agents || []).forEach(a => totalAgentTags.add(a));
            });
        });

        return createElement('div', { className: 'library-stats' }, [
            this.createStat(String(this.categories.length), 'Catégories'),
            this.createStat(String(totalItems), 'Documents'),
            this.createStat(String(totalAgentTags.size), 'Agents liés')
        ]);
    }

    /**
     * Crée un bloc stat
     * @param {string} value
     * @param {string} label
     * @returns {HTMLElement}
     */
    createStat(value, label) {
        return createElement('div', { className: 'library-stat' }, [
            createElement('span', { className: 'library-stat-value' }, value),
            createElement('span', { className: 'library-stat-label' }, label)
        ]);
    }

    /**
     * Rend les filtres
     * @returns {HTMLElement}
     */
    renderFilters() {
        const filters = [
            { id: 'all', label: 'Tout' },
            { id: 'libraries', label: '\uD83D\uDCDA Librairies' },
            { id: 'methodologies', label: '\uD83D\uDCCB Méthodologies' },
            { id: 'prompts', label: '\uD83D\uDCAC Prompts' },
            { id: 'personal', label: '\uD83D\uDC64 Personnel' }
        ];

        const container = createElement('div', { className: 'library-filters' });

        filters.forEach(filter => {
            const btn = createElement('button', {
                className: `library-filter-btn${this.activeFilter === filter.id ? ' active' : ''}`
            }, filter.label);

            btn.addEventListener('click', () => {
                this.activeFilter = filter.id;
                const view = this.container.querySelector('.library-view');
                if (view) this.renderContent(view);
            });

            container.appendChild(btn);
        });

        return container;
    }

    /**
     * Rend la grille des catégories
     * @returns {HTMLElement}
     */
    renderGrid() {
        const grid = createElement('div', { className: 'library-grid' });

        const filtered = this.activeFilter === 'all'
            ? this.categories
            : this.categories.filter(cat => cat.id === this.activeFilter);

        filtered.forEach(category => {
            grid.appendChild(this.renderCategoryCard(category));
        });

        return grid;
    }

    /**
     * Rend une carte catégorie
     * @param {Object} category
     * @returns {HTMLElement}
     */
    renderCategoryCard(category) {
        const card = createElement('div', { className: 'library-category-card slide-in-up' });

        // Header
        card.appendChild(createElement('div', { className: 'library-category-header' }, [
            createElement('div', { className: `library-category-icon ${category.cssClass}` }, category.icon),
            createElement('div', { className: 'library-category-info' }, [
                createElement('h2', {}, category.name),
                createElement('p', {}, category.description)
            ]),
            createElement('span', { className: 'library-category-count' }, `${category.items.length}`)
        ]));

        // Body — liste des items
        const body = createElement('div', { className: 'library-category-body' });

        category.items.forEach(item => {
            body.appendChild(this.renderItem(item));
        });

        card.appendChild(body);
        return card;
    }

    /**
     * Rend un item de la librairie
     * @param {Object} item
     * @returns {HTMLElement}
     */
    renderItem(item) {
        const tagsContainer = createElement('div', { className: 'library-item-tags' });

        (item.agents || []).forEach(agent => {
            tagsContainer.appendChild(
                createElement('span', { className: 'library-item-tag agent-tag' }, agent)
            );
        });

        const el = createElement('div', { className: 'library-item' }, [
            createElement('span', { className: 'library-item-icon' }, item.icon),
            createElement('div', { className: 'library-item-info' }, [
                createElement('div', { className: 'library-item-name' }, item.name),
                createElement('div', { className: 'library-item-desc' }, item.description)
            ]),
            tagsContainer
        ]);

        el.addEventListener('click', () => this.showItemDetail(item));

        return el;
    }

    /**
     * Affiche le détail d'un item dans une modal
     * @param {Object} item
     */
    showItemDetail(item) {
        // Overlay
        const overlay = createElement('div', { className: 'library-modal-overlay' });

        // Modal
        const modal = createElement('div', { className: 'library-modal' });

        // Header
        const closeBtn = createElement('button', { className: 'library-modal-close' }, '\u00D7');
        closeBtn.addEventListener('click', () => overlay.remove());

        modal.appendChild(createElement('div', { className: 'library-modal-header' }, [
            createElement('h2', {}, [
                document.createTextNode(`${item.icon} `),
                document.createTextNode(item.name)
            ]),
            closeBtn
        ]));

        // Body
        const body = createElement('div', { className: 'library-modal-body' });

        // Meta
        const meta = createElement('div', { className: 'library-modal-meta' });

        (item.tags || []).forEach(tag => {
            meta.appendChild(createElement('span', { className: 'library-modal-meta-item' }, `#${tag}`));
        });

        (item.agents || []).forEach(agent => {
            meta.appendChild(createElement('span', { className: 'library-modal-meta-item' }, `\uD83E\uDD16 ${agent}`));
        });

        body.appendChild(meta);

        // Contenu
        const content = createElement('div', { className: 'library-modal-content' });
        content.textContent = item.content || 'Aucun contenu disponible.';
        body.appendChild(content);

        modal.appendChild(body);
        overlay.appendChild(modal);

        // Fermer en cliquant sur l'overlay
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.remove();
        });

        // Fermer avec Escape
        const escHandler = (e) => {
            if (e.key === 'Escape') {
                overlay.remove();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);

        document.body.appendChild(overlay);
    }

    /**
     * Nettoie la vue
     */
    destroy() {
        // Fermer les modals ouvertes
        const modals = document.querySelectorAll('.library-modal-overlay');
        modals.forEach(m => m.remove());

        if (this.container) {
            clearContainer(this.container);
        }
    }
}

export default LibraryView;
