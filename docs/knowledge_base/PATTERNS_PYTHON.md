# Patterns Python

**Type** : Patterns de code réutilisables  
**Langage** : Python  
**Catégorie** : Bonnes pratiques

---

## Pattern 1 : CLI Simple

```python
def main():
    print("=== Application ===")
    while True:
        print("\n1. Action 1")
        print("2. Action 2")
        print("0. Quitter")
        
        choice = input("Choix: ").strip()
        
        if choice == "0":
            print("Au revoir!")
            break
        elif choice == "1":
            # Implémenter action 1
            pass
        elif choice == "2":
            # Implémenter action 2
            pass
        else:
            print("Choix invalide")

if __name__ == "__main__":
    main()
```

---

## Pattern 2 : Tests pytest

```python
import pytest

def test_success_case():
    """Test du cas nominal"""
    result = function(valid_input)
    assert result == expected_output

def test_error_case():
    """Test de la gestion d'erreur"""
    with pytest.raises(ExpectedError):
        function(invalid_input)

def test_edge_cases():
    """Test des cas limites"""
    assert function(None) is None
    assert function([]) == []
    assert function(0) == 0
```

---

## Pattern 3 : Pydantic v2 (BaseModel)

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

# Créer une instance
user = User(id=1, name="Alice", email="alice@example.com")

# Convertir en dict (Pydantic v2)
user_dict = user.model_dump()

# Créer depuis dict (Pydantic v2)
user2 = User.model_validate({"id": 2, "name": "Bob"})

# Copier avec modifications (Pydantic v2)
user3 = user.model_copy(update={"name": "Alice Updated"})

# Exclure champs non définis
user_dict_partial = user.model_dump(exclude_unset=True)
```

**IMPORTANT — API Pydantic v2** :
- ✅ `.model_dump()` au lieu de `.dict()`
- ✅ `.model_validate()` au lieu de `.parse_obj()`
- ✅ `.model_copy()` au lieu de `.copy()`
- ✅ `.model_dump_json()` au lieu de `.json()`
- ❌ N'utilise JAMAIS l'API Pydantic v1 (obsolète)

---

## Pattern 4 : Gestion d'erreurs

```python
def process_data(data: dict) -> dict:
    """Traite les données avec gestion d'erreurs."""
    try:
        if not data:
            raise ValueError("Données vides")
        
        result = {"status": "success", "data": data}
        return result
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Erreur inattendue: {str(e)}"}
```

---

## Pattern 5 : Classe avec méthodes

```python
class Calculator:
    """Calculatrice simple avec opérations de base."""
    
    @staticmethod
    def add(a: float, b: float) -> float:
        """Additionne deux nombres."""
        return a + b
    
    @staticmethod
    def divide(a: float, b: float) -> float:
        """Divise a par b. Lève ZeroDivisionError si b=0."""
        if b == 0:
            raise ZeroDivisionError("Division par zéro impossible")
        return a / b
```
