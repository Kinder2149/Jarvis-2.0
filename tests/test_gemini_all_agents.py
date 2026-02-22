"""
Test d'intégration Gemini - Validation TOUS les agents
Test simple pour vérifier que Gemini fonctionne avec tous les agents
"""

import os
import pytest
from dotenv import load_dotenv

from backend.agents.agent_factory import get_agent, clear_cache

load_dotenv()


@pytest.mark.asyncio
async def test_base_gemini_simple():
    """
    Test simple : BASE répond à une question basique via Gemini.
    """
    # Vérifier que la clé API est configurée
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        pytest.skip("GEMINI_API_KEY non configurée")

    # Clear cache pour forcer nouvelle instance
    clear_cache()

    # Récupérer BASE (devrait utiliser Gemini)
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
    print(f"\n✅ Réponse BASE (Gemini) : {response[:200]}...")


@pytest.mark.asyncio
async def test_codeur_gemini_simple():
    """
    Test simple : CODEUR génère du code simple via Gemini.
    """
    # Vérifier que la clé API est configurée
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        pytest.skip("GEMINI_API_KEY non configurée")

    # Clear cache
    clear_cache()

    # Récupérer CODEUR
    agent = get_agent("CODEUR")

    # Message demandant du code simple
    messages = [
        {
            "role": "user",
            "content": "Crée un fichier add.py avec une fonction add(a, b) qui retourne a + b",
        }
    ]

    # Envoyer message
    response = await agent.handle(messages)

    # Vérifications
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)
    
    # Vérifier que le code est présent
    assert "def add" in response or "add.py" in response
    assert "python" in response.lower() or "```" in response
    
    print(f"\n✅ Réponse CODEUR (Gemini) : {response[:300]}...")


@pytest.mark.asyncio
async def test_validateur_gemini_simple():
    """
    Test simple : VALIDATEUR analyse du code via Gemini.
    """
    # Vérifier que la clé API est configurée
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        pytest.skip("GEMINI_API_KEY non configurée")

    # Clear cache
    clear_cache()

    # Récupérer VALIDATEUR
    agent = get_agent("VALIDATEUR")

    # Code à valider (avec un bug volontaire)
    code_to_validate = """
# add.py
def add(a, b):
    return a + b

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
    assert "STATUT" in response or "statut" in response.lower() or "valide" in response.lower()
    
    print(f"\n✅ Réponse VALIDATEUR (Gemini) : {response[:300]}...")


@pytest.mark.asyncio
async def test_jarvis_maitre_gemini_delegation():
    """
    Test délégation : JARVIS_Maître délègue au CODEUR via Gemini.
    """
    # Vérifier que la clé API est configurée
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        pytest.skip("GEMINI_API_KEY non configurée")

    # Clear cache
    clear_cache()

    # Récupérer JARVIS_Maître
    agent = get_agent("JARVIS_Maître")

    # Message demandant du code (devrait déléguer)
    messages = [
        {
            "role": "user",
            "content": "Crée un fichier multiply.py avec une fonction multiply(a, b) qui retourne a * b",
        }
    ]

    # Envoyer message
    response = await agent.handle(messages)

    # Vérifications
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)
    
    # Vérifier que la délégation est présente
    assert "[DEMANDE_CODE_CODEUR:" in response
    
    print(f"\n✅ Délégation JARVIS_Maître (Gemini) : {response[:300]}...")
