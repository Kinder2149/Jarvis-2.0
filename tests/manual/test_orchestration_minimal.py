"""
Test orchestration minimal - Message simple avec timeout 90s
"""
import requests
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("TEST ORCHESTRATION MINIMAL")
print("=" * 60)

# 1. Récupérer premier projet
projects = requests.get(f"{BASE_URL}/api/projects", timeout=5).json()
project = projects[0]
project_id = project["id"]
project_path = Path(project["path"])

print(f"\n📁 Projet: {project['name']}")
print(f"   Path: {project_path}")

# 2. Créer conversation
response = requests.post(
    f"{BASE_URL}/api/projects/{project_id}/conversations",
    json={"agent_id": "JARVIS_Maître"},
    timeout=5
)
conversation_id = response.json()["id"]
print(f"\n💬 Conversation: {conversation_id[:8]}...")

# 3. Message ULTRA-SIMPLE
print("\n📤 Envoi message (timeout 90s)...")
print("   Message: 'Crée un fichier hello.py avec print(\"Hello\")'")

message = "Crée un fichier hello.py avec une seule ligne : print('Hello World')"

try:
    response = requests.post(
        f"{BASE_URL}/api/conversations/{conversation_id}/messages",
        json={"content": message},
        timeout=90  # 90 secondes max
    )
    
    print(f"\n📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        # Afficher structure réponse
        print(f"\n📝 Réponse reçue:")
        print(f"   Clés: {list(result.keys())}")
        
        # Afficher message si présent
        if "message" in result:
            print(f"   Message ({len(result['message'])} chars):")
            print(f"   {result['message'][:200]}...")
        else:
            print(f"   ⚠️ Pas de clé 'message' dans la réponse")
            print(f"   Réponse complète: {result}")
        
        # Vérifier délégations
        if result.get("delegations"):
            print(f"\n✅ ✅ ✅ DÉLÉGATIONS DÉTECTÉES: {len(result['delegations'])}")
            for deleg in result["delegations"]:
                print(f"\n  Agent: {deleg['agent']}")
                print(f"  Succès: {deleg['success']}")
                print(f"  Fichiers: {deleg.get('files_written', [])}")
            
            # Vérifier fichier
            hello_file = project_path / "hello.py"
            if hello_file.exists():
                print(f"\n🎉 🎉 🎉 FICHIER CRÉÉ: {hello_file}")
                print(f"Contenu ({hello_file.stat().st_size} bytes):")
                print(hello_file.read_text()[:200])
                print("\n✅ ✅ ✅ ORCHESTRATION FONCTIONNELLE ✅ ✅ ✅")
            else:
                print(f"\n⚠️ Fichier non trouvé: {hello_file}")
        else:
            print("\n❌ AUCUNE DÉLÉGATION")
            if "[DEMANDE_CODE_CODEUR:" in result["message"]:
                print("⚠️ Marqueur présent mais orchestration non exécutée")
            else:
                print("⚠️ JARVIS_Maître ne délègue pas")
    
    elif response.status_code == 503:
        print("⚠️ Service Mistral indisponible (503)")
    else:
        print(f"❌ Erreur: {response.text[:200]}")

except requests.exceptions.Timeout:
    print("\n❌ TIMEOUT (90s)")
    print("L'API Mistral est trop lente ou bloquée.")
    print("\nVérifie dans Mistral Console:")
    print("  - JARVIS_Maître a 0 functions (pas de function calling)")
    print("  - Les Agent IDs sont corrects")
except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
