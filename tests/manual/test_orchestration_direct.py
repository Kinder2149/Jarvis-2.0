"""
Test orchestration direct - Utilise le premier projet disponible
"""
import requests
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

# 1. Récupérer premier projet
print("📋 Récupération projets...")
projects = requests.get(f"{BASE_URL}/api/projects").json()
print(f"✅ {len(projects)} projet(s) disponible(s)")

if not projects:
    print("❌ Aucun projet disponible")
    exit(1)

# Utiliser le premier projet
project = projects[0]
project_id = project["id"]
project_path = Path(project["path"])

print(f"\n📁 Projet sélectionné:")
print(f"  ID: {project_id}")
print(f"  Nom: {project['name']}")
print(f"  Path: {project_path}")

# 2. Créer conversation
print("\n💬 Création conversation...")
response = requests.post(
    f"{BASE_URL}/api/projects/{project_id}/conversations",
    json={"agent_id": "JARVIS_Maître"}
)

if response.status_code != 200:
    print(f"❌ Erreur: {response.status_code}")
    print(response.text)
    exit(1)

conversation_id = response.json()["id"]
print(f"✅ Conversation: {conversation_id}")

# 3. Envoyer message simple
print("\n📤 Envoi message test...")
message = """Crée un fichier test_hello.py avec une fonction hello() qui retourne 'Hello World'."""

response = requests.post(
    f"{BASE_URL}/api/conversations/{conversation_id}/messages",
    json={"content": message},
    timeout=60
)

print(f"📊 Status: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    print(f"✅ Réponse reçue ({len(result['message'])} chars)")
    
    # Afficher extrait réponse
    print(f"\n📝 Réponse JARVIS_Maître (300 premiers chars):")
    print(result["message"][:300])
    print("...")
    
    # Vérifier délégations
    if result.get("delegations"):
        print(f"\n✅ ✅ DÉLÉGATIONS DÉTECTÉES: {len(result['delegations'])}")
        for i, deleg in enumerate(result["delegations"], 1):
            print(f"\n  Délégation {i}:")
            print(f"    Agent: {deleg['agent']}")
            print(f"    Succès: {deleg['success']}")
            files = deleg.get('files_written', [])
            print(f"    Fichiers: {len(files)}")
            for f in files:
                print(f"      - {f}")
        
        # Vérifier fichier créé
        test_file = project_path / "test_hello.py"
        if test_file.exists():
            print(f"\n✅ ✅ ✅ FICHIER CRÉÉ: {test_file}")
            print(f"Taille: {test_file.stat().st_size} bytes")
            print("\n🎉 🎉 🎉 ORCHESTRATION FONCTIONNELLE 🎉 🎉 🎉")
        else:
            print(f"\n⚠️ Fichier non trouvé: {test_file}")
    else:
        print("\n❌ AUCUNE DÉLÉGATION DÉTECTÉE")
        print("\n⚠️ Vérifier si marqueur [DEMANDE_CODE_CODEUR:] présent dans réponse:")
        if "[DEMANDE_CODE_CODEUR:" in result["message"]:
            print("  ✅ Marqueur présent - Orchestration devrait se déclencher")
        else:
            print("  ❌ Marqueur absent - JARVIS_Maître ne délègue pas")

elif response.status_code == 503:
    print("⚠️ Service Mistral indisponible (503)")
else:
    print(f"❌ Erreur: {response.status_code}")
    print(response.text[:500])
