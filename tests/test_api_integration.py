import asyncio
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.app import app
from backend.db.database import Database


@pytest.fixture(autouse=True)
def clean_db(tmp_path):
    """Utilise une DB temporaire isolée pour chaque test."""
    test_db_path = str(tmp_path / "test_integration.db")
    test_db = Database(test_db_path)

    with (
        patch("backend.db.database.db_instance", test_db),
        patch("backend.api.db_instance", test_db),
    ):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(test_db.initialize())
        yield test_db
        loop.close()


@pytest.fixture
def client(clean_db):
    return TestClient(app)


@pytest.fixture
def temp_project_path():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        (project_path / "README.md").write_text("# Test Project", encoding="utf-8")
        (project_path / "src").mkdir()
        (project_path / "src" / "main.py").write_text("print('hello')", encoding="utf-8")
        yield str(project_path)


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "JARVIS API"}


def test_list_agents(client):
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert len(data["agents"]) >= 2


def test_create_project_valid(client, temp_project_path):
    response = client.post(
        "/api/projects",
        json={"name": "Test Project", "path": temp_project_path, "description": "Test description"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data


def test_create_project_invalid_path(client):
    response = client.post(
        "/api/projects",
        json={"name": "Invalid Project", "path": "/nonexistent/path", "description": "Test"},
    )

    assert response.status_code == 400


def test_list_projects(client, temp_project_path):
    client.post("/api/projects", json={"name": "Project 1", "path": temp_project_path})

    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_project(client, temp_project_path):
    create_response = client.post(
        "/api/projects", json={"name": "Test Project", "path": temp_project_path}
    )
    project_id = create_response.json()["id"]

    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id


def test_update_project(client, temp_project_path):
    create_response = client.post(
        "/api/projects", json={"name": "Original", "path": temp_project_path}
    )
    project_id = create_response.json()["id"]

    response = client.put(
        f"/api/projects/{project_id}", json={"name": "Updated", "description": "New description"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated"


def test_delete_project(client, temp_project_path):
    create_response = client.post(
        "/api/projects", json={"name": "To Delete", "path": temp_project_path}
    )
    project_id = create_response.json()["id"]

    response = client.delete(f"/api/projects/{project_id}")
    assert response.status_code == 200

    get_response = client.get(f"/api/projects/{project_id}")
    assert get_response.status_code == 404


def test_create_conversation(client, temp_project_path):
    project_response = client.post(
        "/api/projects", json={"name": "Test", "path": temp_project_path}
    )
    project_id = project_response.json()["id"]

    response = client.post(
        f"/api/projects/{project_id}/conversations",
        json={"agent_id": "BASE", "title": "Test Conversation"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["agent_id"] == "BASE"
    assert data["project_id"] == project_id


def test_list_conversations(client, temp_project_path):
    project_response = client.post(
        "/api/projects", json={"name": "Test", "path": temp_project_path}
    )
    project_id = project_response.json()["id"]

    client.post(f"/api/projects/{project_id}/conversations", json={"agent_id": "BASE"})

    response = client.get(f"/api/projects/{project_id}/conversations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_send_message(client, temp_project_path):
    project_response = client.post(
        "/api/projects", json={"name": "Test", "path": temp_project_path}
    )
    project_id = project_response.json()["id"]

    conv_response = client.post(
        f"/api/projects/{project_id}/conversations", json={"agent_id": "BASE"}
    )
    conversation_id = conv_response.json()["id"]

    response = client.post(
        f"/api/conversations/{conversation_id}/messages",
        json={"content": "Hello, what is the project name?"},
    )

    assert response.status_code in [200, 503]


def test_get_messages(client, temp_project_path):
    project_response = client.post(
        "/api/projects", json={"name": "Test", "path": temp_project_path}
    )
    project_id = project_response.json()["id"]

    conv_response = client.post(
        f"/api/projects/{project_id}/conversations", json={"agent_id": "BASE"}
    )
    conversation_id = conv_response.json()["id"]

    response = client.get(f"/api/conversations/{conversation_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_file_tree(client, temp_project_path):
    project_response = client.post(
        "/api/projects", json={"name": "Test", "path": temp_project_path}
    )
    project_id = project_response.json()["id"]

    response = client.get(f"/api/projects/{project_id}/files/tree")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "directory"


def test_list_files(client, temp_project_path):
    project_response = client.post(
        "/api/projects", json={"name": "Test", "path": temp_project_path}
    )
    project_id = project_response.json()["id"]

    response = client.get(f"/api/projects/{project_id}/files/list")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total_count"] >= 0


def test_read_file(client, temp_project_path):
    project_response = client.post(
        "/api/projects", json={"name": "Test", "path": temp_project_path}
    )
    project_id = project_response.json()["id"]

    response = client.get(f"/api/projects/{project_id}/files/read?path=README.md")
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "# Test Project"


def test_read_file_security(client, temp_project_path):
    project_response = client.post(
        "/api/projects", json={"name": "Test", "path": temp_project_path}
    )
    project_id = project_response.json()["id"]

    response = client.get(f"/api/projects/{project_id}/files/read?path=../../../etc/passwd")
    assert response.status_code == 403


def test_search_files(client, temp_project_path):
    project_response = client.post(
        "/api/projects", json={"name": "Test", "path": temp_project_path}
    )
    project_id = project_response.json()["id"]

    response = client.get(f"/api/projects/{project_id}/files/search?pattern=README")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_delete_conversation(client, temp_project_path):
    project_response = client.post(
        "/api/projects", json={"name": "Test", "path": temp_project_path}
    )
    project_id = project_response.json()["id"]

    conv_response = client.post(
        f"/api/projects/{project_id}/conversations", json={"agent_id": "BASE"}
    )
    conversation_id = conv_response.json()["id"]

    response = client.delete(f"/api/conversations/{conversation_id}")
    assert response.status_code == 200


def test_cascade_delete(client, temp_project_path):
    project_response = client.post(
        "/api/projects", json={"name": "Test", "path": temp_project_path}
    )
    project_id = project_response.json()["id"]

    conv_response = client.post(
        f"/api/projects/{project_id}/conversations", json={"agent_id": "BASE"}
    )
    conversation_id = conv_response.json()["id"]

    client.delete(f"/api/projects/{project_id}")

    conv_get = client.get(f"/api/conversations/{conversation_id}")
    assert conv_get.status_code == 404
