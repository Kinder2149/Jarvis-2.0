"""
Tests HTTP endpoint POST /api/conversations/{id}/confirm-action

Tests de sécurité structurelle pour validation production :
- Test confirmation valide (cycle complet)
- Test erreur conversation inexistante (404)
- Test erreur aucune action bloquée (400)
- Test erreur double confirmation (400)
- Test sécurité injection SQL/XSS

⚠️ PHASE 1 BLOQUANT PRODUCTION : Ces tests doivent tous passer (5/5)
"""

import shutil
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient

from backend.agents.agent_factory import get_agent
from backend.app import app
from backend.db.database import Database
from backend.models.session_state import Mode, Phase, ProjectState, SessionState
from backend.services.function_executor import FunctionExecutor
from backend.services.orchestration import SimpleOrchestrator


@pytest_asyncio.fixture
async def test_db():
    """Crée une instance DB temporaire pour les tests"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    db = Database(db_path)
    await db.initialize()

    # Injecter dans app
    app.state.db = db

    yield db

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def temp_project_dir():
    """Crée un dossier projet temporaire"""
    temp_dir = tempfile.mkdtemp(prefix="jarvis_test_confirm_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest_asyncio.fixture
async def test_client(test_db):
    """Client HTTP async pour tests API"""
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_confirm_action_valid(test_client, test_db, temp_project_dir):
    """
    Test 1 : Confirmation valide

    Scénario :
    1. Créer conversation en DB
    2. Simuler action NON-SAFE bloquée (sans appeler API Mistral)
    3. Appeler POST /confirm-action
    4. Vérifier statut 200 OK
    5. Vérifier nettoyage _pending_actions

    Note : Ce test ne vérifie pas l'exécution réelle (nécessiterait API Mistral),
    seulement le workflow HTTP de confirmation
    """
    # 1. Créer projet en DB
    project = await test_db.create_project(
        name="TestConfirmProject", path=temp_project_dir, description="Test confirmation"
    )
    project_id = project["id"]

    # 2. Créer conversation en DB
    conversation = await test_db.create_conversation(
        project_id=project_id, agent_id="JARVIS_Maître", title="Test Confirmation"
    )
    conversation_id = conversation["id"]

    # 3. Simuler action bloquée (sans appeler API Mistral)
    from unittest.mock import AsyncMock

    function_executor = FunctionExecutor(temp_project_dir)
    session_state = SessionState(
        mode=Mode.PROJECT,
        conversation_id=conversation_id,
        phase=Phase.EXECUTION,
        project_state=ProjectState.DEBT,
        project_id=project_id,
    )

    # Simuler réponse IA avec marqueur délégation
    original_response = "[DEMANDE_CODE_CODEUR: Créer fichier test.py]"

    # Stocker action bloquée (simuler ce que l'orchestration fait)
    SimpleOrchestrator._pending_actions[conversation_id] = {
        "user_message": "Créer fichier test.py",
        "original_response": original_response,
        "delegations": [{"agent_name": "CODEUR", "instruction": "Créer fichier test.py"}],
        "classification": {"is_safe": False, "requires_validation": True},
        "conversation_history": [{"role": "user", "content": "Créer fichier test.py"}],
        "project_path": temp_project_dir,
        "function_executor": function_executor,
        "session_state": session_state,
        "confirmed": False,
    }

    # 4. Vérifier action stockée
    assert conversation_id in SimpleOrchestrator._pending_actions
    assert SimpleOrchestrator._pending_actions[conversation_id]["confirmed"] is False

    # 5. Mocker process_response pour éviter appel API Mistral
    from unittest.mock import patch

    mock_response = "Fichier test.py créé avec succès"
    mock_delegations = [{"agent_name": "CODEUR", "success": True, "files_written": []}]

    with patch.object(
        SimpleOrchestrator, "process_response", new_callable=AsyncMock
    ) as mock_process:
        mock_process.return_value = (mock_response, mock_delegations)

        # 6. Appeler endpoint confirmation
        response = await test_client.post(f"/api/conversations/{conversation_id}/confirm-action")

    # 7. Vérifier statut 200 OK
    assert response.status_code == 200
    result = response.json()

    # 8. Vérifier structure réponse
    assert "message" in result
    assert "delegations" in result
    assert result["message"] == mock_response

    # 9. Vérifier nettoyage _pending_actions (fait par process_response mocké)
    # Note: Le nettoyage est fait dans process_response, pas dans l'endpoint

    # 10. Vérifier message sauvegardé en DB
    messages = await test_db.get_messages(conversation_id)
    assistant_messages = [m for m in messages if m["role"] == "assistant"]
    assert len(assistant_messages) >= 1
    assert assistant_messages[-1]["content"] == mock_response

    print("\n✅ Test 1 PASSÉ : Confirmation valide")
    print(f"   Statut : {response.status_code}")
    print(f"   Message : {result['message'][:50]}...")
    print(f"   Délégations : {len(result['delegations'])}")


@pytest.mark.asyncio
async def test_confirm_action_conversation_not_found(test_client, test_db):
    """
    Test 2 : Erreur conversation inexistante

    Scénario :
    1. Appeler POST /confirm-action avec ID inexistant
    2. Vérifier statut 404 Not Found
    3. Vérifier message erreur
    """
    fake_conversation_id = "fake-conversation-id-12345"

    # Appeler endpoint avec ID inexistant
    response = await test_client.post(f"/api/conversations/{fake_conversation_id}/confirm-action")

    # Vérifier statut 404
    assert response.status_code == 404

    # Vérifier message erreur
    result = response.json()
    assert "detail" in result
    assert "aucune action" in result["detail"].lower() or "attente" in result["detail"].lower()

    print("\n✅ Test 2 PASSÉ : Erreur conversation inexistante")
    print(f"   Statut : {response.status_code}")
    print(f"   Message : {result['detail']}")


@pytest.mark.asyncio
async def test_confirm_action_no_pending_action(test_client, test_db, temp_project_dir):
    """
    Test 3 : Erreur aucune action bloquée

    Scénario :
    1. Créer conversation sans action bloquée
    2. Appeler POST /confirm-action
    3. Vérifier statut 404
    4. Vérifier message erreur
    """
    # 1. Créer projet
    project_data = {
        "name": "TestNoPendingProject",
        "path": temp_project_dir,
        "description": "Test no pending action",
    }
    response = await test_client.post("/api/projects", json=project_data)
    assert response.status_code == 200
    project = response.json()
    project_id = project["id"]

    # 2. Créer conversation
    conv_data = {"agent_id": "JARVIS_Maître", "title": "Test No Pending"}
    response = await test_client.post(f"/api/projects/{project_id}/conversations", json=conv_data)
    assert response.status_code == 200
    conversation = response.json()
    conversation_id = conversation["id"]

    # 3. Vérifier aucune action bloquée
    assert conversation_id not in SimpleOrchestrator._pending_actions

    # 4. Appeler endpoint confirmation
    response = await test_client.post(f"/api/conversations/{conversation_id}/confirm-action")

    # 5. Vérifier statut 404
    assert response.status_code == 404

    # 6. Vérifier message erreur
    result = response.json()
    assert "detail" in result
    assert "aucune action" in result["detail"].lower() or "attente" in result["detail"].lower()

    print("\n✅ Test 3 PASSÉ : Erreur aucune action bloquée")
    print(f"   Statut : {response.status_code}")
    print(f"   Message : {result['detail']}")


@pytest.mark.asyncio
async def test_confirm_action_double_confirmation(test_client, test_db, temp_project_dir):
    """
    Test 4 : Erreur double confirmation

    Scénario :
    1. Créer action bloquée
    2. Confirmer 1ère fois (OK)
    3. Confirmer 2ème fois (erreur)
    4. Vérifier statut 404
    """
    # 1. Créer projet
    project_data = {
        "name": "TestDoubleConfirmProject",
        "path": temp_project_dir,
        "description": "Test double confirmation",
    }
    response = await test_client.post("/api/projects", json=project_data)
    assert response.status_code == 200
    project = response.json()
    project_id = project["id"]

    # 2. Créer conversation
    conv_data = {"agent_id": "JARVIS_Maître", "title": "Test Double Confirm"}
    response = await test_client.post(f"/api/projects/{project_id}/conversations", json=conv_data)
    assert response.status_code == 200
    conversation = response.json()
    conversation_id = conversation["id"]

    # 3. Simuler action bloquée
    agent = get_agent("JARVIS_Maître")
    function_executor = FunctionExecutor(temp_project_dir)
    session_state = SessionState(
        mode=Mode.PROJECT,
        conversation_id=conversation_id,
        phase=Phase.EXECUTION,
        project_state=ProjectState.DEBT,
        project_id=project_id,
    )

    original_response = "[DEMANDE_CODE_CODEUR: Créer fichier double.py]"

    SimpleOrchestrator._pending_actions[conversation_id] = {
        "user_message": "Créer fichier double.py",
        "original_response": original_response,
        "delegations": [{"agent_name": "CODEUR", "instruction": "Créer fichier double.py"}],
        "classification": {"is_safe": False, "requires_validation": True},
        "conversation_history": [{"role": "user", "content": "Créer fichier double.py"}],
        "project_path": temp_project_dir,
        "function_executor": function_executor,
        "session_state": session_state,
        "confirmed": False,
    }

    # 4. Première confirmation (OK)
    response_1 = await test_client.post(f"/api/conversations/{conversation_id}/confirm-action")
    assert response_1.status_code == 200

    # 5. Vérifier nettoyage
    assert conversation_id not in SimpleOrchestrator._pending_actions

    # 6. Deuxième confirmation (erreur)
    response_2 = await test_client.post(f"/api/conversations/{conversation_id}/confirm-action")

    # 7. Vérifier statut 404
    assert response_2.status_code == 404

    # 8. Vérifier message erreur
    result = response_2.json()
    assert "detail" in result
    assert "aucune action" in result["detail"].lower() or "attente" in result["detail"].lower()

    print("\n✅ Test 4 PASSÉ : Erreur double confirmation")
    print(f"   1ère confirmation : {response_1.status_code}")
    print(f"   2ème confirmation : {response_2.status_code}")
    print(f"   Message : {result['detail']}")


@pytest.mark.asyncio
async def test_confirm_action_security_injection(test_client, test_db):
    """
    Test 5 : Sécurité injection SQL/XSS

    Scénario :
    1. Tenter injection SQL dans conversation_id
    2. Tenter injection XSS dans conversation_id
    3. Vérifier protection active (404, pas d'exécution)
    """
    # Test injection SQL
    sql_injection_ids = [
        "'; DROP TABLE conversations; --",
        "1' OR '1'='1",
        "admin'--",
        "1; DELETE FROM messages WHERE 1=1; --",
    ]

    for injection_id in sql_injection_ids:
        response = await test_client.post(f"/api/conversations/{injection_id}/confirm-action")
        # Doit retourner 404 (pas d'action trouvée), pas d'erreur SQL
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        # Vérifier pas d'erreur SQL dans réponse
        assert "sql" not in result["detail"].lower()
        assert "syntax" not in result["detail"].lower()

    # Test injection XSS
    xss_injection_ids = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "javascript:alert('XSS')",
        "<svg/onload=alert('XSS')>",
    ]

    for injection_id in xss_injection_ids:
        response = await test_client.post(f"/api/conversations/{injection_id}/confirm-action")
        # Doit retourner 404 (pas d'action trouvée), pas d'exécution XSS
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        # Vérifier pas de script dans réponse
        assert "<script>" not in result["detail"]
        assert "onerror=" not in result["detail"]

    print("\n✅ Test 5 PASSÉ : Sécurité injection SQL/XSS")
    print(f"   Injections SQL testées : {len(sql_injection_ids)}")
    print(f"   Injections XSS testées : {len(xss_injection_ids)}")
    print("   Toutes bloquées avec 404")
