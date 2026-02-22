"""
Tests unitaires pour les providers LLM
Validation de l'abstraction et des implémentations
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from backend.ia.providers.base_provider import BaseProvider
from backend.ia.providers.gemini_provider import GeminiProvider
from backend.ia.providers.provider_factory import ProviderFactory


class TestBaseProvider:
    """Tests de l'interface BaseProvider"""

    def test_validate_messages_valid(self):
        """Validation de messages valides"""
        provider = MagicMock(spec=BaseProvider)
        provider.validate_messages = BaseProvider.validate_messages.__get__(provider)

        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
        ]

        provider.validate_messages(messages)

    def test_validate_messages_invalid_role(self):
        """Validation échoue avec rôle invalide"""
        provider = MagicMock(spec=BaseProvider)
        provider.validate_messages = BaseProvider.validate_messages.__get__(provider)

        messages = [{"role": "invalid", "content": "Hello"}]

        with pytest.raises(ValueError, match="role must be"):
            provider.validate_messages(messages)

    def test_validate_messages_not_list(self):
        """Validation échoue si messages n'est pas une liste"""
        provider = MagicMock(spec=BaseProvider)
        provider.validate_messages = BaseProvider.validate_messages.__get__(provider)

        with pytest.raises(ValueError, match="must be a list"):
            provider.validate_messages("not a list")


class TestGeminiProvider:
    """Tests du provider Gemini"""

    def test_format_functions(self):
        """Conversion fonctions JARVIS → Gemini"""
        provider = GeminiProvider(api_key="test_key", model="gemini-1.5-flash")

        functions = [
            {
                "name": "get_file",
                "description": "Get a file",
                "parameters": {
                    "type": "object",
                    "properties": {"path": {"type": "string"}},
                    "required": ["path"],
                },
            }
        ]

        gemini_functions = provider.format_functions(functions)

        assert len(gemini_functions) == 1
        assert gemini_functions[0].name == "get_file"
        assert gemini_functions[0].description == "Get a file"

    def test_convert_schema_to_gemini(self):
        """Conversion JSON Schema → Gemini Schema"""
        provider = GeminiProvider(api_key="test_key", model="gemini-1.5-flash")

        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name"},
                "age": {"type": "integer"},
            },
            "required": ["name"],
        }

        gemini_schema = provider._convert_schema_to_gemini(schema)

        assert gemini_schema["type"] == "OBJECT"
        assert "properties" in gemini_schema
        assert gemini_schema["properties"]["name"]["type"] == "STRING"
        assert gemini_schema["properties"]["age"]["type"] == "INTEGER"

    @pytest.mark.asyncio
    async def test_send_message_mock(self):
        """Test envoi message avec mock"""
        with patch("google.generativeai.GenerativeModel") as mock_model:
            mock_chat = AsyncMock()
            mock_response = MagicMock()
            mock_response.candidates = [
                MagicMock(
                    content=MagicMock(parts=[MagicMock(text="Hello from Gemini")])
                )
            ]
            mock_chat.send_message_async.return_value = mock_response
            mock_model.return_value.start_chat.return_value = mock_chat

            provider = GeminiProvider(api_key="test_key", model="gemini-1.5-flash")

            messages = [{"role": "user", "content": "Hello"}]
            response = await provider.send_message(messages)

            assert response["content"] == "Hello from Gemini"
            assert response["finish_reason"] == "stop"


class TestProviderFactory:
    """Tests de la factory"""

    def test_create_gemini(self, monkeypatch):
        """Création provider Gemini"""
        monkeypatch.setenv("JARVIS_MAITRE_PROVIDER", "gemini")
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        monkeypatch.setenv("JARVIS_MAITRE_MODEL", "gemini-2.5-pro")

        ProviderFactory.clear_cache()
        provider = ProviderFactory.create("JARVIS_Maître")

        assert isinstance(provider, GeminiProvider)
        assert provider.model == "gemini-2.5-pro"


    def test_cache_works(self, monkeypatch):
        """Vérification que le cache fonctionne"""
        monkeypatch.setenv("BASE_PROVIDER", "gemini")
        monkeypatch.setenv("GEMINI_API_KEY", "test_key")
        monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-pro")

        ProviderFactory.clear_cache()
        provider1 = ProviderFactory.create("BASE")
        provider2 = ProviderFactory.create("BASE")

        assert provider1 is provider2



