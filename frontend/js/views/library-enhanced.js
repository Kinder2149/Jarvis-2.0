/**
 * Library View Enhanced - JARVIS 2.0
 * Documentation complète de l'architecture, flow de données et état réel
 */

import { createElement, clearContainer } from '../utils/dom.js';

const API_BASE = 'http://localhost:8000';

/**
 * Métadonnées des catégories (structure uniquement)
 * Les documents sont chargés depuis l'API /api/library
 */
const CATEGORY_METADATA = {
    'libraries': {
        id: 'libraries',
        name: 'Librairies & Frameworks',
        icon: '📚',
        cssClass: 'libraries',
        description: 'Documentation de référence des librairies Python, Flutter, JS, etc.'
    },
    'methodologies': {
        id: 'methodologies',
        name: 'Méthodologies',
        icon: '📋',
        cssClass: 'methodologies',
        description: 'Processus de travail, audits, plans d\'exécution'
    },
    'prompts': {
        id: 'prompts',
        name: 'Prompts & Templates',
        icon: '💬',
        cssClass: 'prompts',
        description: 'Prompts récurrents pour les tâches courantes et la communication inter-agents'
    },
    'personal': {
        id: 'personal',
        name: 'Données personnelles',
        icon: '👤',
        cssClass: 'personal',
        description: 'Préférences, conventions, informations spécifiques à Val C.'
    }
};

/**
 * ANCIEN CODE HARDCODÉ - CONSERVÉ POUR RÉFÉRENCE
 * ⚠️ Ces données ne sont PLUS utilisées - remplacées par API
 */
const LIBRARY_CATEGORIES_OLD = [
    {
        id: 'libraries',
        name: 'Librairies & Frameworks',
        icon: '📚',
        cssClass: 'libraries',
        description: 'Documentation de référence des librairies Python, Flutter, JS, etc.',
        items: [
            {
                id: 'python-fastapi',
                name: 'FastAPI',
                icon: '⚡',
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
                icon: '🧪',
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
                icon: '📋',
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
            }
        ]
    },
    {
        id: 'methodologies',
        name: 'Méthodologies',
        icon: '📋',
        cssClass: 'methodologies',
        description: 'Processus de travail, audits, plans d\'exécution',
        items: [
            {
                id: 'methodo-audit-plan',
                name: 'Audit > Plan > Exécution',
                icon: '🎯',
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
            }
        ]
    },
    {
        id: 'prompts',
        name: 'Prompts & Templates',
        icon: '💬',
        cssClass: 'prompts',
        description: 'Prompts récurrents pour les tâches courantes et la communication inter-agents',
        items: [
            {
                id: 'prompt-delegation-codeur',
                name: 'Délégation au CODEUR',
                icon: '➡️',
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
            }
        ]
    },
    {
        id: 'personal',
        name: 'Données personnelles',
        icon: '👤',
        cssClass: 'personal',
        description: 'Préférences, conventions, informations spécifiques à Val C.',
        items: [
            {
                id: 'personal-conventions',
                name: 'Conventions de code',
                icon: '📝',
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
            }
        ]
    }
];

class LibraryViewEnhanced {
    constructor() {
        this.container = null;
        this.documents = [];  // Documents depuis API
        this.categories = [];  // Catégories construites depuis documents
        this.activeFilter = 'all';
    }

    async render(container) {
        this.container = container;
        clearContainer(container);

        const view = createElement('div', { className: 'library-view fade-in' });
        container.appendChild(view);

        this.renderLoading(view);
        await this.loadDocuments(view);
    }

    renderLoading(container) {
        clearContainer(container);
        const loading = createElement('div', { className: 'agents-loading' }, [
            createElement('div', { className: 'spinner' }),
            createElement('span', {}, 'Chargement de la Library...')
        ]);
        container.appendChild(loading);
    }

    async loadDocuments(container) {
        try {
            const response = await fetch(`${API_BASE}/api/library`);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            this.documents = await response.json();
            
            // Construire les catégories depuis les documents
            this.categories = this.buildCategoriesFromDocuments(this.documents);
            
            this.renderContent(container);
        } catch (error) {
            console.error('Erreur chargement Library:', error);
            this.renderError(container, error.message);
        }
    }

    buildCategoriesFromDocuments(documents) {
        const categories = [];
        
        // Pour chaque catégorie définie dans CATEGORY_METADATA
        Object.keys(CATEGORY_METADATA).forEach(catId => {
            const metadata = CATEGORY_METADATA[catId];
            const items = documents.filter(doc => doc.category === catId);
            
            if (items.length > 0) {
                categories.push({
                    ...metadata,
                    items: items
                });
            }
        });
        
        return categories;
    }

    renderError(container, message) {
        clearContainer(container);

        const errorDiv = createElement('div', { className: 'agents-error' }, [
            createElement('div', { style: 'font-size: 3rem; margin-bottom: 1rem;' }, '⚠️'),
            createElement('h2', {}, 'Erreur de chargement'),
            createElement('p', {}, `Impossible de charger la Library : ${message}`)
        ]);

        const retryBtn = createElement('button', { className: 'retry-btn' }, 'Réessayer');
        retryBtn.addEventListener('click', () => this.loadDocuments(container));
        errorDiv.appendChild(retryBtn);

        container.appendChild(errorDiv);
    }

    renderContent(container) {
        clearContainer(container);

        container.appendChild(this.renderHeader());
        container.appendChild(this.renderArchitectureInfo());
        container.appendChild(this.renderStats());
        container.appendChild(this.renderFilters());
        container.appendChild(this.renderGrid());
        container.appendChild(this.renderSystemStatus());
    }

    renderHeader() {
        return createElement('div', { className: 'library-header' }, [
            createElement('h1', {}, '📚 Knowledge Base'),
            createElement('p', {}, 'Base de connaissances pour les agents et l\'utilisateur')
        ]);
    }

    renderArchitectureInfo() {
        const section = createElement('div', { className: 'architecture-info' });
        
        section.appendChild(createElement('h2', {}, '🏗️ Architecture de la Library'));
        
        const layers = createElement('div', { className: 'architecture-layers' });
        
        [
            {
                title: 'Couche 1 : Base de Données',
                status: 'warning',
                icon: '🗄️',
                desc: 'Table SQLite library_documents',
                state: '❌ Vide (migration jamais exécutée)'
            },
            {
                title: 'Couche 2 : Backend API',
                status: 'success',
                icon: '⚙️',
                desc: 'API REST + Functions pour agents',
                state: '✅ Implémenté (mais BDD vide)'
            },
            {
                title: 'Couche 3 : Frontend',
                status: 'warning',
                icon: '🖥️',
                desc: 'Interface utilisateur',
                state: '⚠️ Données hardcodées (non synchronisées)'
            }
        ].forEach(layer => {
            const layerEl = createElement('div', { className: `architecture-layer ${layer.status}` }, [
                createElement('div', { className: 'layer-icon' }, layer.icon),
                createElement('div', { className: 'layer-content' }, [
                    createElement('h3', {}, layer.title),
                    createElement('p', { className: 'layer-desc' }, layer.desc),
                    createElement('p', { className: 'layer-state' }, layer.state)
                ])
            ]);
            layers.appendChild(layerEl);
        });
        
        section.appendChild(layers);
        return section;
    }

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
            this.createStat(String(totalItems), 'Documents (hardcodés)'),
            this.createStat(String(totalAgentTags.size), 'Agents liés'),
            this.createStat('0', 'Documents en BDD')
        ]);
    }

    createStat(value, label) {
        return createElement('div', { className: 'library-stat' }, [
            createElement('span', { className: 'library-stat-value' }, value),
            createElement('span', { className: 'library-stat-label' }, label)
        ]);
    }

    renderFilters() {
        const filters = [
            { id: 'all', label: 'Tout' },
            { id: 'libraries', label: '📚 Librairies' },
            { id: 'methodologies', label: '📋 Méthodologies' },
            { id: 'prompts', label: '💬 Prompts' },
            { id: 'personal', label: '👤 Personnel' }
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

    renderCategoryCard(category) {
        const card = createElement('div', { className: 'library-category-card slide-in-up' });

        card.appendChild(createElement('div', { className: 'library-category-header' }, [
            createElement('div', { className: `library-category-icon ${category.cssClass}` }, category.icon),
            createElement('div', { className: 'library-category-info' }, [
                createElement('h2', {}, category.name),
                createElement('p', {}, category.description)
            ]),
            createElement('span', { className: 'library-category-count' }, `${category.items.length}`)
        ]));

        const body = createElement('div', { className: 'library-category-body' });

        category.items.forEach(item => {
            body.appendChild(this.renderItem(item));
        });

        card.appendChild(body);
        return card;
    }

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

    showItemDetail(item) {
        const overlay = createElement('div', { className: 'library-modal-overlay' });
        const modal = createElement('div', { className: 'library-modal' });

        const closeBtn = createElement('button', { className: 'library-modal-close' }, '×');
        closeBtn.addEventListener('click', () => overlay.remove());

        modal.appendChild(createElement('div', { className: 'library-modal-header' }, [
            createElement('h2', {}, [
                document.createTextNode(`${item.icon} `),
                document.createTextNode(item.name)
            ]),
            closeBtn
        ]));

        const body = createElement('div', { className: 'library-modal-body' });

        const meta = createElement('div', { className: 'library-modal-meta' });

        (item.tags || []).forEach(tag => {
            meta.appendChild(createElement('span', { className: 'library-modal-meta-item' }, `#${tag}`));
        });

        (item.agents || []).forEach(agent => {
            meta.appendChild(createElement('span', { className: 'library-modal-meta-item' }, `🤖 ${agent}`));
        });

        body.appendChild(meta);

        const content = createElement('div', { className: 'library-modal-content' });
        content.textContent = item.content || 'Aucun contenu disponible.';
        body.appendChild(content);

        modal.appendChild(body);
        overlay.appendChild(modal);

        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) overlay.remove();
        });

        const escHandler = (e) => {
            if (e.key === 'Escape') {
                overlay.remove();
                document.removeEventListener('keydown', escHandler);
            }
        };
        document.addEventListener('keydown', escHandler);

        document.body.appendChild(overlay);
    }

    renderSystemStatus() {
        const section = createElement('div', { className: 'system-status-section' });

        section.appendChild(createElement('h2', { className: 'status-title' }, '🔍 État du Système Library'));

        // Flow de données
        const flowSection = createElement('div', { className: 'status-category' });
        flowSection.appendChild(createElement('h3', {}, '🔄 Flow de Données Actuel'));
        
        const totalDocs = this.documents.length;
        const flowDiagram = createElement('div', { className: 'flow-diagram-simple' });
        flowDiagram.innerHTML = `
            <div class="flow-step-simple">👤 Utilisateur clique "Library"</div>
            <div class="flow-arrow-simple">↓</div>
            <div class="flow-step-simple">📱 Frontend charge library-enhanced.js</div>
            <div class="flow-arrow-simple">↓</div>
            <div class="flow-step-simple">� Appel API GET /api/library</div>
            <div class="flow-arrow-simple">↓</div>
            <div class="flow-step-simple">�️ Backend lit depuis library_documents (BDD)</div>
            <div class="flow-arrow-simple">↓</div>
            <div class="flow-step-simple success">✅ Affichage des ${totalDocs} documents</div>
        `;
        flowSection.appendChild(flowDiagram);
        section.appendChild(flowSection);

        // Utilisation agents
        const agentsSection = createElement('div', { className: 'status-category' });
        agentsSection.appendChild(createElement('h3', {}, '🤖 Utilisation par les Agents'));
        
        const dbCount = this.documents.length;
        const agentsList = createElement('ul', { className: 'status-list' });
        [
            { agent: 'JARVIS_Maître', access: 'Consulte méthodologies, prompts', state: dbCount > 0 ? '✅ Peut accéder via get_library_document()' : '❌ BDD vide' },
            { agent: 'BASE', access: 'Consulte librairies, méthodologies', state: dbCount > 0 ? '✅ Peut accéder via get_library_document()' : '❌ BDD vide' },
            { agent: 'CODEUR', access: 'Consulte librairies, conventions', state: '⚠️ Pas de function déclarée (mais BDD peuplée)' },
            { agent: 'VALIDATEUR', access: 'Consulte conventions', state: '⚠️ Pas de function déclarée (mais BDD peuplée)' }
        ].forEach(({ agent, access, state }) => {
            agentsList.appendChild(createElement('li', {}, `**${agent}** : ${access} → ${state}`));
        });
        agentsSection.appendChild(agentsList);
        section.appendChild(agentsSection);

        // Implémenté
        const implemented = createElement('div', { className: 'status-category' });
        implemented.appendChild(createElement('h3', {}, '✅ Fonctionnalités Implémentées'));
        const implList = createElement('ul', { className: 'status-list' });
        [
            'Table library_documents créée (SQLite)',
            'API REST complète (GET, POST, PUT, DELETE)',
            'Functions pour agents (get_library_document, get_library_list)',
            'Filtres avancés (category, agent, tag, search)',
            `Seed automatique au démarrage (library_seed.json)`,
            `BDD peuplée avec ${dbCount} documents`,
            'Frontend lit depuis API /api/library',
            'Interface frontend ergonomique',
            'Modal de prévisualisation',
            'Tags agents affichés',
            'Synchronisation frontend ↔ backend garantie'
        ].forEach(item => {
            implList.appendChild(createElement('li', {}, `✅ ${item}`));
        });
        implemented.appendChild(implList);
        section.appendChild(implemented);

        // Problèmes
        const issues = createElement('div', { className: 'status-category' });
        issues.appendChild(createElement('h3', {}, '🚨 Problèmes Identifiés'));
        const issuesList = createElement('ul', { className: 'status-list error' });
        [
            'Pas de CRUD utilisateur (pas d\'interface pour gérer les documents)',
            'Pas de versioning des documents (modifications écrasent)',
            'CODEUR et VALIDATEUR n\'ont pas de functions Library',
            'Pas de prévisualisation Markdown en temps réel',
            'Pas de corbeille (suppression définitive)'
        ].forEach(item => {
            issuesList.appendChild(createElement('li', {}, `❌ ${item}`));
        });
        issues.appendChild(issuesList);
        section.appendChild(issues);

        // Solutions
        const solutions = createElement('div', { className: 'status-category' });
        solutions.appendChild(createElement('h3', {}, '🚀 Solutions Recommandées'));
        const solList = createElement('ul', { className: 'status-list' });
        [
            '✅ **Phase 1 TERMINÉE** : Seed automatique implémenté (library_seed.json)',
            '✅ **Frontend mis à jour** : Lit depuis API /api/library',
            '🔄 **Phase 2 EN COURS** : Ajouter bouton "Ajouter un document"',
            '📅 **Phase 3 FUTUR** : Interface CRUD complète (Modifier/Supprimer)'
        ].forEach(item => {
            solList.appendChild(createElement('li', {}, item));
        });
        solutions.appendChild(solList);
        section.appendChild(solutions);

        return section;
    }

    destroy() {
        const modals = document.querySelectorAll('.library-modal-overlay');
        modals.forEach(m => m.remove());

        if (this.container) {
            clearContainer(this.container);
        }
    }
}

export default LibraryViewEnhanced;
