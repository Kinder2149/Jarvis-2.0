from typing import List, Dict, Any

# Base de données en mémoire (simple liste de dictionnaires)
db: List[Dict[str, Any]] = []

# Compteur pour générer des ID uniques pour les posts
post_id_counter = 0

def get_next_id() -> int:
    """Incrémente et retourne le prochain ID disponible."""
    global post_id_counter
    post_id_counter += 1
    return post_id_counter
