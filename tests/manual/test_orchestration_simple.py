"""
Test orchestration simplifié - Utilise un projet existant
"""
import requests
import json
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def test_orchestration():
    """Test orchestration avec projet existant"""
    
    # 1. Lister projets existants
    print("📋 Liste des projets...")
    response = requests.get(f"{BASE_URL}/api/projects")
    projects = response.json()
    print(f"✅ {len(projects)} projet(s) trouvé(s)")
    
    # 2. Créer ou utiliser projet de test
    project_path = Path("d:/Coding/AppWindows/Jarvis 2.0/TEST_LIVE/test_orchestration_calc")
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Chercher si projet existe déjà
    existing_project = None
    for p in projects:
        if p["path"] == str(project_path):
            existing_project = p
            break
    
    if existing_project:
        print(f"✅ Projet existant trouvé: {existing_project['id']}")
        project_id = existing_project["id"]
    else:
        print("📁 Création nouveau projet...")
        try:
            response = requests.post(
                f"{BASE_URL}/api/projects",
                json={"name": "Test Orchestration Calc", "path": str(project_path)}
            )
            if response.status_code != 200:
                print(f"❌ Erreur création projet: {response.status_code}")
                print(response.text)
                return False
            project_id = response.json()["id"]
            print(f"✅ Projet créé: {project_id}")
        except Exception as e:
            print(f"❌ Exception création projet: {e}")
            return False
    
    # 3. Créer conversation
    print("\n💬 Création conversation...")
    response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/conversations",
        json={"agent_id": "JARVIS_Maître"}
    )
    if response.status_code != 200:
        print(f"❌ Erreur création conversation: {response.status_code}")
        print(response.text)
        return False
    
    conversation_id = response.json()["id"]
    print(f"✅ Conversation créée: {conversation_id}")
    
    # 4. Envoyer message
    print("\n📤 Envoi message (demande calculatrice)...")
    message = """Crée une calculatrice Python simple avec :
- Fichier src/calculator.py avec 4 opérations (add, sub, mul, div)
- Fichier tests/test_calculator.py avec tests unitaires pytest
- Fichier requirements.txt avec pytest

Utilise des fonctions simples, pas de classes."""
    
    response = requests.post(
        f"{BASE_URL}/api/conversations/{conversation_id}/messages",
        json={"content": message}
    )
    
    print(f"📊 Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Réponse reçue")
        print(f"\n📝 Message JARVIS_Maître (extrait):")
        print(result["message"][:300] + "...")
        
        if result.get("delegations"):
            print(f"\n🔄 Délégations: {len(result['delegations'])}")
            for deleg in result["delegations"]:
                print(f"  - {deleg['agent']}: {deleg['success']} ({len(deleg.get('files_written', []))} fichiers)")
        else:
            print("\n⚠️ Aucune délégation détectée")
        
        # Vérifier fichiers
        print("\n📂 Vérification fichiers...")
        expected = ["src/calculator.py", "tests/test_calculator.py", "requirements.txt"]
        created = []
        for fname in expected:
            fpath = project_path / fname
            if fpath.exists():
                print(f"  ✅ {fname} ({fpath.stat().st_size} bytes)")
                created.append(fname)
            else:
                print(f"  ❌ {fname} MANQUANT")
        
        print(f"\n📊 RÉSULTAT: {len(created)}/{len(expected)} fichiers")
        return len(created) == len(expected)
    
    elif response.status_code == 503:
        print("⚠️ Service Mistral indisponible (503)")
        return None
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(response.text[:500])
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST ORCHESTRATION JARVIS 2.0 (SIMPLIFIÉ)")
    print("=" * 60)
    
    try:
        result = test_orchestration()
        
        if result is True:
            print("\n" + "=" * 60)
            print("🎉 TEST RÉUSSI - Orchestration fonctionnelle")
            print("=" * 60)
        elif result is False:
            print("\n" + "=" * 60)
            print("❌ TEST ÉCHOUÉ")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️ TEST INDÉTERMINÉ - Service indisponible")
            print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
