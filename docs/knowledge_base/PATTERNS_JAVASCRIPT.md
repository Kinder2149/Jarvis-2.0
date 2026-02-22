# Patterns JavaScript/TypeScript

**Type** : Patterns de code réutilisables  
**Langage** : JavaScript/TypeScript  
**Catégorie** : Bonnes pratiques

---

## Pattern 1 : API Express (Node.js)

```javascript
const express = require('express');
const app = express();
const PORT = 3000;

// Middleware
app.use(express.json());

// Routes
app.get('/items', (req, res) => {
    res.json({ items: [] });
});

app.post('/items', (req, res) => {
    const { name } = req.body;
    res.status(201).json({ id: 1, name });
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
```

---

## Pattern 2 : Tests Jest

```javascript
const { add, divide } = require('./calculator');

describe('Calculator', () => {
    test('should add two numbers', () => {
        expect(add(2, 3)).toBe(5);
    });

    test('should throw error on division by zero', () => {
        expect(() => divide(5, 0)).toThrow('Division by zero');
    });

    test('should handle edge cases', () => {
        expect(add(0, 0)).toBe(0);
        expect(add(-1, 1)).toBe(0);
    });
});
```

---

## Pattern 3 : React Component (Functional)

```javascript
import React, { useState, useEffect } from 'react';

function ItemList() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('/api/items')
            .then(res => res.json())
            .then(data => {
                setItems(data.items);
                setLoading(false);
            })
            .catch(err => console.error(err));
    }, []);

    if (loading) return <div>Loading...</div>;

    return (
        <div>
            <h1>Items</h1>
            <ul>
                {items.map(item => (
                    <li key={item.id}>{item.name}</li>
                ))}
            </ul>
        </div>
    );
}

export default ItemList;
```

---

## Pattern 4 : Async/Await avec gestion d'erreurs

```javascript
async function fetchData(url) {
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        console.error('Fetch error:', error);
        return { success: false, error: error.message };
    }
}
```

---

## Pattern 5 : TypeScript Interface

```typescript
interface User {
    id: number;
    name: string;
    email?: string;
}

class UserService {
    private users: User[] = [];

    addUser(user: User): void {
        this.users.push(user);
    }

    getUser(id: number): User | undefined {
        return this.users.find(u => u.id === id);
    }

    getAllUsers(): User[] {
        return [...this.users];
    }
}
```

---

## Pattern 6 : Validation avec Joi

```javascript
const Joi = require('joi');

const userSchema = Joi.object({
    name: Joi.string().min(3).max(30).required(),
    email: Joi.string().email().required(),
    age: Joi.number().integer().min(0).max(120)
});

function validateUser(data) {
    const { error, value } = userSchema.validate(data);
    
    if (error) {
        return { valid: false, errors: error.details };
    }
    
    return { valid: true, data: value };
}
```

---

## Conventions JavaScript/TypeScript

**Indentation** : 2 espaces  
**Imports** : ES6 modules (`import/export`) ou CommonJS (`require/module.exports`)  
**Naming** :
- Variables/fonctions : camelCase (`getUserById`)
- Classes : PascalCase (`UserService`)
- Constantes : UPPER_SNAKE_CASE (`API_URL`)

**Tests** : Jest ou Mocha  
**Linting** : ESLint  
**Type checking** : TypeScript ou JSDoc
