import argparse
from storage import JsonStorage
from todo import TodoManager

def main():
    """Gère l'interface en ligne de commande pour le gestionnaire de tâches."""
    storage = JsonStorage("todo_list.json")
    manager = TodoManager(storage)

    parser = argparse.ArgumentParser(description="Un gestionnaire de tâches TODO simple en ligne de commande.")
    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles", required=True)

    # Commande 'add'
    add_parser = subparsers.add_parser("add", help="Ajouter une nouvelle tâche.")
    add_parser.add_argument("title", type=str, help="Le titre de la tâche.")

    # Commande 'list'
    subparsers.add_parser("list", help="Lister toutes les tâches.")

    # Commande 'complete'
    complete_parser = subparsers.add_parser("complete", help="Marquer une tâche comme complétée.")
    complete_parser.add_argument("id", type=int, help="L'ID de la tâche à compléter.")

    # Commande 'delete'
    delete_parser = subparsers.add_parser("delete", help="Supprimer une tâche.")
    delete_parser.add_argument("id", type=int, help="L'ID de la tâche à supprimer.")

    args = parser.parse_args()

    if args.command == "add":
        new_id = manager.add_task(args.title)
        print(f"Tâche ajoutée avec l'ID: {new_id}")
    elif args.command == "list":
        tasks = manager.list_tasks()
        if not tasks:
            print("Aucune tâche à afficher.")
        else:
            print("Liste des tâches :")
            for task in tasks:
                status = "✅" if task['completed'] else "❌"
                print(f"  {task['id']}. [{status}] {task['title']}")
    elif args.command == "complete":
        try:
            manager.complete_task(args.id)
            print(f"Tâche {args.id} marquée comme complétée.")
        except ValueError as e:
            print(f"Erreur : {e}")
    elif args.command == "delete":
        try:
            manager.delete_task(args.id)
            print(f"Tâche {args.id} supprimée.")
        except ValueError as e:
            print(f"Erreur : {e}")

if __name__ == "__main__":
    main()
