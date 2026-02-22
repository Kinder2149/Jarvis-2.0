# Architecture Complète de la Library - JARVIS 2.0

## Date : 22 février 2026

---

## 📋 Vue d'Ensemble

La **Library** (Knowledge Base) est un système de gestion de documentation technique à **3 couches** :

1. **Couche Données** : Base SQLite (`library_documents`)
2. **Couche Backend** : API REST + Functions pour agents
3. **Couche Frontend** : Interface utilisateur + Données statiques hardcodées

**⚠️ ÉTAT ACTUEL** : **Système hybride non unifié**
- Frontend utilise des données **hardcodées** (JavaScript)
- Backend a une BDD **vide** (jamais migrée)
- Agents **peuvent** accéder via functions mais BDD vide = inutile

---

## 🏗️ Architecture des 3 Couches

### **COUCHE 1 : Base de Données SQLite**

#### Schéma `library_documents`
```sql
CREATE TABLE IF NOT EXISTS library_documents (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL CHECK(category IN ('libraries', 'methodologies', 'prompts', 'personal')),
    name TEXT NOT NULL,
    icon TEXT,
    description TEXT,
    content TEXT NOT NULL,
    tags TEXT,        -- JSON array stringifié
    agents TEXT,      -- JSON array stringifié
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### Index
- `idx_library_category` : Recherche par catégorie
- `idx_library_updated` : Tri par date de mise à jour
- `idx_library_name` : Recherche par nom

#### État Actuel
- ✅ **Table créée** (via `schema.sql`)
- ❌ **Aucune donnée** (migration jamais exécutée)
- ⚠️ **Script de migration existe** (`backend/db/migrations.py`) mais jamais lancé

---

### **COUCHE 2 : Backend API + Functions**

#### API REST (`backend/api.py`)

| Endpoint | Méthode | Description | État |
|----------|---------|-------------|------|
| `/api/library` | GET | Liste documents (filtres : category, agent, tag, search) | ✅ Implémenté |
| `/api/library/{doc_id}` | GET | Récupère un document par ID | ✅ Implémenté |
| `/api/library` | POST | Crée un nouveau document | ✅ Implémenté |
| `/api/library/{doc_id}` | PUT | Met à jour un document | ✅ Implémenté |
| `/api/library/{doc_id}` | DELETE | Supprime un document | ✅ Implémenté |

**État** : ✅ API complète et fonctionnelle, mais **BDD vide** donc retourne toujours `[]`

#### Functions pour Agents (`backend/services/function_executor.py`)

**Function 1 : `get_library_document`**
```python
async def get_library_document(self, name: str, category: str | None = None) -> dict
```
- **Usage** : Agents peuvent chercher un document par nom
- **Agents autorisés** : BASE, JARVIS_Maître (via prompt)
- **État** : ✅ Implémenté mais **BDD vide** donc retourne toujours erreur "not found"

**Function 2 : `get_library_list`**
```python
async def get_library_list(self, category: str | None = None) -> dict
```
- **Usage** : Agents peuvent lister les documents d'une catégorie
- **Agents autorisés** : BASE, JARVIS_Maître
- **État** : ✅ Implémenté mais **BDD vide** donc retourne toujours `[]`

#### Couche Database (`backend/db/database.py`)

**Méthodes disponibles** :
- `create_library_document()` : Insère un document
- `get_library_document(doc_id)` : Récupère par ID
- `list_library_documents(category, agent, tag, search)` : Liste avec filtres
- `update_library_document(doc_id, updates)` : Met à jour
- `delete_library_document(doc_id)` : Supprime

**État** : ✅ Toutes les méthodes implémentées et testées

---

### **COUCHE 3 : Frontend**

#### Données Statiques Hardcodées (`frontend/js/views/library.js`)

**Structure** : Constante JavaScript `LIBRARY_CATEGORIES`
```javascript
const LIBRARY_CATEGORIES = [
    {
        id: 'libraries',
        name: 'Librairies & Frameworks',
        icon: '📚',
        items: [
            { id: 'python-fastapi', name: 'FastAPI', content: '...', agents: ['CODEUR', 'BASE'] },
            { id: 'python-pytest', name: 'Pytest', content: '...', agents: ['CODEUR', 'BASE'] },
            // ... 5 items total
        ]
    },
    {
        id: 'methodologies',
        name: 'Méthodologies',
        icon: '📋',
        items: [
            { id: 'methodo-audit-plan', name: 'Audit > Plan > Exécution', agents: ['JARVIS_Maitre'] },
            // ... 3 items total
        ]
    },
    {
        id: 'prompts',
        name: 'Prompts & Templates',
        icon: '💬',
        items: [
            { id: 'prompt-delegation-codeur', name: 'Délégation au CODEUR', agents: ['JARVIS_Maitre'] },
            // ... 3 items total
        ]
    },
    {
        id: 'personal',
        name: 'Données personnelles',
        icon: '👤',
        items: [
            { id: 'personal-conventions', name: 'Conventions de code', agents: ['CODEUR', 'JARVIS_Maitre', 'BASE'] },
            // ... 2 items total
        ]
    }
];
```

**Total** : **4 catégories**, **13 documents** hardcodés

#### Interface Utilisateur

**Fonctionnalités** :
- ✅ Affichage des 4 catégories
- ✅ Filtres par catégorie
- ✅ Statistiques (catégories, documents, agents liés)
- ✅ Modal de prévisualisation du contenu
- ✅ Tags agents affichés
- ❌ **Aucune interaction avec l'API backend**
- ❌ **Aucun CRUD** (création, modification, suppression)

**État** : ✅ Interface fonctionnelle mais **100% statique**

---

## 🔄 Flow de Données Actuel

### **Scénario 1 : Utilisateur consulte la Library**

```
👤 Utilisateur clique "Library"
    ↓
📱 Frontend charge library.js
    ↓
📦 Lecture LIBRARY_CATEGORIES (hardcodé)
    ↓
🖥️ Affichage des 13 documents
    ↓
❌ AUCUN appel API backend
```

**Résultat** : Utilisateur voit les données hardcodées, jamais synchronisées avec la BDD

---

### **Scénario 2 : Agent cherche un document**

```
🤖 Agent (BASE ou JARVIS_Maître) appelle get_library_document("FastAPI")
    ↓
⚙️ FunctionExecutor.get_library_document()
    ↓
🗄️ Database.list_library_documents(search="FastAPI")
    ↓
📊 SELECT * FROM library_documents WHERE content LIKE '%FastAPI%'
    ↓
❌ BDD vide → Retourne []
    ↓
🤖 Agent reçoit : {"success": False, "error": "Document 'FastAPI' not found"}
```

**Résultat** : Agent ne peut **jamais** accéder aux documents, même s'ils existent en frontend

---

### **Scénario 3 : Migration des données (jamais exécuté)**

```
🔧 Script migrations.py existe
    ↓
📝 Fonction migrate_library_data() prête
    ↓
❌ JAMAIS EXÉCUTÉE
    ↓
🗄️ BDD reste vide
```

**Raison** : Migration manuelle requise, jamais lancée

---

## 🚨 Problèmes Identifiés

### **1. Désynchronisation Frontend ↔ Backend**
- Frontend : 13 documents hardcodés
- Backend BDD : 0 documents
- **Conséquence** : Agents ne peuvent pas accéder aux documents que l'utilisateur voit

### **2. Données Hardcodées Non Maintenables**
- Modification d'un document = éditer `library.js` manuellement
- Pas de versioning
- Pas de traçabilité
- **Conséquence** : Risque d'incohérences, difficile à maintenir

### **3. Agents Aveugles**
- Functions `get_library_document` et `get_library_list` implémentées
- Mais BDD vide donc inutiles
- **Conséquence** : Agents ne peuvent pas consulter la documentation technique

### **4. Pas de CRUD Utilisateur**
- Utilisateur ne peut pas ajouter/modifier/supprimer des documents
- API CRUD existe mais pas d'interface
- **Conséquence** : Library figée, pas évolutive

### **5. Migration Jamais Exécutée**
- Script `migrate_library_data()` existe depuis longtemps
- Jamais lancé
- **Conséquence** : BDD reste vide indéfiniment

---

## ✅ Fonctionnalités Implémentées

### **Backend**
- ✅ Table `library_documents` créée
- ✅ API REST complète (GET, POST, PUT, DELETE)
- ✅ Functions pour agents (`get_library_document`, `get_library_list`)
- ✅ Filtres avancés (category, agent, tag, search)
- ✅ Script de migration prêt

### **Frontend**
- ✅ Affichage 4 catégories
- ✅ 13 documents hardcodés
- ✅ Filtres par catégorie
- ✅ Modal de prévisualisation
- ✅ Tags agents affichés
- ✅ Statistiques temps réel

---

## ❌ Fonctionnalités Non Implémentées

### **Backend**
- ❌ Migration des données jamais exécutée
- ❌ Pas de seed data automatique au démarrage

### **Frontend**
- ❌ Aucun appel API backend
- ❌ Pas d'interface CRUD (création, modification, suppression)
- ❌ Pas de synchronisation avec la BDD
- ❌ Pas de gestion des versions de documents

### **Agents**
- ❌ Agents ne peuvent pas accéder aux documents (BDD vide)
- ❌ Pas de mise à jour automatique de la Library par les agents
- ❌ Pas de suggestion de nouveaux documents par les agents

---

## 🎯 Utilisation Réelle des Agents

### **Agents Concernés**

| Agent | Utilisation Library | État Actuel |
|-------|---------------------|-------------|
| **JARVIS_Maître** | Consulte méthodologies, prompts, conventions | ❌ BDD vide, ne peut pas accéder |
| **BASE** | Consulte librairies, méthodologies, conventions | ❌ BDD vide, ne peut pas accéder |
| **CODEUR** | Consulte librairies, conventions de code | ❌ Pas de function, ne peut pas accéder |
| **VALIDATEUR** | Consulte conventions de code | ❌ Pas de function, ne peut pas accéder |

### **Functions Disponibles**

**Dans `config_agents/BASE.md` et `config_agents/JARVIS_MAITRE.md`** :
```json
{
  "name": "get_library_document",
  "description": "Recherche un document dans la Knowledge Base",
  "parameters": {
    "name": "Nom du document",
    "category": "Catégorie optionnelle"
  }
}
```

**État** : ✅ Déclarées dans les prompts, ❌ Inutilisables (BDD vide)

---

## 🔧 Comment les Agents Devraient Utiliser la Library

### **Scénario Idéal : CODEUR génère du code FastAPI**

```
👤 Utilisateur : "Crée une API FastAPI pour gérer des utilisateurs"
    ↓
👑 JARVIS_Maître analyse la demande
    ↓
🔍 JARVIS_Maître appelle get_library_document("FastAPI", "libraries")
    ↓
📚 Récupère le template FastAPI avec exemples
    ↓
👑 JARVIS_Maître délègue au CODEUR avec contexte enrichi :
    "[DEMANDE_CODE_CODEUR: Crée une API FastAPI...
     Référence : [contenu du document FastAPI]]"
    ↓
💻 CODEUR génère du code conforme aux patterns de la Library
```

**Résultat attendu** : Code de meilleure qualité, conforme aux conventions

---

## 📊 Statistiques Actuelles

### **Données Frontend (Hardcodées)**
- **4 catégories** : Librairies, Méthodologies, Prompts, Personnel
- **13 documents** :
  - 5 Librairies (FastAPI, Pytest, Pydantic, aiosqlite, Flutter)
  - 3 Méthodologies (Audit>Plan>Exécution, Gouvernance doc, Revue code)
  - 3 Prompts (Délégation CODEUR, Vérification BASE, Création projet)
  - 2 Personnel (Conventions code, Stack technique)

### **Données Backend (BDD)**
- **0 documents** (table vide)
- **0 catégories utilisées**
- **0 appels API** depuis le frontend

### **Utilisation Agents**
- **0 appels** à `get_library_document` (BDD vide)
- **0 appels** à `get_library_list` (BDD vide)
- **0 documents consultés** par les agents

---

## 🚀 Solutions Recommandées

### **Option 1 : Migration Immédiate (Recommandé)**

**Actions** :
1. Exécuter `migrate_library_data()` pour peupler la BDD
2. Modifier frontend pour appeler `/api/library` au lieu de `LIBRARY_CATEGORIES`
3. Tester les functions agents

**Avantages** :
- ✅ Unifie frontend et backend
- ✅ Agents peuvent accéder aux documents
- ✅ Données centralisées

**Inconvénients** :
- ⚠️ Nécessite modification frontend
- ⚠️ Migration one-time à exécuter

---

### **Option 2 : Seed Automatique au Démarrage**

**Actions** :
1. Ajouter `seed_library_data()` dans `backend/app.py` au startup
2. Vérifier si BDD vide, si oui → insérer les 13 documents
3. Frontend continue d'appeler `/api/library`

**Avantages** :
- ✅ Automatique, pas de migration manuelle
- ✅ BDD toujours peuplée

**Inconvénients** :
- ⚠️ Données dupliquées (hardcodées + BDD)
- ⚠️ Risque de désynchronisation

---

### **Option 3 : Interface CRUD Frontend**

**Actions** :
1. Ajouter boutons "Ajouter", "Modifier", "Supprimer" dans la Library
2. Formulaires pour créer/éditer des documents
3. Appels API POST/PUT/DELETE

**Avantages** :
- ✅ Utilisateur peut gérer la Library
- ✅ Données évolutives

**Inconvénients** :
- ⚠️ Développement frontend important
- ⚠️ Nécessite gestion des permissions

---

## 📝 Recommandation Finale

**Approche Hybride (Option 1 + 3)** :

1. **Court terme** : Exécuter migration pour peupler BDD
2. **Moyen terme** : Modifier frontend pour lire depuis API
3. **Long terme** : Ajouter interface CRUD pour gestion utilisateur

**Bénéfices** :
- Agents peuvent immédiatement accéder aux documents
- Frontend et backend synchronisés
- Évolutivité future garantie

---

## 🔍 Vérification de l'État Actuel

### **Commandes de Diagnostic**

```bash
# Vérifier si BDD contient des documents
sqlite3 jarvis_data.db "SELECT COUNT(*) FROM library_documents;"
# Résultat attendu : 0

# Lister les documents (devrait être vide)
sqlite3 jarvis_data.db "SELECT id, name, category FROM library_documents;"
# Résultat attendu : (vide)

# Vérifier le schéma
sqlite3 jarvis_data.db ".schema library_documents"
# Résultat attendu : CREATE TABLE...
```

### **Test API**

```bash
# Lister tous les documents
curl http://localhost:8000/api/library
# Résultat attendu : {"agents": []}

# Chercher un document
curl "http://localhost:8000/api/library?search=FastAPI"
# Résultat attendu : {"agents": []}
```

---

## 📚 Fichiers Concernés

### **Backend**
- `backend/db/schema.sql` : Schéma table `library_documents`
- `backend/db/database.py` : Méthodes CRUD
- `backend/db/migrations.py` : Script migration (jamais exécuté)
- `backend/api.py` : Routes API `/api/library`
- `backend/services/function_executor.py` : Functions agents
- `backend/models.py` : Modèles Pydantic `LibraryDocument`

### **Frontend**
- `frontend/js/views/library.js` : Vue Library (données hardcodées)
- `frontend/css/library.css` : Styles Library

### **Configuration Agents**
- `config_agents/BASE.md` : Prompt avec functions Library
- `config_agents/JARVIS_MAITRE.md` : Prompt avec functions Library

---

## 🎯 Conclusion

La Library est un système **bien architecturé** mais **non unifié** :
- ✅ Backend complet et fonctionnel
- ✅ Frontend ergonomique
- ❌ **Aucune synchronisation** entre les deux
- ❌ **Agents aveugles** (BDD vide)
- ❌ **Migration jamais exécutée**

**Action prioritaire** : Exécuter la migration pour débloquer l'accès agents et unifier le système.
