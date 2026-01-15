import logging
import os

from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

logger = logging.getLogger(__name__)

class MistralClient:
    """
    Client bas niveau responsable uniquement de la communication avec Mistral.
    Aucune logique d’agent ici.
    """

    def __init__(self, agent_id: str):
        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError("MISTRAL_API_KEY manquante dans .env")

        self.agent_id = agent_id
        self.client = Mistral(api_key=api_key)
        self.use_agent_api = os.environ.get("USE_MISTRAL_AGENT_API", "0") == "1"

    def send(self, messages: list[dict]) -> str:
        if self.use_agent_api:
            try:
                response = self.client.beta.conversations.start(
                    agent_id=self.agent_id,
                    inputs=messages,
                )
                return response.output_text
            except Exception:
                logger.exception(
                    "Mistral beta.conversations.start failed for agent_id=%s; falling back to chat completion.",
                    self.agent_id,
                )

        model = os.environ.get("MISTRAL_MODEL", "mistral-small-latest")
        response = self.client.chat.complete(
            model=model,
            messages=messages,
        )
        if getattr(response, "choices", None):
            message = response.choices[0].message
            content = getattr(message, "content", None)
            if isinstance(content, str) and content.strip():
                return content
        raise RuntimeError("Unexpected response format from Mistral chat completion")