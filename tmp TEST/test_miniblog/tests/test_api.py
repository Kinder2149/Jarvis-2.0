import pytest
from fastapi.testclient import TestClient
from src.main import app
from src import database

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Fixture pour nettoyer la base de données avant chaque test."""
    database.db = []
    database.post_id_counter = 0
    yield

client = TestClient(app)

def test_create_post():
    """Teste la création d'un nouveau post."""
    response = client.post("/posts", json={"title": "Titre 1", "content": "Contenu 1"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Titre 1"
    assert data["content"] == "Contenu 1"
    assert "id" in data
    assert data["id"] == 1

def test_get_all_posts():
    """Teste la récupération de tous les posts."""
    client.post("/posts", json={"title": "Titre 1", "content": "Contenu 1"})
    client.post("/posts", json={"title": "Titre 2", "content": "Contenu 2"})
    
    response = client.get("/posts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Titre 1"
    assert data[1]["title"] == "Titre 2"

def test_get_one_post():
    """Teste la récupération d'un post spécifique."""
    post_res = client.post("/posts", json={"title": "Titre Test", "content": "Contenu Test"})
    post_id = post_res.json()["id"]
    
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Titre Test"
    assert data["id"] == post_id

def test_get_nonexistent_post():
    """Teste la récupération d'un post qui n'existe pas."""
    response = client.get("/posts/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Le post avec l'ID 999 n'a pas été trouvé."}

def test_update_post():
    """Teste la mise à jour d'un post existant."""
    post_res = client.post("/posts", json={"title": "Ancien Titre", "content": "Ancien Contenu"})
    post_id = post_res.json()["id"]
    
    response = client.put(f"/posts/{post_id}", json={"title": "Nouveau Titre", "content": "Nouveau Contenu"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Nouveau Titre"
    assert data["content"] == "Nouveau Contenu"
    assert data["id"] == post_id

def test_update_nonexistent_post():
    """Teste la mise à jour d'un post qui n'existe pas."""
    response = client.put("/posts/999", json={"title": "Titre", "content": "Contenu"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Le post avec l'ID 999 n'a pas été trouvé."}

def test_delete_post():
    """Teste la suppression d'un post existant."""
    post_res = client.post("/posts", json={"title": "À supprimer", "content": "Contenu"})
    post_id = post_res.json()["id"]
    
    response = client.delete(f"/posts/{post_id}")
    assert response.status_code == 204
    
    # Vérifier que le post a bien été supprimé
    get_response = client.get(f"/posts/{post_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_post():
    """Teste la suppression d'un post qui n'existe pas."""
    response = client.delete("/posts/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Le post avec l'ID 999 n'a pas été trouvé."}
