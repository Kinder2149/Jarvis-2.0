from src.storage import JsonStorage
from typing import List, Dict, Any

class TodoManager:
    """Gère la logique métier des tâches."""

    def __init__(self, storage: JsonStorage):
        """
        Initialise avec une instance de JsonStorage et charge les tâches.

        Args:
            storage (JsonStorage): L'instance de storage pour la persistance.
        """
        self.storage = storage
        self.tasks = self.storage.load()

    def _get_next_id(self) -> int:
        """
        Calcule le prochain ID de tâche disponible.

        Returns:
            int: Le prochain ID (max des IDs existants + 1).
        """
        if not self.tasks:
            return 1
        return max(task['id'] for task in self.tasks) + 1

    def add_task(self, title: str) -> int:
        """
        Ajoute une nouvelle tâche.

        Args:
            title (str): Le titre de la tâche.

        Returns:
            int: L'ID de la nouvelle tâche.
        """
        if not isinstance(title, str) or not title:
            raise ValueError("Le titre doit être une chaîne de caractères non vide.")
        
        new_id = self._get_next_id()
        task = {
            'id': new_id,
            'title': title,
            'completed': False
        }
        self.tasks.append(task)
        self.storage.save(self.tasks)
        return new_id

    def list_tasks(self) -> List[Dict[str, Any]]:
        """
        Retourne la liste complète des tâches.

        Returns:
            list: La liste des tâches.
        """
        return self.tasks

    def complete_task(self, task_id: int) -> bool:
        """
        Marque une tâche comme complétée.

        Args:
            task_id (int): L'ID de la tâche à compléter.
        
        Returns:
            bool: True si la tâche a été trouvée et modifiée, False sinon.
        """
        if not isinstance(task_id, int):
            raise ValueError("L'ID de la tâche doit être un entier.")

        task_found = False
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                task_found = True
                break
        
        if task_found:
            self.storage.save(self.tasks)
        return task_found

    def delete_task(self, task_id: int) -> bool:
        """
        Supprime une tâche en se basant sur son ID.

        Args:
            task_id (int): L'ID de la tâche à supprimer.

        Returns:
            bool: True si la tâche a été trouvée et supprimée, False sinon.
        """
        if not isinstance(task_id, int):
            raise ValueError("L'ID de la tâche doit être un entier.")
            
        initial_len = len(self.tasks)
        self.tasks = [task for task in self.tasks if task['id'] != task_id]
        
        if len(self.tasks) < initial_len:
            self.storage.save(self.tasks)
            return True
        return False
