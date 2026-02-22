import os

from backend.db.database import Database


async def migrate_sessions_to_conversations(sessions_dict: dict):
    """
    Migre les sessions in-memory existantes vers des conversations persistantes.
    À exécuter une seule fois lors du déploiement.

    Args:
        sessions_dict: Le dictionnaire SESSIONS de api.py
    """
    if not sessions_dict:
        return

    db = Database()
    await db.initialize()

    legacy_project = await db.create_project(
        name="Conversations Historiques",
        path=os.getcwd(),
        description="Projet créé automatiquement pour migrer les anciennes sessions",
    )

    for session_id, session_data in sessions_dict.items():
        conversation = await db.create_conversation(
            project_id=legacy_project["id"],
            agent_id=session_data.get("agent_id", "BASE"),
            title=f"Session {session_id[:8]}",
        )

        for msg in session_data.get("history", []):
            await db.add_message(
                conversation_id=conversation["id"], role=msg["role"], content=msg["content"]
            )

    sessions_dict.clear()


async def migrate_library_data():
    """
    Migre les données statiques de la librairie (frontend/js/views/library.js)
    vers la table library_documents.
    À exécuter une seule fois lors du déploiement de la Knowledge Base.
    """
    import json
    import uuid
    from datetime import datetime

    db = Database()
    await db.initialize()

    # Données extraites de library.js
    library_items = [
        # Librairies & Frameworks
        {
            "category": "libraries",
            "name": "FastAPI",
            "icon": "⚡",
            "description": "Framework web Python async — routes, modèles Pydantic, middleware",
            "tags": ["python", "web", "api"],
            "agents": ["CODEUR", "BASE"],
            "content": """# FastAPI — Référence rapide

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
assert response.status_code == 200""",
        },
        {
            "category": "libraries",
            "name": "Pytest",
            "icon": "🧪",
            "description": "Framework de tests Python — fixtures, parametrize, tmp_path",
            "tags": ["python", "testing"],
            "agents": ["CODEUR", "BASE"],
            "content": """# Pytest — Référence rapide

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
pytest tests/ -v --tb=short""",
        },
        {
            "category": "libraries",
            "name": "Pydantic",
            "icon": "📋",
            "description": "Validation de données Python — BaseModel, Field, validators",
            "tags": ["python", "validation"],
            "agents": ["CODEUR"],
            "content": """# Pydantic v2 — Référence rapide

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
        return v""",
        },
        {
            "category": "libraries",
            "name": "aiosqlite",
            "icon": "🗃️",
            "description": "SQLite async pour Python — requêtes, transactions",
            "tags": ["python", "database", "async"],
            "agents": ["CODEUR"],
            "content": """# aiosqlite — Référence rapide

## Installation
pip install aiosqlite

## Connexion et requêtes
import aiosqlite

async def example():
    async with aiosqlite.connect("data.db") as db:
        db.row_factory = aiosqlite.Row

        # Créer table
        await db.execute(\"\"\"
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            )
        \"\"\")
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
            return [dict(r) for r in rows]""",
        },
        {
            "category": "libraries",
            "name": "Flutter",
            "icon": "🐦",
            "description": "Framework mobile/web — widgets, state, navigation",
            "tags": ["flutter", "dart", "mobile"],
            "agents": ["CODEUR"],
            "content": """# Flutter — Référence rapide

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
        Text('Count: $_count'),
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
final response = await http.get(Uri.parse('https://api.example.com/data'));""",
        },
        # Méthodologies
        {
            "category": "methodologies",
            "name": "Audit > Plan > Exécution",
            "icon": "🎯",
            "description": "Méthodologie principale JARVIS — cycle complet de travail",
            "tags": ["process", "core"],
            "agents": ["JARVIS_Maître"],
            "content": """# Méthodologie : Audit > Plan > Validation > Exécution > Documentation

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
- Mettre à jour INDEX.md""",
        },
        {
            "category": "methodologies",
            "name": "Gouvernance documentaire",
            "icon": "📁",
            "description": "Règles de gestion des documents — reference/work/history",
            "tags": ["process", "documentation"],
            "agents": ["JARVIS_Maître", "BASE"],
            "content": """# Gouvernance documentaire

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
1 sujet = 1 document de référence (éviter redondances)""",
        },
        {
            "category": "methodologies",
            "name": "Revue de code",
            "icon": "🔍",
            "description": "Checklist de vérification du code produit par les agents",
            "tags": ["process", "quality"],
            "agents": ["BASE"],
            "content": """# Checklist revue de code

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
- [ ] Aucun TODO ou placeholder""",
        },
        # Prompts & Templates
        {
            "category": "prompts",
            "name": "Délégation au CODEUR",
            "icon": "➡️",
            "description": "Template de marqueur pour déléguer du code au CODEUR",
            "tags": ["inter-agent", "delegation"],
            "agents": ["JARVIS_Maître"],
            "content": """# Template : Délégation au CODEUR

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
Imports absolus simples, fichiers complets.]""",
        },
        {
            "category": "prompts",
            "name": "Vérification par BASE",
            "icon": "✅",
            "description": "Template pour demander une vérification de complétude à BASE",
            "tags": ["inter-agent", "verification"],
            "agents": ["JARVIS_Maître"],
            "content": """# Template : Vérification par BASE

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
- requirements.txt]""",
        },
        {
            "category": "prompts",
            "name": "Création de projet",
            "icon": "🆕",
            "description": "Template de prompt pour demander la création d'un nouveau projet",
            "tags": ["user", "project"],
            "agents": ["JARVIS_Maître"],
            "content": """# Template : Demande de création de projet

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
- Mentionner les dépendances exactes""",
        },
        # Données personnelles
        {
            "category": "personal",
            "name": "Conventions de code",
            "icon": "📝",
            "description": "Règles de style et conventions suivies dans tous les projets",
            "tags": ["style", "rules"],
            "agents": ["CODEUR", "JARVIS_Maître", "BASE"],
            "content": """# Conventions de code — Val C.

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
- tmp_path pour les fichiers temporaires""",
        },
        {
            "category": "personal",
            "name": "Stack technique",
            "icon": "🛠️",
            "description": "Technologies utilisées et préférées",
            "tags": ["tech", "preferences"],
            "agents": ["JARVIS_Maître", "CODEUR"],
            "content": """# Stack technique — Val C.

## Backend
- Python 3.11+
- FastAPI (web framework)
- SQLite + aiosqlite (base de données)
- Pydantic v2 (validation)
- Google Gemini (LLM)

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
- localhost:8000 pour le backend""",
        },
    ]

    async with db._connect() as conn:
        for item in library_items:
            doc_id = str(uuid.uuid4())
            now = datetime.now().isoformat()

            await conn.execute(
                """INSERT INTO library_documents 
                (id, category, name, icon, description, content, tags, agents, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    doc_id,
                    item["category"],
                    item["name"],
                    item.get("icon", ""),
                    item["description"],
                    item["content"],
                    json.dumps(item.get("tags", [])),
                    json.dumps(item.get("agents", [])),
                    now,
                    now,
                ),
            )
        await conn.commit()

    print(f"Migration terminée : {len(library_items)} documents insérés dans library_documents")
