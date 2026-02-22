
import pytest
import pytest_asyncio

from backend.db.database import Database


@pytest_asyncio.fixture
async def db(tmp_path):
    test_db_path = str(tmp_path / "test_jarvis.db")
    db_instance = Database(test_db_path)
    await db_instance.initialize()
    yield db_instance


@pytest.mark.asyncio
async def test_create_project_valid(db):
    project = await db.create_project(
        name="Test Project", path="/test/path", description="Test description"
    )

    assert project["name"] == "Test Project"
    assert project["path"] == "/test/path"
    assert project["description"] == "Test description"
    assert "id" in project
    assert "created_at" in project


@pytest.mark.asyncio
async def test_get_project_exists(db):
    created = await db.create_project(name="Test", path="/test")
    retrieved = await db.get_project(created["id"])

    assert retrieved is not None
    assert retrieved["id"] == created["id"]
    assert retrieved["name"] == "Test"


@pytest.mark.asyncio
async def test_get_project_not_found(db):
    result = await db.get_project("non-existent-id")
    assert result is None


@pytest.mark.asyncio
async def test_list_projects_empty(db):
    projects = await db.list_projects()
    assert projects == []


@pytest.mark.asyncio
async def test_list_projects_multiple(db):
    await db.create_project(name="Project 1", path="/path1")
    await db.create_project(name="Project 2", path="/path2")

    projects = await db.list_projects()
    assert len(projects) == 2


@pytest.mark.asyncio
async def test_update_project(db):
    project = await db.create_project(name="Original", path="/test")

    success = await db.update_project(project["id"], name="Updated", description="New description")

    assert success is True

    updated = await db.get_project(project["id"])
    assert updated["name"] == "Updated"
    assert updated["description"] == "New description"


@pytest.mark.asyncio
async def test_delete_project(db):
    project = await db.create_project(name="To Delete", path="/test")

    success = await db.delete_project(project["id"])
    assert success is True

    retrieved = await db.get_project(project["id"])
    assert retrieved is None


@pytest.mark.asyncio
async def test_create_conversation(db):
    project = await db.create_project(name="Test", path="/test")

    conversation = await db.create_conversation(
        agent_id="BASE", project_id=project["id"], title="Test Conversation"
    )

    assert conversation["project_id"] == project["id"]
    assert conversation["agent_id"] == "BASE"
    assert conversation["title"] == "Test Conversation"
    assert "id" in conversation


@pytest.mark.asyncio
async def test_list_conversations(db):
    project = await db.create_project(name="Test", path="/test")

    await db.create_conversation(agent_id="BASE", project_id=project["id"], title="Conv 1")
    await db.create_conversation(agent_id="JARVIS_Maître", project_id=project["id"], title="Conv 2")

    conversations = await db.list_conversations(project["id"])
    assert len(conversations) == 2


@pytest.mark.asyncio
async def test_delete_conversation(db):
    project = await db.create_project(name="Test", path="/test")
    conversation = await db.create_conversation(agent_id="BASE", project_id=project["id"])

    success = await db.delete_conversation(conversation["id"])
    assert success is True

    retrieved = await db.get_conversation(conversation["id"])
    assert retrieved is None


@pytest.mark.asyncio
async def test_add_message(db):
    project = await db.create_project(name="Test", path="/test")
    conversation = await db.create_conversation(agent_id="BASE", project_id=project["id"])

    message = await db.add_message(conversation["id"], "user", "Hello world")

    assert message["conversation_id"] == conversation["id"]
    assert message["role"] == "user"
    assert message["content"] == "Hello world"
    assert "id" in message


@pytest.mark.asyncio
async def test_get_messages(db):
    project = await db.create_project(name="Test", path="/test")
    conversation = await db.create_conversation(agent_id="BASE", project_id=project["id"])

    await db.add_message(conversation["id"], "user", "Message 1")
    await db.add_message(conversation["id"], "assistant", "Message 2")

    messages = await db.get_messages(conversation["id"])
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


@pytest.mark.asyncio
async def test_get_conversation_history(db):
    project = await db.create_project(name="Test", path="/test")
    conversation = await db.create_conversation(agent_id="BASE", project_id=project["id"])

    await db.add_message(conversation["id"], "user", "Hello")
    await db.add_message(conversation["id"], "assistant", "Hi")

    history = await db.get_conversation_history(conversation["id"])
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[0]["content"] == "Hello"


@pytest.mark.asyncio
async def test_cascade_delete_project(db):
    project = await db.create_project(name="Test", path="/test")
    conversation = await db.create_conversation(agent_id="BASE", project_id=project["id"])
    await db.add_message(conversation["id"], "user", "Test")

    await db.delete_project(project["id"])

    retrieved_conv = await db.get_conversation(conversation["id"])
    assert retrieved_conv is None

    messages = await db.get_messages(conversation["id"])
    assert len(messages) == 0


@pytest.mark.asyncio
async def test_update_conversation_timestamp(db):
    project = await db.create_project(name="Test", path="/test")
    conversation = await db.create_conversation(agent_id="BASE", project_id=project["id"])

    original_time = conversation["updated_at"]

    import asyncio

    await asyncio.sleep(0.1)

    await db.update_conversation_timestamp(conversation["id"])

    updated = await db.get_conversation(conversation["id"])
    assert updated["updated_at"] != original_time


@pytest.mark.asyncio
async def test_project_conversation_count(db):
    project = await db.create_project(name="Test", path="/test")

    retrieved = await db.get_project(project["id"])
    assert retrieved["conversation_count"] == 0

    await db.create_conversation(agent_id="BASE", project_id=project["id"])
    await db.create_conversation(agent_id="BASE", project_id=project["id"])

    retrieved = await db.get_project(project["id"])
    assert retrieved["conversation_count"] == 2
