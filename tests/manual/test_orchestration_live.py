"""
Test live orchestration JARVIS 2.0
Teste la création d'un projet calculatrice via l'API REST
"""
import requests
import json
import time
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000"

def test_orchestration_calculatrice():
    """Test complet orchestration : projet calculatrice"""
    
    # 1. Créer projet
    print("📁 Création projet...")
    project_path = Path("d:/Coding/AppWindows/Jarvis 2.0/TEST_LIVE/test_orchestration_calc")
    project_path.mkdir(parents=True, exist_ok=True)
    
    response = requests.post(
        f"{BASE_URL}/api/projects",
        json={"name": "Test Orchestration Calc", "path": str(project_path)}
    )
    assert response.status_code == 200, f"Erreur création projet: {response.status_code}"
    project_id = response.json()["id"]
    print(f"✅ Projet créé: {project_id}")
    
    # 2. Créer conversation avec JARVIS_Maître
    print("\n💬 Création conversation...")
    response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/conversations",
        json={"agent_id": "JARVIS_Maître"}
    )
    assert response.status_code == 200, f"Erreur création conversation: {response.status_code}"
    conversation_id = response.json()["id"]
    print(f"✅ Conversation créée: {conversation_id}")
    
    # 3. Envoyer message demandant génération code
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
    
    print(f"📊 Status code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Réponse reçue")
        print(f"\n📝 Message JARVIS_Maître:")
        print(result["message"][:500] + "..." if len(result["message"]) > 500 else result["message"])
        
        if result.get("delegations"):
            print(f"\n🔄 Délégations détectées: {len(result['delegations'])}")
            for i, deleg in enumerate(result["delegations"], 1):
                print(f"\n  Délégation {i}:")
                print(f"    Agent: {deleg['agent']}")
                print(f"    Succès: {deleg['success']}")
                print(f"    Fichiers: {deleg.get('files_written', [])}")
        else:
            print("\n⚠️ Aucune délégation détectée")
        
        # 4. Vérifier fichiers créés
        print("\n📂 Vérification fichiers créés...")
        expected_files = [
            project_path / "src" / "calculator.py",
            project_path / "tests" / "test_calculator.py",
            project_path / "requirements.txt"
        ]
        
        files_created = []
        for file_path in expected_files:
            if file_path.exists():
                print(f"  ✅ {file_path.name} créé ({file_path.stat().st_size} bytes)")
                files_created.append(file_path.name)
            else:
                print(f"  ❌ {file_path.name} MANQUANT")
        
        print(f"\n📊 RÉSULTAT: {len(files_created)}/{len(expected_files)} fichiers créés")
        
        if len(files_created) == len(expected_files):
            print("✅ ✅ ✅ ORCHESTRATION RÉUSSIE ✅ ✅ ✅")
            return True
        else:
            print("❌ ORCHESTRATION INCOMPLÈTE")
            return False
    
    elif response.status_code == 503:
        print("⚠️ Service Mistral indisponible (503)")
        return None
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TEST LIVE ORCHESTRATION JARVIS 2.0")
    print("=" * 60)
    
    try:
        result = test_orchestration_calculatrice()
        
        if result is True:
            print("\n" + "=" * 60)
            print("🎉 TEST RÉUSSI - Orchestration fonctionnelle")
            print("=" * 60)
        elif result is False:
            print("\n" + "=" * 60)
            print("❌ TEST ÉCHOUÉ - Orchestration non fonctionnelle")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("⚠️ TEST INDÉTERMINÉ - Service Mistral indisponible")
            print("=" * 60)
    
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
