"""
Test d'intégration Gemini - Validation JARVIS_Maître
Test simple pour vérifier que Gemini fonctionne avec tool calling
"""

import os
import pytest
from dotenv import load_dotenv

from backend.agents.agent_factory import get_agent, clear_cache
from backend.services.function_executor import FunctionExecutor
from backend.db.database import Database

load_dotenv()


@pytest.mark.asyncio
async def test_jarvis_maitre_gemini_simple():
    """
    Test simple : JARVIS_Maître répond à une question basique.
    Pas de tool calling, juste validation que Gemini fonctionne.
    """
    # Vérifier que les clés API sont configurées
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        pytest.skip("GEMINI_API_KEY non configurée")

    # Clear cache pour forcer nouvelle instance
    clear_cache()

    # Récupérer JARVIS_Maître (devrait utiliser Gemini)
    agent = get_agent("JARVIS_Maître")

    # Message simple
    messages = [{"role": "user", "content": "Bonjour, qui es-tu ?"}]

    # Envoyer message
    response = await agent.handle(messages)

    # Vérifications
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)
    print(f"\n✅ Réponse Gemini : {response[:200]}...")


@pytest.mark.asyncio
async def test_jarvis_maitre_gemini_with_tools():
    """
    Test avec tool calling : JARVIS_Maître utilise get_project_structure.
    Validation que le tool calling Gemini fonctionne.
    """
    # Vérifier que les clés API sont configurées
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        pytest.skip("GEMINI_API_KEY non configurée")

    # Clear cache
    clear_cache()

    # Créer database et function executor
    db = Database(":memory:")

    # Utiliser le dossier du projet comme contexte
    project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    function_executor = FunctionExecutor(db, project_path=project_path)

    # Récupérer JARVIS_Maître
    agent = get_agent("JARVIS_Maître")

    # Message demandant la structure du projet
    messages = [
        {
            "role": "user",
            "content": "Donne-moi la structure du projet (dossiers principaux uniquement, max_depth=1)",
        }
    ]

    # Envoyer message avec function_executor
    response = await agent.handle(messages, function_executor=function_executor)

    # Vérifications
    assert response is not None
    assert len(response) > 0
    assert isinstance(response, str)

    # Vérifier que la réponse mentionne des dossiers du projet
    assert any(
        folder in response.lower()
        for folder in ["backend", "frontend", "tests", "docs", "config"]
    )

    print(f"\n✅ Réponse avec tool calling : {response[:300]}...")


@pytest.mark.asyncio
async def test_jarvis_maitre_delegation_marker():
    """
    Test délégation : JARVIS_Maître doit utiliser le marqueur [DEMANDE_CODE_CODEUR:].
    Validation que le prompt fonctionne correctement.
    """
    # Vérifier que les clés API sont configurées
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        pytest.skip("GEMINI_API_KEY non configurée")

    # Clear cache
    clear_cache()

    # Récupérer JARVIS_Maître
    agent = get_agent("JARVIS_Maître")

    # Message demandant du code
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

    # Vérifier que le marqueur de délégation est présent
    assert "[DEMANDE_CODE_CODEUR:" in response

    print(f"\n✅ Délégation détectée : {response[:300]}...")
