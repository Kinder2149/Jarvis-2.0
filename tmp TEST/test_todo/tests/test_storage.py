import pytest
import os
import json
from src.storage import JsonStorage

def test_load_non_existent_file(tmp_path):
    """Vérifie que load() retourne une liste vide si le fichier n'existe pas."""
    filepath = tmp_path / "non_existent.json"
    storage = JsonStorage(str(filepath))
    
    # Action
    data = storage.load()
    
    # Assertion
    assert data == []

def test_save_and_load_cycle(tmp_path):
    """Vérifie qu'une liste de données sauvegardée peut être rechargée."""
    filepath = tmp_path / "test_data.json"
    storage = JsonStorage(str(filepath))
    sample_data = [
        {"id": 1, "title": "Test 1", "completed": False},
        {"id": 2, "title": "Test 2", "completed": True}
    ]
    
    # Action
    storage.save(sample_data)
    loaded_data = storage.load()
    
    # Assertion
    assert loaded_data == sample_data
    
    # Vérification supplémentaire du contenu du fichier
    with open(filepath, 'r', encoding='utf-8') as f:
        content = json.load(f)
    assert content == sample_data
