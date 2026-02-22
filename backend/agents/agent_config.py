"""
Configuration des agents JARVIS 2.0
Mapping agent_name → variable .env + métadonnées
"""

AGENT_CONFIGS = {
    "BASE": {
        "name": "BASE",
        "role": "Assistant générique",
        "description": "Agent neutre servant de worker pour tâches génériques.",
        "permissions": ["read", "write"],
        "type": "worker",
        "temperature": 0.7,
        "max_tokens": 4096,
        "prompt_file": "config_agents/BASE.md",
    },
    "CODEUR": {
        "name": "CODEUR",
        "role": "Agent spécialisé code",
        "description": (
            "Agent spécialisé dans l'écriture de code. Exécute des instructions précises, "
            "produit du code propre et fonctionnel. Ne prend aucune décision architecturale."
        ),
        "permissions": ["read", "write", "code"],
        "type": "worker",
        "temperature": 0.3,
        "max_tokens": 4096,
        "prompt_file": "config_agents/CODEUR.md",
    },
    "VALIDATEUR": {
        "name": "VALIDATEUR",
        "role": "Agent de contrôle qualité",
        "description": (
            "Agent spécialisé dans la vérification de la qualité du code. "
            "Détecte les bugs, erreurs syntaxiques, et incohérences. "
            "Signale les problèmes sans corriger le code."
        ),
        "permissions": ["read"],
        "type": "validator",
        "temperature": 0.5,
        "max_tokens": 2048,
        "prompt_file": "config_agents/VALIDATEUR.md",
    },
    "JARVIS_Maître": {
        "name": "JARVIS_Maître",
        "role": "Assistant personnel principal",
        "description": (
            "Assistant IA personnel de Val C. Interface centrale du système JARVIS. "
            "Répond de manière claire et structurée, traduit le technique en langage accessible."
        ),
        "permissions": ["read", "write", "orchestrate"],
        "type": "orchestrator",
        "temperature": 0.3,
        "max_tokens": 4096,
        "prompt_file": "config_agents/JARVIS_MAITRE.md",
    },
}


def get_agent_config(agent_name: str) -> dict:
    """
    Récupère la configuration d'un agent.

    Args:
        agent_name: Nom de l'agent ("BASE" ou "JARVIS_Maître")

    Returns:
        Configuration de l'agent

    Raises:
        ValueError: Si l'agent n'existe pas
    """
    if agent_name not in AGENT_CONFIGS:
        available = ", ".join(AGENT_CONFIGS.keys())
        raise ValueError(f"Agent inconnu: {agent_name}. Agents disponibles: {available}")
    return AGENT_CONFIGS[agent_name]


def list_available_agents() -> list[dict]:
    """
    Liste tous les agents disponibles avec leurs métadonnées.

    Returns:
        Liste des agents avec id, name, role, description
    """
    return [
        {
            "id": name,
            "name": config["name"],
            "role": config["role"],
            "description": config["description"],
        }
        for name, config in AGENT_CONFIGS.items()
    ]


def list_agents_detailed() -> list[dict]:
    """
    Liste tous les agents avec toutes leurs couches de configuration.

    Returns:
        Liste complète : config locale, permissions, paramètres, provider, modèle
    """
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Mapping des modèles par agent depuis .env
    model_mapping = {
        "JARVIS_Maître": os.getenv("JARVIS_MAITRE_MODEL", "gemini-2.5-pro"),
        "BASE": os.getenv("BASE_MODEL", "gemini-2.5-pro"),
        "CODEUR": os.getenv("CODEUR_MODEL", "gemini-2.5-pro"),
        "VALIDATEUR": os.getenv("VALIDATEUR_MODEL", "gemini-3.1-pro-preview"),
    }
    
    agents = []
    for name, config in AGENT_CONFIGS.items():
        agents.append(
            {
                "id": name,
                "name": config["name"],
                "role": config["role"],
                "description": config["description"],
                "type": config["type"],
                "permissions": config["permissions"],
                "temperature": config["temperature"],
                "max_tokens": config["max_tokens"],
                "provider": "gemini",
                "model": model_mapping.get(name, "gemini-2.5-pro"),
                "env_var": f"{name.upper().replace('Î', 'I').replace('È', 'E')}_MODEL" if name != "JARVIS_Maître" else "JARVIS_MAITRE_MODEL",
            }
        )

    return agents
