"""Vérifier résultat du test live"""
import requests

conversation_id = "d1d06375-3744-4727-9c0e-b5eaa50bb15e"
r = requests.get(f"http://localhost:8000/api/conversations/{conversation_id}/messages")

if r.status_code == 200:
    msgs = r.json()
    print(f"Messages: {len(msgs)}")
    for msg in msgs:
        print(f"\n{'='*60}")
        print(f"Role: {msg.get('role')}")
        print(f"Content: {msg.get('content')}")
else:
    print(f"Erreur: {r.status_code}")
