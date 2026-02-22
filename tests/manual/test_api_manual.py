"""Script de test manuel API JARVIS - Test live calculatrice"""
import requests
import json
import time
import os
from pathlib import Path

BASE_URL = "http://localhost:8000/api"

def test_live_calculatrice():
    """Test live complet : création projet + conversation + message"""
    
    print("=" * 60)
    print("TEST LIVE JARVIS - CALCULATRICE")
    print("=" * 60)
    
    # 1. Créer projet
    print("\n1. Création projet...")
    timestamp = int(time.time())
    project_path = f"D:/Coding/TEST/test_live_calc_{timestamp}"
    
    # Créer le dossier
    Path(project_path).mkdir(parents=True, exist_ok=True)
    print(f"   📁 Dossier créé: {project_path}")
    
    project_data = {
        "name": f"Test Live Calculatrice {timestamp}",
        "path": project_path,
        "description": "Test live JARVIS - Calculatrice Python"
    }
    
    r = requests.post(f"{BASE_URL}/projects", json=project_data)
    print(f"   Status: {r.status_code}")
    
    if r.status_code != 200:
        print(f"   Erreur: {r.text}")
        return
    
    project = r.json()
    project_id = project["id"]
    print(f"   ✅ Projet créé: {project_id}")
    
    # 2. Créer conversation
    print("\n2. Création conversation...")
    conv_data = {
        "agent_id": "JARVIS_Maître",
        "project_id": project_id,
        "title": "Test Calculatrice"
    }
    
    r = requests.post(f"{BASE_URL}/conversations", json=conv_data)
    print(f"   Status: {r.status_code}")
    
    if r.status_code != 200:
        print(f"   Erreur: {r.text}")
        return
    
    conversation = r.json()
    conversation_id = conversation["id"]
    print(f"   ✅ Conversation créée: {conversation_id}")
    
    # 3. Envoyer message
    print("\n3. Envoi message à JARVIS...")
    message_data = {
        "content": "Bonjour JARVIS, peux-tu créer une calculatrice Python simple avec les 4 opérations de base (addition, soustraction, multiplication, division) et des tests unitaires complets ?"
    }
    
    print("   ⏳ Attente réponse JARVIS (peut prendre 30-60s)...")
    start_time = time.time()
    
    r = requests.post(
        f"{BASE_URL}/conversations/{conversation_id}/messages",
        json=message_data,
        timeout=120
    )
    
    elapsed = time.time() - start_time
    print(f"   Status: {r.status_code} (temps: {elapsed:.1f}s)")
    
    if r.status_code != 200:
        print(f"   ❌ Erreur: {r.text}")
        return
    
    response = r.json()
    print(f"\n   ✅ Réponse reçue:")
    print(f"   Agent: {response.get('agent_name', 'N/A')}")
    print(f"   Contenu: {response.get('content', '')[:500]}...")
    
    # 4. Vérifier fichiers créés
    print("\n4. Vérification fichiers créés...")
    r = requests.get(f"{BASE_URL}/projects/{project_id}/files")
    
    if r.status_code == 200:
        files = r.json()
        print(f"   ✅ {len(files)} fichiers trouvés:")
        for f in files:
            print(f"      - {f.get('path', 'N/A')}")
    else:
        print(f"   ⚠️ Impossible de lister les fichiers: {r.status_code}")
    
    print("\n" + "=" * 60)
    print("TEST TERMINÉ")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_live_calculatrice()
    except requests.exceptions.ConnectionError:
        print("❌ ERREUR: Backend non accessible sur http://localhost:8000")
        print("   Vérifiez que le serveur est démarré: uvicorn backend.app:app --reload")
    except requests.exceptions.Timeout:
        print("❌ ERREUR: Timeout (>120s)")
        print("   La requête a pris trop de temps. Vérifiez les logs backend.")
    except Exception as e:
        print(f"❌ ERREUR: {e}")
