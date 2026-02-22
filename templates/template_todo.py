"""
Template — Gestionnaire TODO Python
Gestionnaire de tâches avec stockage JSON et CLI
"""

import json
from datetime import datetime
from pathlib import Path


class Task:
    """Représente une tâche TODO"""

    def __init__(self, id: int, title: str, completed: bool = False, created_at: str = None):
        self.id = id
        self.title = title
        self.completed = completed
        self.created_at = created_at or datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convertit la tâche en dictionnaire"""
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dict(data: dict) -> "Task":
        """Crée une tâche depuis un dictionnaire"""
        return Task(
            id=data["id"],
            title=data["title"],
            completed=data.get("completed", False),
            created_at=data.get("created_at"),
        )


class TodoStorage:
    """Gère le stockage des tâches en JSON"""

    def __init__(self, filepath: str = "todos.json"):
        self.filepath = Path(filepath)

    def load(self) -> list[Task]:
        """Charge les tâches depuis le fichier"""
        if not self.filepath.exists():
            return []

        try:
            with open(self.filepath, encoding="utf-8") as f:
                data = json.load(f)
                return [Task.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError):
            return []

    def save(self, tasks: list[Task]) -> None:
        """Sauvegarde les tâches dans le fichier"""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump([task.to_dict() for task in tasks], f, indent=2, ensure_ascii=False)


class TodoManager:
    """Gestionnaire de tâches TODO"""

    def __init__(self, storage: TodoStorage):
        self.storage = storage
        self.tasks = storage.load()

    def add(self, title: str) -> Task:
        """Ajoute une nouvelle tâche"""
        new_id = max([t.id for t in self.tasks], default=0) + 1
        task = Task(id=new_id, title=title)
        self.tasks.append(task)
        self.storage.save(self.tasks)
        return task

    def list_all(self) -> list[Task]:
        """Liste toutes les tâches"""
        return self.tasks

    def list_pending(self) -> list[Task]:
        """Liste les tâches non complétées"""
        return [t for t in self.tasks if not t.completed]

    def list_completed(self) -> list[Task]:
        """Liste les tâches complétées"""
        return [t for t in self.tasks if t.completed]

    def get(self, task_id: int) -> Task | None:
        """Récupère une tâche par son ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def complete(self, task_id: int) -> bool:
        """Marque une tâche comme complétée"""
        task = self.get(task_id)
        if task:
            task.completed = True
            self.storage.save(self.tasks)
            return True
        return False

    def delete(self, task_id: int) -> bool:
        """Supprime une tâche"""
        task = self.get(task_id)
        if task:
            self.tasks.remove(task)
            self.storage.save(self.tasks)
            return True
        return False


def main():
    """Interface CLI pour le gestionnaire TODO"""
    storage = TodoStorage("todos.json")
    manager = TodoManager(storage)

    print("=== Gestionnaire TODO ===")

    while True:
        print("\n1. Ajouter une tâche")
        print("2. Lister toutes les tâches")
        print("3. Lister les tâches en cours")
        print("4. Lister les tâches complétées")
        print("5. Compléter une tâche")
        print("6. Supprimer une tâche")
        print("0. Quitter")

        choice = input("\nChoisissez une option: ").strip()

        if choice == "0":
            print("Au revoir!")
            break

        elif choice == "1":
            title = input("Titre de la tâche: ").strip()
            if title:
                task = manager.add(title)
                print(f"✓ Tâche #{task.id} ajoutée: {task.title}")
            else:
                print("✗ Titre invalide")

        elif choice == "2":
            tasks = manager.list_all()
            if tasks:
                print("\nToutes les tâches:")
                for task in tasks:
                    status = "✓" if task.completed else "○"
                    print(f"  {status} #{task.id}: {task.title}")
            else:
                print("\nAucune tâche")

        elif choice == "3":
            tasks = manager.list_pending()
            if tasks:
                print("\nTâches en cours:")
                for task in tasks:
                    print(f"  ○ #{task.id}: {task.title}")
            else:
                print("\nAucune tâche en cours")

        elif choice == "4":
            tasks = manager.list_completed()
            if tasks:
                print("\nTâches complétées:")
                for task in tasks:
                    print(f"  ✓ #{task.id}: {task.title}")
            else:
                print("\nAucune tâche complétée")

        elif choice == "5":
            try:
                task_id = int(input("ID de la tâche à compléter: "))
                if manager.complete(task_id):
                    print(f"✓ Tâche #{task_id} complétée")
                else:
                    print(f"✗ Tâche #{task_id} introuvable")
            except ValueError:
                print("✗ ID invalide")

        elif choice == "6":
            try:
                task_id = int(input("ID de la tâche à supprimer: "))
                if manager.delete(task_id):
                    print(f"✓ Tâche #{task_id} supprimée")
                else:
                    print(f"✗ Tâche #{task_id} introuvable")
            except ValueError:
                print("✗ ID invalide")

        else:
            print("✗ Option invalide")


if __name__ == "__main__":
    main()
