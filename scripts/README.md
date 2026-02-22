# Scripts Utilitaires — JARVIS 2.0

**Description** : Scripts d'aide et maintenance  
**Date** : 2026-02-18

---

## 📁 Contenu

### `check_test_result.py`

**Description** : Vérification résultats tests pytest

**Usage** :
```bash
python scripts/check_test_result.py
```

### `clean_test_projects.py`

**Description** : Nettoyage projets de test de la base de données

**Fonction** : Supprime tous les projets avec :
- Chemin contenant `test_`
- Chemin contenant `Temp`
- Nom commençant par `Test`

**Usage** :
```bash
python scripts/clean_test_projects.py
```

**⚠️ Attention** : Supprime définitivement les projets de la base de données `jarvis_data.db`

---

## 📝 Notes

- Scripts à usage ponctuel (maintenance, diagnostic)
- Ne font pas partie de la suite de tests
- Peuvent modifier la base de données (attention)
