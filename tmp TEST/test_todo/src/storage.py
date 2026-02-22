import json
import os
from typing import List, Dict, Any

class JsonStorage:
    """Gère la persistance des données dans un fichier JSON."""

    def __init__(self, filepath: str):
        """
        Initialise le chemin du fichier de stockage.

        Args:
            filepath (str): Le chemin vers le fichier JSON.
        """
        self.filepath = filepath

    def load(self) -> List[Dict[str, Any]]:
        """
        Charge les tâches depuis le fichier JSON.

        Returns:
            list: La liste des tâches. Retourne une liste vide si le fichier n'existe pas.
        """
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save(self, data: List[Dict[str, Any]]) -> None:
        """
        Sauvegarde la liste des tâches dans le fichier JSON.

        Args:
            data (list): La liste des tâches à sauvegarder.
        """
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
