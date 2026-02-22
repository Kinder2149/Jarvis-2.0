"""
Test direct de l'agent CODEUR pour diagnostiquer pourquoi il ne génère pas de code.
"""
import asyncio
import os
from dotenv import load_dotenv
from backend.agents.agent_factory import get_agent

load_dotenv()

async def test_codeur_direct():
    """Test direct CODEUR avec instruction simple"""
    
    print("=" * 60)
    print("TEST DIRECT AGENT CODEUR")
    print("=" * 60)
    
    # Récupérer agent CODEUR
    codeur = get_agent("CODEUR")
    print(f"\n✅ Agent CODEUR chargé")
    print(f"   Agent ID: {os.getenv('JARVIS_CODEUR_AGENT_ID')}")
    
    # Instruction simple
    instruction = """Crée un fichier hello.py avec ce contenu :

# hello.py
print("Hello World")

Utilise le format de sortie obligatoire :
# hello.py
```python
print("Hello World")
```
"""
    
    print(f"\n📤 Envoi instruction ({len(instruction)} chars)...")
    print(f"   Instruction: {instruction[:100]}...")
    
    # Appeler CODEUR
    messages = [{"role": "user", "content": instruction}]
    response = await codeur.handle(messages, session_id="test-direct")
    
    print(f"\n📝 Réponse CODEUR:")
    print(f"   Longueur: {len(response)} chars")
    print(f"   Contenu complet:")
    print("-" * 60)
    print(response)
    print("-" * 60)
    
    # Analyser la réponse
    if len(response) < 200:
        print(f"\n❌ PROBLÈME: Réponse trop courte ({len(response)} chars)")
        print("   CODEUR ne génère pas le format attendu")
    elif "# hello.py" in response and "```" in response:
        print(f"\n✅ Format correct détecté")
    else:
        print(f"\n⚠️ Format incorrect - Manque marqueurs # ou ```")

if __name__ == "__main__":
    asyncio.run(test_codeur_direct())
