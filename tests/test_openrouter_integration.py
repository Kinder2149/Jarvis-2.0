"""
Test d'intégration OpenRouter - Validation BASE/CODEUR/VALIDATEUR
Test simple pour vérifier qu'OpenRouter fonctionne avec les agents workers
"""

import os
import pytest
from dotenv import load_dotenv

from backend.agents.agent_factory import get_agent, clear_cache

load_dotenv()


@pytest.mark.asyncio
async def test_base_openrouter_simple():
    """
    Test simple : BASE répond à une question basique via OpenRouter.
    """
    # Vérifier que les clés API sont configurées
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        pytest.skip("OPENROUTER_API_KEY non configurée")

    # Clear cache pour forcer nouvelle instance
    clear_cache()

    # Récupérer BASE (devrait utiliser OpenRouter)
    agent = get_agent("BASE")

    # Message simple
    messages = [{"role": "user", "content": "Bonjour, qui es-tu ?"}]

    # Envoyer message
    response = await agent.handle(messages)

    # Vérifications
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)
    assert "BASE" in response or "base" in response.lower()
    print(f"\n✅ Réponse BASE (OpenRouter) : {response[:200]}...")


@pytest.mark.asyncio
async def test_codeur_openrouter_simple():
    """
    Test simple : CODEUR génère du code simple via OpenRouter.
    """
    # Vérifier que les clés API sont configurées
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        pytest.skip("OPENROUTER_API_KEY non configurée")

    # Clear cache
    clear_cache()

    # Récupérer CODEUR
    agent = get_agent("CODEUR")

    # Message demandant du code simple
    messages = [
        {
            "role": "user",
            "content": "Crée un fichier hello.py avec une fonction hello(name) qui retourne 'Hello, {name}!'",
        }
    ]

    # Envoyer message
    response = await agent.handle(messages)

    # Vérifications
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)
    
    # Vérifier que le code est présent
    assert "def hello" in response or "hello.py" in response
    assert "python" in response.lower() or "```" in response
    
    print(f"\n✅ Réponse CODEUR (OpenRouter) : {response[:300]}...")


@pytest.mark.asyncio
async def test_validateur_openrouter_simple():
    """
    Test simple : VALIDATEUR analyse du code via OpenRouter.
    """
    # Vérifier que les clés API sont configurées
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    if not openrouter_key:
        pytest.skip("OPENROUTER_API_KEY non configurée")

    # Clear cache
    clear_cache()

    # Récupérer VALIDATEUR
    agent = get_agent("VALIDATEUR")

    # Code à valider (avec un bug volontaire)
    code_to_validate = """
# hello.py
def hello(name):
    return f'Hello, {name}'

# Pas de tests
"""

    messages = [
        {
            "role": "user",
            "content": f"Valide ce code :\n{code_to_validate}",
        }
    ]

    # Envoyer message
    response = await agent.handle(messages)

    # Vérifications
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)
    
    # Vérifier que le format de réponse est respecté
    assert "STATUT" in response or "statut" in response.lower()
    
    print(f"\n✅ Réponse VALIDATEUR (OpenRouter) : {response[:300]}...")
