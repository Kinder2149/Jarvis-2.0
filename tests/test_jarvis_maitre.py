"""
Tests pour JARVIS_Maître et endpoints API associés.
Couvre : non-régression BASE, contrat JARVIS_Maître, /select_agent, /chat active_agent.
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

os.environ.setdefault("MISTRAL_API_KEY", "test-key-fake")
os.environ.setdefault("JARVIS_BASE_AGENT_ID", "ag_test_fake")
os.environ.setdefault("USE_MISTRAL_AGENT_API", "1")

from backend.agents.base_agent import BaseAgent, InvalidRuntimeMessageError
from backend.agents.jarvis_maitre import JarvisMaitre


@pytest.fixture
def jarvis(tmp_path):
    """Crée un JarvisMaitre avec MistralClient mocké."""
    from unittest.mock import AsyncMock

    with patch("backend.agents.base_agent.MistralClient") as MockClient:
        mock_instance = MagicMock()
        mock_instance.send = AsyncMock(return_value="Réponse de JARVIS_Maître.")
        MockClient.return_value = mock_instance

        agent = JarvisMaitre(agent_id="ag_test_fake")
        agent.log_file = tmp_path / "test_audit.log"
        yield agent


class TestJarvisMaitreContrat:
    """Vérifie que le contrat JARVIS_Maître est respecté."""

    def test_inherits_base_agent(self, jarvis):
        assert isinstance(jarvis, BaseAgent)

    def test_name(self, jarvis):
        assert jarvis.name == "JARVIS_Maître"

    def test_role(self, jarvis):
        assert jarvis.role == "Assistant personnel principal"

    def test_permissions_include_orchestrate(self, jarvis):
        assert "orchestrate" in jarvis.permissions

    def test_permissions_include_read_write(self, jarvis):
        assert "read" in jarvis.permissions
        assert "write" in jarvis.permissions

    def test_description_not_empty(self, jarvis):
        assert len(jarvis.description) > 0


class TestJarvisMaitreParameters:
    """Tests des paramètres techniques (temperature, max_tokens)."""

    def test_default_temperature_is_none(self, jarvis):
        assert jarvis.temperature is None

    def test_default_max_tokens_is_none(self, jarvis):
        assert jarvis.max_tokens is None

    def test_custom_temperature(self, tmp_path):
        with patch("backend.agents.base_agent.MistralClient") as MockClient:
            MockClient.return_value = MagicMock()
            agent = JarvisMaitre(agent_id="ag_test", temperature=0.3)
            agent.log_file = tmp_path / "test.log"
            assert agent.temperature == 0.3

    def test_custom_max_tokens(self, tmp_path):
        with patch("backend.agents.base_agent.MistralClient") as MockClient:
            MockClient.return_value = MagicMock()
            agent = JarvisMaitre(agent_id="ag_test", max_tokens=4096)
            agent.log_file = tmp_path / "test.log"
            assert agent.max_tokens == 4096

    def test_parameters_propagated_to_client(self, tmp_path):
        with patch("backend.agents.base_agent.MistralClient") as MockClient:
            MockClient.return_value = MagicMock()
            JarvisMaitre(agent_id="ag_test", temperature=0.3, max_tokens=4096)
            MockClient.assert_called_once_with(
                agent_id="ag_test",
                temperature=0.3,
                max_tokens=4096,
            )


class TestJarvisMaitreNonRegression:
    """JARVIS_Maître ne casse pas le comportement hérité de BaseAgent."""

    @pytest.mark.asyncio
    async def test_handle_valid_message(self, jarvis):
        result = await jarvis.handle([{"role": "user", "content": "Bonjour JARVIS"}])
        assert result == "Réponse de JARVIS_Maître."

    @pytest.mark.asyncio
    async def test_handle_rejects_invalid_messages(self, jarvis):
        with pytest.raises(InvalidRuntimeMessageError):
            await jarvis.handle("pas une liste")

    @pytest.mark.asyncio
    async def test_handle_rejects_empty_content(self, jarvis):
        with pytest.raises(InvalidRuntimeMessageError):
            await jarvis.handle([{"role": "user", "content": ""}])

    @pytest.mark.asyncio
    async def test_state_idle_after_success(self, jarvis):
        await jarvis.handle([{"role": "user", "content": "test"}])
        assert jarvis.state == "idle"

    @pytest.mark.asyncio
    async def test_state_error_after_failure(self, jarvis):
        with pytest.raises(InvalidRuntimeMessageError):
            await jarvis.handle("invalide")
        assert jarvis.state == "error"

    @pytest.mark.asyncio
    async def test_logs_written(self, jarvis):
        await jarvis.handle([{"role": "user", "content": "test"}], session_id="sess-jm")
        logs = jarvis.log_file.read_text(encoding="utf-8").strip().split("\n")
        entries = [json.loads(line) for line in logs]

        assert any(e["action"] == "handle_request" for e in entries)
        assert any(e["action"] == "handle_response" for e in entries)
        assert all(e["agent_name"] == "JARVIS_Maître" for e in entries)
        assert all(e["session_id"] == "sess-jm" for e in entries)


# --- Tests API (endpoint /agents) ---

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Client de test FastAPI avec MistralClient mocké."""
    with patch("backend.agents.base_agent.MistralClient") as MockClient:
        mock_instance = MagicMock()
        mock_instance.send.return_value = "Réponse API simulée."
        MockClient.return_value = mock_instance

        from backend.agents import agent_factory

        agent_factory.clear_cache()

        from backend.app import app

        with TestClient(app) as c:
            yield c

        agent_factory.clear_cache()


class TestAgentsEndpoint:
    """Tests de l'endpoint GET /agents."""

    def test_list_agents(self, client):
        resp = client.get("/agents")
        assert resp.status_code == 200
        agents = resp.json()["agents"]
        assert len(agents) == 2
        ids = [a["id"] for a in agents]
        assert "BASE" in ids
        assert "JARVIS_Maître" in ids

    def test_jarvis_maitre_metadata(self, client):
        resp = client.get("/agents")
        agents = resp.json()["agents"]
        jm = next(a for a in agents if a["id"] == "JARVIS_Maître")
        assert jm["role"] == "Assistant personnel principal"
        assert "Val C" in jm["description"]
