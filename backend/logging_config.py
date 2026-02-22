"""
Configuration centralisée du logging pour JARVIS 2.0.
Logs détaillés pour diagnostic des timeouts API.
"""

import logging
import sys
from pathlib import Path


def setup_logging(log_level=logging.INFO):
    """
    Configure le logging pour l'application avec sortie console et fichier.

    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR)
    """
    # Créer le dossier logs s'il n'existe pas
    log_dir = Path("backend/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Format détaillé pour diagnostic
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler fichier (logs détaillés)
    file_handler = logging.FileHandler(log_dir / "gemini_api.log", mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)

    # Handler console (logs importants seulement)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(log_format)

    # Configuration du logger racine
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Loggers spécifiques avec niveau DEBUG
    loggers_to_configure = [
        "backend.ia.providers.gemini_provider",
        "backend.agents.base_agent",
        "backend.api",
        "backend.services.orchestration",
    ]

    for logger_name in loggers_to_configure:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

    # Réduire verbosité des librairies tierces
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logging.info("Logging configuré : backend/logs/gemini_api.log")
