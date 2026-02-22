"""
Tests unitaires pour BaseAgent.handle()
Couvre : validation messages, comportement en erreur, logs écrits.
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

# Simuler les variables d'environnement AVANT l'import
os.environ.setdefault("MISTRAL_API_KEY", "test-key-fake")
os.environ.setdefault("JARVIS_BASE_AGENT_ID", "ag_test_fake")
os.environ.setdefault("USE_MISTRAL_AGENT_API", "1")

from backend.agents.base_agent import BaseAgent, InvalidRuntimeMessageError


@pytest.fixture
def agent(tmp_path):
    """Crée un BaseAgent avec MistralClient mocké et log dans un dossier temporaire."""
    from unittest.mock import AsyncMock

    with patch("backend.agents.base_agent.MistralClient") as MockClient:
        mock_instance = MagicMock()
        mock_instance.send = AsyncMock(return_value="Réponse simulée de l'agent.")
        MockClient.return_value = mock_instance

        a = BaseAgent(
            agent_id="ag_test_fake",
            name="BASE",
            role="Assistant générique",
            description="Agent neutre de test",
        )
        a.log_file = tmp_path / "test_audit.log"
        yield a


class TestHandleValidation:
    """Tests de validation des messages d'entrée."""

    @pytest.mark.asyncio
    async def test_messages_not_a_list(self, agent):
        with pytest.raises(InvalidRuntimeMessageError, match="messages must be a list"):
            await agent.handle("pas une liste")

    @pytest.mark.asyncio
    async def test_message_not_a_dict(self, agent):
        with pytest.raises(InvalidRuntimeMessageError, match="messages\\[0\\] must be an object"):
            await agent.handle(["pas un dict"])

    @pytest.mark.asyncio
    async def test_role_invalid(self, agent):
        with pytest.raises(InvalidRuntimeMessageError, match="messages\\[0\\].role must be"):
            await agent.handle([{"role": "system", "content": "test"}])

    @pytest.mark.asyncio
    async def test_role_missing(self, agent):
        with pytest.raises(InvalidRuntimeMessageError, match="messages\\[0\\].role must be"):
            await agent.handle([{"content": "test"}])

    @pytest.mark.asyncio
    async def test_content_empty(self, agent):
        with pytest.raises(
            InvalidRuntimeMessageError, match="messages\\[0\\].content must be a non-empty string"
        ):
            await agent.handle([{"role": "user", "content": ""}])

    @pytest.mark.asyncio
    async def test_content_whitespace_only(self, agent):
        with pytest.raises(
            InvalidRuntimeMessageError, match="messages\\[0\\].content must be a non-empty string"
        ):
            await agent.handle([{"role": "user", "content": "   "}])

    @pytest.mark.asyncio
    async def test_content_not_string(self, agent):
        with pytest.raises(
            InvalidRuntimeMessageError, match="messages\\[0\\].content must be a non-empty string"
        ):
            await agent.handle([{"role": "user", "content": 123}])

    @pytest.mark.asyncio
    async def test_content_missing(self, agent):
        with pytest.raises(
            InvalidRuntimeMessageError, match="messages\\[0\\].content must be a non-empty string"
        ):
            await agent.handle([{"role": "user"}])

    @pytest.mark.asyncio
    async def test_valid_single_message(self, agent):
        result = await agent.handle([{"role": "user", "content": "Bonjour"}])
        assert result == "Réponse simulée de l'agent."

    @pytest.mark.asyncio
    async def test_valid_conversation(self, agent):
        messages = [
            {"role": "user", "content": "Bonjour"},
            {"role": "assistant", "content": "Salut"},
            {"role": "user", "content": "Comment vas-tu ?"},
        ]
        result = await agent.handle(messages)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_second_message_invalid(self, agent):
        messages = [
            {"role": "user", "content": "Bonjour"},
            {"role": "invalid", "content": "test"},
        ]
        with pytest.raises(InvalidRuntimeMessageError, match="messages\\[1\\].role must be"):
            await agent.handle(messages)


class TestAgentParameters:
    """Tests des paramètres techniques (temperature, max_tokens)."""

    def test_default_temperature_is_none(self, agent):
        assert agent.temperature is None

    def test_default_max_tokens_is_none(self, agent):
        assert agent.max_tokens is None

    def test_custom_temperature(self, tmp_path):
        with patch("backend.agents.base_agent.MistralClient") as MockClient:
            MockClient.return_value = MagicMock()
            a = BaseAgent(
                agent_id="ag_test",
                name="TEST",
                role="test",
                description="test",
                temperature=0.3,
            )
            a.log_file = tmp_path / "test.log"
            assert a.temperature == 0.3
            MockClient.assert_called_once_with(
                agent_id="ag_test",
                temperature=0.3,
                max_tokens=None,
            )

    def test_custom_max_tokens(self, tmp_path):
        with patch("backend.agents.base_agent.MistralClient") as MockClient:
            MockClient.return_value = MagicMock()
            a = BaseAgent(
                agent_id="ag_test",
                name="TEST",
                role="test",
                description="test",
                max_tokens=4096,
            )
            a.log_file = tmp_path / "test.log"
            assert a.max_tokens == 4096
            MockClient.assert_called_once_with(
                agent_id="ag_test",
                temperature=None,
                max_tokens=4096,
            )

    def test_both_parameters(self, tmp_path):
        with patch("backend.agents.base_agent.MistralClient") as MockClient:
            MockClient.return_value = MagicMock()
            a = BaseAgent(
                agent_id="ag_test",
                name="TEST",
                role="test",
                description="test",
                temperature=0.3,
                max_tokens=4096,
            )
            a.log_file = tmp_path / "test.log"
            assert a.temperature == 0.3
            assert a.max_tokens == 4096


class TestHandleState:
    """Tests de gestion d'état de l'agent."""

    @pytest.mark.asyncio
    async def test_state_idle_after_success(self, agent):
        await agent.handle([{"role": "user", "content": "test"}])
        assert agent.state == "idle"

    @pytest.mark.asyncio
    async def test_state_error_after_failure(self, agent):
        with pytest.raises(InvalidRuntimeMessageError):
            await agent.handle("pas une liste")
        assert agent.state == "error"


class TestHandleLogs:
    """Tests de journalisation."""

    @pytest.mark.asyncio
    async def test_log_handle_request_on_success(self, agent):
        await agent.handle([{"role": "user", "content": "Bonjour"}])
        logs = agent.log_file.read_text(encoding="utf-8").strip().split("\n")
        entries = [json.loads(line) for line in logs]

        request_logs = [e for e in entries if e["action"] == "handle_request"]
        assert len(request_logs) == 1
        assert request_logs[0]["agent_name"] == "BASE"
        assert request_logs[0]["details"]["message_count"] == 1

    @pytest.mark.asyncio
    async def test_log_handle_response_on_success(self, agent):
        await agent.handle([{"role": "user", "content": "Bonjour"}])
        logs = agent.log_file.read_text(encoding="utf-8").strip().split("\n")
        entries = [json.loads(line) for line in logs]

        response_logs = [e for e in entries if e["action"] == "handle_response"]
        assert len(response_logs) == 1
        assert "response_length" in response_logs[0]["details"]

    @pytest.mark.asyncio
    async def test_log_handle_error_on_failure(self, agent):
        with pytest.raises(InvalidRuntimeMessageError):
            await agent.handle("pas une liste")

        logs = agent.log_file.read_text(encoding="utf-8").strip().split("\n")
        entries = [json.loads(line) for line in logs]

        error_logs = [e for e in entries if e["action"] == "handle_error"]
        assert len(error_logs) == 1
        assert "error" in error_logs[0]["details"]
        assert "messages must be a list" in error_logs[0]["details"]["error"]

    @pytest.mark.asyncio
    async def test_log_entry_has_required_fields(self, agent):
        await agent.handle([{"role": "user", "content": "test"}])
        logs = agent.log_file.read_text(encoding="utf-8").strip().split("\n")
        entry = json.loads(logs[0])

        required_fields = [
            "timestamp",
            "agent_id",
            "agent_name",
            "session_id",
            "action",
            "state",
            "details",
        ]
        for field in required_fields:
            assert field in entry, f"Champ manquant dans le log : {field}"

    @pytest.mark.asyncio
    async def test_log_contains_session_id(self, agent):
        await agent.handle([{"role": "user", "content": "test"}], session_id="sess-123")
        logs = agent.log_file.read_text(encoding="utf-8").strip().split("\n")
        entry = json.loads(logs[0])
        assert entry["session_id"] == "sess-123"

    @pytest.mark.asyncio
    async def test_log_session_id_none_when_not_provided(self, agent):
        await agent.handle([{"role": "user", "content": "test"}])
        logs = agent.log_file.read_text(encoding="utf-8").strip().split("\n")
        entry = json.loads(logs[0])
        assert entry["session_id"] is None
