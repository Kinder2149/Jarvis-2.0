"""
Test minimal pour vérifier si JARVIS_Maître délègue correctement au CODEUR
Sans contexte projet, message ultra simple
"""

import os
import shutil
import time

import requests

BASE_URL = "http://localhost:8000"
TEST_PATH = "D:/Coding/TEST/test_minimal"

print("\n=== TEST MINIMAL DÉLÉGATION ===\n")

# Nettoyer le dossier test
if os.path.exists(TEST_PATH):
    shutil.rmtree(TEST_PATH)
os.makedirs(TEST_PATH, exist_ok=True)
print(f"✓ Dossier test créé : {TEST_PATH}")

# Créer un projet
print("\n1. Création projet...")
resp = requests.post(
    f"{BASE_URL}/api/projects",
    json={"name": "Test Minimal", "path": TEST_PATH, "description": "Test minimal délégation"},
)
if resp.status_code != 200:
    print(f"✗ Échec création projet : {resp.status_code} - {resp.text}")
    exit(1)
project_id = resp.json()["id"]
print(f"✓ Projet créé : {project_id[:8]}...")

# Créer une conversation
print("\n2. Création conversation...")
resp = requests.post(
    f"{BASE_URL}/api/projects/{project_id}/conversations",
    json={"agent_id": "JARVIS_Maître", "title": "Test Délégation"},
)
if resp.status_code != 200:
    print(f"✗ Échec création conversation : {resp.status_code} - {resp.text}")
    exit(1)
conv_id = resp.json()["id"]
print(f"✓ Conversation créée : {conv_id[:8]}...")

# Envoyer un message ULTRA SIMPLE
print("\n3. Envoi message ultra simple...")
message = "Crée un fichier hello.py avec print('Hello World')"
print(f"   Message : {message}")

start = time.time()
try:
    resp = requests.post(
        f"{BASE_URL}/api/conversations/{conv_id}/messages", json={"content": message}, timeout=300
    )
    elapsed = time.time() - start

    if resp.status_code != 200:
        print(f"\n✗ Échec envoi message : {resp.status_code} - {resp.text}")
        exit(1)

    response_data = resp.json()
    assistant_message = response_data.get("response", "")

    print(f"\n✓ Réponse reçue en {elapsed:.2f}s")
    print("\n--- RÉPONSE JARVIS_MAÎTRE ---")
    print(assistant_message[:1000])
    print("---\n")

    # Vérifier la délégation
    if "[DEMANDE_CODE_CODEUR:" in assistant_message:
        print("✅ SUCCÈS : JARVIS_Maître a délégué au CODEUR !")
        print(f"   Temps de réponse : {elapsed:.2f}s")

        # Vérifier si des fichiers ont été créés
        time.sleep(2)
        files = [f for f in os.listdir(TEST_PATH) if f.endswith(".py")]
        if files:
            print(f"✅ Fichiers créés : {files}")
        else:
            print("⚠️  Aucun fichier créé (orchestration backend à vérifier)")
    else:
        print("❌ ÉCHEC : JARVIS_Maître n'a PAS délégué au CODEUR")
        print("\n   Phrases problématiques détectées :")
        if "ne peux pas" in assistant_message.lower():
            print("   - 'ne peux pas' trouvé dans la réponse")
        if "je vais" in assistant_message.lower():
            print("   - 'je vais' trouvé (explique au lieu de déléguer)")
        if "manuel" in assistant_message.lower():
            print("   - 'manuel' trouvé (fournit instructions manuelles)")

        print("\n   ⚠️  PROBLÈME : Prompt Mistral Console mal déployé")
        print("   → Vérifier que le prompt contient 'TU PEUX ET TU DOIS utiliser les marqueurs'")

except requests.Timeout:
    elapsed = time.time() - start
    print(f"\n✗ TIMEOUT après {elapsed:.2f}s")
    print("   ⚠️  PROBLÈME : API Mistral trop lente ou function calling en boucle")
    print("   → Vérifier les logs backend pour voir les appels de functions")

except Exception as e:
    print(f"\n✗ Erreur : {e}")

print("\n=== FIN TEST ===\n")
