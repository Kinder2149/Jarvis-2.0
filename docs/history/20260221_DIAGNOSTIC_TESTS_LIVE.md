# Diagnostic Tests Live - Problème Identifié

**Date** : 2026-02-21 19:20
**Statut** : 🔍 DIAGNOSTIC EN COURS

---

## Problème Constaté

**Symptôme** : Les tests live ne se lancent pas ou timeout après 10 minutes

**Observations** :
1. Backend démarre correctement (port 8000)
2. Serveur accessible via HTTP
3. Création projet/conversation fonctionne
4. **Envoi message bloque ou timeout**

---

## Causes Potentielles

### 1. Configuration .env Manquante ✅ RÉSOLU
**Problème** : `.env` n'existait pas, variables providers non chargées
**Solution** : `Copy-Item ".env.configured" ".env" -Force`
**Statut** : ✅ Corrigé

### 2. Base de Données Corrompue
**Problème** : Contraintes UNIQUE échouent (projets déjà existants)
**Solution** : Supprimer `jarvis_data.db` avant chaque test
**Statut** : ⚠️ À vérifier

### 3. Timeout Gemini API
**Problème** : Gemini peut prendre >60s pour répondre
**Solution** : Augmenter timeout à 180s
**Statut** : ⚠️ À tester

### 4. Orchestration Bloquée
**Problème** : Boucle infinie dans `SimpleOrchestrator`
**Solution** : Vérifier logs backend
**Statut** : 🔍 À investiguer

### 5. Quotas Gemini Dépassés
**Problème** : 15 RPM, 1M TPM dépassés
**Solution** : Attendre 1 minute entre tests
**Statut** : ⚠️ Possible

---

## Actions Effectuées

1. ✅ Copié `.env.configured` → `.env`
2. ✅ Supprimé `jarvis_data.db`
3. ✅ Nettoyé dossier `D:\Coding\TEST`
4. ✅ Redémarré backend
5. ⏳ Test simple en cours...

---

## Prochaines Actions

### Immédiat
1. Créer test ultra-simple (juste JARVIS_Maître, pas de délégation)
2. Vérifier logs backend en temps réel
3. Tester avec timeout 180s

### Si Problème Persiste
1. Vérifier quotas Gemini
2. Tester avec un seul agent (pas d'orchestration)
3. Ajouter logs détaillés dans orchestration

---

## Test Ultra-Simple Recommandé

```python
# Test sans délégation, juste réponse JARVIS_Maître
import requests

BASE_URL = "http://localhost:8000"

# 1. Créer projet
resp = requests.post(f"{BASE_URL}/api/projects", json={
    "name": "test_minimal",
    "path": "D:\\Coding\\TEST\\test_minimal",
    "description": "Test"
})
project = resp.json()

# 2. Créer conversation
resp = requests.post(f"{BASE_URL}/api/conversations", json={
    "project_id": project["id"],
    "title": "Test",
    "agent_id": "JARVIS_Maître"
})
conv = resp.json()

# 3. Message simple (pas de code)
resp = requests.post(
    f"{BASE_URL}/api/conversations/{conv['id']}/messages",
    json={"content": "Bonjour, qui es-tu ?"},
    timeout=30
)
print(resp.json()["response"])
```

---

## Hypothèse Principale

**Le problème est probablement lié aux quotas Gemini ou à un timeout trop court.**

**Raison** :
- Backend démarre ✅
- API accessible ✅
- Création projet/conv ✅
- **Envoi message bloque** ❌

**Solution recommandée** :
1. Augmenter timeout à 180s
2. Ajouter retry avec backoff
3. Vérifier quotas Gemini

---

## Commandes de Diagnostic

### Vérifier Backend Logs
```bash
# Voir les logs en temps réel
Get-Content jarvis_audit.log -Tail 50 -Wait
```

### Tester API Directement
```bash
# Test création projet
curl -X POST http://localhost:8000/api/projects -H "Content-Type: application/json" -d '{"name":"test","path":"D:\\Coding\\TEST\\test","description":"Test"}'

# Test création conversation
curl -X POST http://localhost:8000/api/conversations -H "Content-Type: application/json" -d '{"project_id":"XXX","title":"Test","agent_id":"JARVIS_Maître"}'

# Test envoi message
curl -X POST http://localhost:8000/api/conversations/XXX/messages -H "Content-Type: application/json" -d '{"content":"Bonjour"}' --max-time 60
```

---

## Métriques Attendues

### Temps de Réponse Normal
- JARVIS_Maître simple : 4-10s
- JARVIS_Maître avec délégation : 30-60s
- CODEUR génération : 10-30s
- Orchestration complète : 60-180s

### Si Timeout
- < 30s : Problème backend
- 30-60s : Problème Gemini API
- > 60s : Problème orchestration/boucle

---

## État Actuel

**Backend** : ✅ Démarré (PID 21968)
**Configuration** : ✅ `.env` copié
**Base de données** : ✅ Nettoyée
**Dossier test** : ✅ Nettoyé

**Prochaine action** : Lancer test ultra-simple sans délégation
