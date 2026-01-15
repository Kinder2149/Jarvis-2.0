import logging
import os

from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

logger = logging.getLogger(__name__)

class MistralUpstreamError(RuntimeError):
    pass

class MistralResponseFormatError(RuntimeError):
    pass

class MistralClient:
    """
    Client bas niveau responsable uniquement de la communication avec Mistral.
    Aucune logique d’agent ici.
    """

    def _extract_text_from_conversation_response(self, response) -> str | None:
        outputs = getattr(response, "outputs", None)
        if not isinstance(outputs, list):
            return None

        for output in outputs:
            output_type = getattr(output, "type", None)
            if output_type != "message.output":
                continue

            content = getattr(output, "content", None)
            if isinstance(content, str):
                if content.strip():
                    return content
                continue

            if isinstance(content, list):
                parts: list[str] = []
                for chunk in content:
                    chunk_type = getattr(chunk, "type", None)
                    if chunk_type == "text":
                        text = getattr(chunk, "text", None)
                        if isinstance(text, str) and text:
                            parts.append(text)
                text_out = "".join(parts).strip()
                if text_out:
                    return text_out

        return None

    def __init__(self, agent_id: str):
        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            raise RuntimeError("MISTRAL_API_KEY manquante dans .env")

        self.agent_id = agent_id
        self.client = Mistral(api_key=api_key)
        self.use_agent_api = os.environ.get("USE_MISTRAL_AGENT_API", "0") == "1"
        if not self.use_agent_api:
            raise RuntimeError(
                "USE_MISTRAL_AGENT_API must be set to '1' (Mistral Agent API is mandatory)"
            )

    def send(self, messages: list[dict]) -> str:
        try:
            response = self.client.beta.conversations.start(
                agent_id=self.agent_id,
                inputs=messages,
            )
            output_text = self._extract_text_from_conversation_response(response)
            if isinstance(output_text, str) and output_text.strip():
                return output_text
            raise MistralResponseFormatError(
                "Unexpected response format from Mistral agent conversation start"
            )
        except MistralResponseFormatError:
            raise
        except Exception as e:
            logger.exception(
                "Mistral beta.conversations.start failed for agent_id=%s",
                self.agent_id,
            )
            raise MistralUpstreamError("Mistral agent API call failed") from e