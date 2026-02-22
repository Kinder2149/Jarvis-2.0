# Règles Frontend HTML/JS

**Type** : Règle architecturale  
**Langage** : HTML/CSS/JavaScript  
**Catégorie** : Interface utilisateur web

---

## Règle obligatoire

Quand on demande un frontend web, une interface HTML, ou une application web :

**OBLIGATOIRE** : Générer ces 3 fichiers :

1. `static/index.html` — Page HTML principale
2. `static/app.js` — Code JavaScript pour l'interface
3. `static/style.css` — Styles CSS

---

## Exemple minimal

### static/index.html
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Application</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div id="app">
        <h1>Application</h1>
        <div id="content"></div>
    </div>
    <script src="app.js"></script>
</body>
</html>
```

### static/app.js
```javascript
const API_URL = 'http://localhost:8000';

async function loadData() {
    const response = await fetch(`${API_URL}/items`);
    const data = await response.json();
    displayData(data);
}

function displayData(data) {
    const content = document.getElementById('content');
    content.innerHTML = data.map(item => `<div>${item.name}</div>`).join('');
}

loadData();
```

### static/style.css
```css
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f5f5f5;
}

#app {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
```

---

## Erreurs courantes

❌ **Générer seulement le backend** : L'utilisateur ne peut pas voir l'interface  
❌ **Oublier les fichiers frontend** : Pas d'interface utilisable  
❌ **Fichiers dans le mauvais dossier** : Respecter `static/` pour les fichiers statiques

✅ **Toujours générer les 3 fichiers** même si l'instruction ne mentionne que "crée une API".
