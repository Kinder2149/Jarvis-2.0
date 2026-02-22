def build_project_context_message(project: dict, file_tree: dict) -> str:
    """
    Construit un message système avec contexte projet.
    Injecté comme premier message dans la conversation.
    Limite stricte à 1000 chars pour éviter timeout API.
    Max 3 niveaux de profondeur, 50 fichiers max.
    """
    description_line = (
        f"{project['description'][:80]}" if project.get("description") else "Nouveau projet"
    )

    # Générer l'arborescence compressée (max 3 niveaux, 50 fichiers)
    tree_output = format_file_tree(file_tree, max_depth=3, max_files=50)

    # Limiter l'arborescence à 600 chars max
    if len(tree_output) > 600:
        tree_output = tree_output[:600] + "\n..."

    # Contexte compressé
    context = f"""PROJET: {project["name"]}
PATH: {project["path"]}
DESC: {description_line}

STRUCTURE:
{tree_output}

MODE PROJET: Méthodologie obligatoire"""

    # Sécurité finale : limiter à 1000 chars
    if len(context) > 1000:
        context = context[:1000]

    return context


def build_chat_simple_context() -> str:
    """
    Construit un contexte léger pour le mode chat simple.
    Injecté comme préfixe au premier message de la conversation.
    """
    return "MODE CHAT: Réponses directes."


def format_file_tree(
    tree: dict, max_depth: int = 3, indent: int = 0, max_files: int = 50, file_count: list = None
) -> str:
    """Formate l'arborescence en texte lisible avec indentation.
    Limite à max_depth niveaux et max_files fichiers totaux.
    """
    if file_count is None:
        file_count = [0]  # Compteur mutable partagé

    if not tree or indent > max_depth or file_count[0] >= max_files:
        return ""

    result = []
    prefix = "  " * indent

    if tree.get("type") == "directory":
        if indent > 0:
            result.append(f"{prefix}{tree['name']}/")

        for item in tree.get("items", []):
            if file_count[0] >= max_files:
                result.append(f"{prefix}  ... ({max_files} fichiers max atteints)")
                break

            if item["type"] == "directory":
                if indent < max_depth:
                    child_result = format_file_tree(
                        item, max_depth, indent + 1, max_files, file_count
                    )
                    if child_result:
                        result.append(child_result)
            else:
                result.append(f"{prefix}  {item['name']}")
                file_count[0] += 1

    return "\n".join(result)
