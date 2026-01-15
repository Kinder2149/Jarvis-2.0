from backend.ia.mistral_client import MistralClient


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

        full_context = [
            {"role": "system", "content": self.system_prompt},
            *messages,
        ]

        return self.client.send(full_context)