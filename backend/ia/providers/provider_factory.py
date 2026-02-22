"""
Factory pour créer le provider Gemini selon l'agent
Sélection basée sur configuration .env
"""

import logging
import os
from dotenv import load_dotenv

from backend.ia.providers.base_provider import BaseProvider
from backend.ia.providers.gemini_provider import GeminiProvider

# Charger .env au démarrage du module
load_dotenv()

logger = logging.getLogger(__name__)


class ProviderFactory:
    """
    Factory pour instancier le provider Gemini selon l'agent.
    
    Configuration via .env :
    - JARVIS_MAITRE_PROVIDER=gemini → GeminiProvider
    - BASE_PROVIDER=gemini → GeminiProvider
    - CODEUR_PROVIDER=gemini → GeminiProvider
    - VALIDATEUR_PROVIDER=gemini → GeminiProvider
    """

    _PROVIDER_CACHE: dict[str, BaseProvider] = {}

    @staticmethod
    def create(agent_name: str) -> BaseProvider:
        """
        Crée ou récupère un provider Gemini pour l'agent donné.
        
        Args:
            agent_name: Nom de l'agent ("JARVIS_Maître", "BASE", "CODEUR", "VALIDATEUR")
            
        Returns:
            Instance du GeminiProvider avec modèle spécifique à l'agent
            
        Raises:
            RuntimeError: Si les variables .env sont manquantes
        """
        # Recharger .env pour éviter cache obsolète (important en dev avec --reload)
        load_dotenv(override=True)
        
        # Normaliser nom agent pour variable .env
        env_agent_name = agent_name.upper().replace("Î", "I").replace("È", "E")
        if env_agent_name == "JARVIS_MAÎTRE":
            env_agent_name = "JARVIS_MAITRE"

        # Vérifier si provider en cache
        cache_key = agent_name
        cached_provider = ProviderFactory._PROVIDER_CACHE.get(cache_key)
        
        if cached_provider:
            logger.debug(f"Provider cache hit: {agent_name} (gemini)")
            return cached_provider

        # Créer provider Gemini
        provider = ProviderFactory._create_gemini(agent_name)

        # Mettre en cache
        ProviderFactory._PROVIDER_CACHE[cache_key] = provider
        
        logger.info(f"Provider created: {agent_name} → gemini (model={provider.model})")

        return provider

    @staticmethod
    def _create_gemini(agent_name: str = None) -> GeminiProvider:
        """Crée un provider Gemini avec modèle spécifique par agent."""
        api_key = os.getenv("GEMINI_API_KEY")
        
        # Récupérer modèle spécifique à l'agent si défini
        if agent_name:
            env_agent_name = agent_name.upper().replace("Î", "I").replace("È", "E")
            if env_agent_name == "JARVIS_MAÎTRE":
                env_agent_name = "JARVIS_MAITRE"
            
            agent_model = os.getenv(f"{env_agent_name}_MODEL")
            if agent_model:
                model = agent_model
            else:
                # Fallback sur GEMINI_MODEL global
                model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")
        else:
            model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash-latest")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY manquante dans .env")

        return GeminiProvider(api_key=api_key, model=model)


    @staticmethod
    def clear_cache():
        """Vide le cache des providers (utile pour tests)."""
        ProviderFactory._PROVIDER_CACHE.clear()
        logger.debug("Provider cache cleared")
