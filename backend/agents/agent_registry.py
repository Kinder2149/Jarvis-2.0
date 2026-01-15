from backend.agents.base_agent import BaseAgent

_BASE_AGENT = None


def get_base_agent() -> BaseAgent:
    """
    Fournit l’instance unique de l’agent de base.
    Prépare le terrain pour le multi-agent sans l’activer.
    """
    global _BASE_AGENT

    if _BASE_AGENT is None:
        _BASE_AGENT = BaseAgent(
            agent_id="ag_019ba8ca8eaa76288371e13fb962d1ed",
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