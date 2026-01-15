import os

from backend.agents.base_agent import BaseAgent

_BASE_AGENT = None


def get_base_agent() -> BaseAgent:
    """
    Fournit l’instance unique de l’agent de base.
    Prépare le terrain pour le multi-agent sans l’activer.
    """
    global _BASE_AGENT

    if _BASE_AGENT is None:
        agent_id = os.environ.get("JARVIS_BASE_AGENT_ID")
        if not agent_id:
            raise RuntimeError(
                "JARVIS_BASE_AGENT_ID manquante dans l'environnement"
            )
        _BASE_AGENT = BaseAgent(
            agent_id=agent_id,
            name="Agent de Base",
            role="Assistant générique",
            description="Agent neutre servant de modèle pour tous les futurs agents.",
            system_prompt=(
                "Tu es un agent IA générique, neutre et professionnel. "
                "Tu réponds uniquement dans ton périmètre. "
                "Si une information est incertaine ou inconnue, tu le dis explicitement. "
                "Tu ne prends aucune décision système et ne sors jamais de ton rôle."
            ),
        )

    return _BASE_AGENT