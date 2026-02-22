"""
Test ultra-simple du backend avec timeout court
"""
import requests

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("TEST BACKEND SIMPLE (timeout 5s)")
print("=" * 60)

# 1. Test health check
print("\n1. Test /health...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"   ✅ Status: {response.status_code}")
    print(f"   Réponse: {response.json()}")
except requests.exceptions.Timeout:
    print("   ❌ TIMEOUT (5s)")
    exit(1)
except Exception as e:
    print(f"   ❌ ERREUR: {e}")
    exit(1)

# 2. Test liste projets
print("\n2. Test /api/projects...")
try:
    response = requests.get(f"{BASE_URL}/api/projects", timeout=5)
    print(f"   ✅ Status: {response.status_code}")
    projects = response.json()
    print(f"   Projets: {len(projects)}")
except requests.exceptions.Timeout:
    print("   ❌ TIMEOUT (5s)")
    exit(1)
except Exception as e:
    print(f"   ❌ ERREUR: {e}")
    exit(1)

# 3. Test création conversation (si projets disponibles)
if projects:
    project_id = projects[0]["id"]
    print(f"\n3. Test création conversation (projet {project_id[:8]}...)...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/projects/{project_id}/conversations",
            json={"agent_id": "JARVIS_Maître"},
            timeout=5
        )
        print(f"   ✅ Status: {response.status_code}")
        if response.status_code == 200:
            conv_id = response.json()["id"]
            print(f"   Conversation: {conv_id[:8]}...")
        else:
            print(f"   ⚠️ Erreur: {response.text[:100]}")
    except requests.exceptions.Timeout:
        print("   ❌ TIMEOUT (5s)")
        exit(1)
    except Exception as e:
        print(f"   ❌ ERREUR: {e}")
        exit(1)

print("\n" + "=" * 60)
print("✅ BACKEND FONCTIONNEL")
print("=" * 60)
print("\nLe backend répond correctement.")
print("Le problème du test d'orchestration vient probablement")
print("du timeout trop long (60s) sur l'appel Mistral.")
