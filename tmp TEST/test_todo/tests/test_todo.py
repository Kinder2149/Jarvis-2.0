import pytest
import os
from src.storage import JsonStorage
from src.todo import TodoManager

@pytest.fixture
def todo_manager(tmp_path):
    """
    Fixture pour créer une instance de TodoManager avec un fichier de stockage
    temporaire pour chaque test, garantissant l'isolation des tests.
    """
    temp_file = tmp_path / "test_todo.json"
    storage = JsonStorage(filepath=str(temp_file))
    manager = TodoManager(storage=storage)
    return manager

def test_add_task(todo_manager):
    """Vérifie l'ajout d'une tâche et l'incrémentation correcte de l'ID."""
    # Ajout de la première tâche
    task_id_1 = todo_manager.add_task("Faire les courses")
    assert task_id_1 == 1
    tasks = todo_manager.list_tasks()
    assert len(tasks) == 1
    assert tasks[0] == {"id": 1, "title": "Faire les courses", "completed": False}

    # Ajout de la deuxième tâche pour vérifier l'incrémentation de l'ID
    task_id_2 = todo_manager.add_task("Appeler le médecin")
    assert task_id_2 == 2
    tasks = todo_manager.list_tasks()
    assert len(tasks) == 2
    assert tasks[1] == {"id": 2, "title": "Appeler le médecin", "completed": False}

def test_list_tasks(todo_manager):
    """Vérifie que la liste des tâches est correcte après un ajout."""
    # La liste doit être vide au début
    assert todo_manager.list_tasks() == []

    # Après ajout, la liste doit contenir la nouvelle tâche
    todo_manager.add_task("Lire un livre")
    tasks = todo_manager.list_tasks()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Lire un livre"

def test_complete_task(todo_manager):
    """Vérifie que le statut 'completed' d'une tâche passe bien à True."""
    task_id = todo_manager.add_task("Nettoyer la cuisine")
    
    # Vérifier l'état initial
    task_initial = todo_manager.list_tasks()[0]
    assert task_initial["completed"] is False

    # Marquer comme complétée
    todo_manager.complete_task(task_id)
    
    # Vérifier le nouvel état
    task_completed = todo_manager.list_tasks()[0]
    assert task_completed["completed"] is True

def test_delete_task(todo_manager):
    """Vérifie qu'une tâche est bien supprimée de la liste."""
    task_id_1 = todo_manager.add_task("Tâche à garder")
    task_id_2 = todo_manager.add_task("Tâche à supprimer")
    
    assert len(todo_manager.list_tasks()) == 2

    # Suppression de la tâche
    todo_manager.delete_task(task_id_2)
    
    tasks = todo_manager.list_tasks()
    assert len(tasks) == 1
    assert tasks[0]["id"] == task_id_1 # Vérifie que la bonne tâche a été supprimée
