from backend.ia.mistral_client import MistralClient


class InvalidRuntimeMessageError(ValueError):
    pass


class BaseAgent:
    """
    Implémentation concrète du modèle d’agent de base.

    Responsabilités :
    - appliquer un rôle stable
    - consommer un contexte
    - produire une réponse textuelle
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        description: str,
        system_prompt: str,
    ):
        self.id = agent_id
        self.name = name
        self.role = role
        self.description = description
        self.system_prompt = system_prompt

        self.client = MistralClient(agent_id=agent_id)

    def handle(self, messages: list[dict]) -> str:
        """
        Point d’entrée unique de l’agent.
        """

        if not isinstance(messages, list):
            raise InvalidRuntimeMessageError("messages must be a list")

        validated_messages: list[dict] = []
        for idx, msg in enumerate(messages):
            if not isinstance(msg, dict):
                raise InvalidRuntimeMessageError(
                    f"messages[{idx}] must be an object"
                )

            role = msg.get("role")
            content = msg.get("content")

            if role != "user":
                raise InvalidRuntimeMessageError(
                    f"messages[{idx}].role must be 'user'"
                )
            if not isinstance(content, str) or not content.strip():
                raise InvalidRuntimeMessageError(
                    f"messages[{idx}].content must be a non-empty string"
                )

            validated_messages.append({"role": "user", "content": content})

        return self.client.send(validated_messages)