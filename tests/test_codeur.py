"""
Tests pour l'agent CODEUR — Contrat, configuration, instanciation.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from backend.agents.agent_config import AGENT_CONFIGS, get_agent_config, list_available_agents
from backend.agents.agent_factory import clear_cache, get_agent
from backend.agents.base_agent import BaseAgent


class TestCodeurConfig:
    """Tests de configuration de l'agent CODEUR."""

    def test_codeur_exists_in_configs(self):
        assert "CODEUR" in AGENT_CONFIGS

    def test_codeur_env_var(self):
        config = get_agent_config("CODEUR")
        assert config["env_var"] == "JARVIS_CODEUR_AGENT_ID"

    def test_codeur_type_worker(self):
        config = get_agent_config("CODEUR")
        assert config["type"] == "worker"

    def test_codeur_permissions(self):
        config = get_agent_config("CODEUR")
        assert "read" in config["permissions"]
        assert "write" in config["permissions"]
        assert "code" in config["permissions"]

    def test_codeur_temperature(self):
        config = get_agent_config("CODEUR")
        assert config["temperature"] == 0.3

    def test_codeur_max_tokens(self):
        config = get_agent_config("CODEUR")
        assert config["max_tokens"] == 4096

    def test_codeur_in_list_agents(self):
        agents = list_available_agents()
        names = [a["name"] for a in agents]
        assert "CODEUR" in names

    def test_codeur_role(self):
        config = get_agent_config("CODEUR")
        assert "code" in config["role"].lower()


class TestCodeurFactory:
    """Tests d'instanciation via factory."""

    def setup_method(self):
        clear_cache()

    def teardown_method(self):
        clear_cache()

    @patch.dict(os.environ, {"JARVIS_CODEUR_AGENT_ID": "ag_test_codeur_123"})
    @patch("backend.agents.agent_factory.BaseAgent")
    def test_factory_creates_codeur(self, MockBaseAgent):
        mock_instance = MagicMock(spec=BaseAgent)
        MockBaseAgent.return_value = mock_instance

        agent = get_agent("CODEUR")
        assert agent is not None
        MockBaseAgent.assert_called_once()

    @patch.dict(os.environ, {"JARVIS_CODEUR_AGENT_ID": "ag_test_codeur_123"})
    @patch("backend.agents.agent_factory.BaseAgent")
    def test_factory_passes_correct_agent_id(self, MockBaseAgent):
        mock_instance = MagicMock(spec=BaseAgent)
        MockBaseAgent.return_value = mock_instance

        get_agent("CODEUR")
        call_kwargs = MockBaseAgent.call_args
        assert call_kwargs.kwargs["agent_id"] == "ag_test_codeur_123"

    @patch.dict(os.environ, {"JARVIS_CODEUR_AGENT_ID": "ag_test_codeur_123"})
    @patch("backend.agents.agent_factory.BaseAgent")
    def test_factory_passes_temperature(self, MockBaseAgent):
        mock_instance = MagicMock(spec=BaseAgent)
        MockBaseAgent.return_value = mock_instance

        get_agent("CODEUR")
        call_kwargs = MockBaseAgent.call_args
        assert call_kwargs.kwargs["temperature"] == 0.3

    @patch.dict(os.environ, {"JARVIS_CODEUR_AGENT_ID": "ag_test_codeur_123"})
    @patch("backend.agents.agent_factory.BaseAgent")
    def test_factory_passes_code_permission(self, MockBaseAgent):
        mock_instance = MagicMock(spec=BaseAgent)
        MockBaseAgent.return_value = mock_instance

        get_agent("CODEUR")
        call_kwargs = MockBaseAgent.call_args
        assert "code" in call_kwargs.kwargs["permissions"]

    def test_factory_raises_without_env_var(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("JARVIS_CODEUR_AGENT_ID", None)
            with pytest.raises(RuntimeError, match="JARVIS_CODEUR_AGENT_ID"):
                get_agent("CODEUR")

    @patch.dict(os.environ, {"JARVIS_CODEUR_AGENT_ID": "ag_test_codeur_123"})
    @patch("backend.agents.agent_factory.BaseAgent")
    def test_factory_caches_codeur(self, MockBaseAgent):
        mock_instance = MagicMock(spec=BaseAgent)
        MockBaseAgent.return_value = mock_instance

        agent1 = get_agent("CODEUR")
        agent2 = get_agent("CODEUR")
        assert agent1 is agent2
        assert MockBaseAgent.call_count == 1
