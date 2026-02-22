# Règles Storage JSON (Python)

**Type** : Règle architecturale  
**Langage** : Python  
**Catégorie** : Persistance de données

---

## Règle obligatoire

Une classe Storage JSON **DOIT TOUJOURS** avoir ces 3 méthodes :

### 1. Constructeur
```python
def __init__(self, filepath: str):
    self.filepath = filepath
```

### 2. Méthode save
```python
def save(self, data: list) -> None:
    """Sauvegarde les données dans le fichier JSON."""
    with open(self.filepath, 'w', encoding='utf-8') as f:
        json.dump([item.to_dict() for item in data], f, indent=2)
```

### 3. Méthode load
```python
def load(self) -> list:
    """Charge les données depuis le fichier JSON."""
    if not os.path.exists(self.filepath):
        return []
    with open(self.filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return [Item.from_dict(d) for d in data]
```

---

## Exemple complet

```python
import json
import os
from pathlib import Path
from typing import List

class Item:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
    
    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name}
    
    @staticmethod
    def from_dict(data: dict) -> 'Item':
        return Item(data["id"], data["name"])

class JsonStorage:
    """Storage JSON avec constructeur, save ET load."""
    
    def __init__(self, filepath: str = "data.json"):
        """IMPORTANT : Toujours inclure un constructeur."""
        self.filepath = Path(filepath)
    
    def save(self, items: List[Item]) -> None:
        """IMPORTANT : save() est obligatoire pour la persistance."""
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump([i.to_dict() for i in items], f, indent=2)
    
    def load(self) -> List[Item]:
        """IMPORTANT : load() doit gérer le cas fichier inexistant."""
        if not self.filepath.exists():
            return []
        with open(self.filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Item.from_dict(d) for d in data]

# Utilisation
storage = JsonStorage("items.json")
items = storage.load()
items.append(Item(1, "Test"))
storage.save(items)
```

---

## Erreurs courantes

❌ **Oublier save()** : La classe ne peut pas persister les données  
❌ **Oublier load()** : La classe ne peut pas charger les données  
❌ **Oublier __init__** : Impossible d'instancier la classe  
❌ **Ne pas gérer FileNotFoundError** : Crash au premier load()

✅ **Toujours inclure les 3 méthodes** même si l'instruction ne les mentionne pas explicitement.
