import pytest
import pytest_asyncio

from backend.db.database import Database
from backend.models.library import LibraryDocumentCreate, LibraryDocumentUpdate

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def db():
    import os

    test_db_path = "test_library.db"

    # Supprimer la base de test si elle existe
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    db = Database(db_path=test_db_path)
    await db.initialize()

    yield db

    # Nettoyage après les tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)


@pytest_asyncio.fixture
async def sample_doc(db):
    doc = await db.create_library_document(
        category="libraries",
        name="Test Library",
        description="A test library document",
        content="# Test Content\n\nThis is test content.",
        tags=["test", "python"],
        agents=["CODEUR", "BASE"],
        icon="🧪",
    )
    return doc


@pytest.mark.asyncio
async def test_create_library_document(db):
    doc = await db.create_library_document(
        category="methodologies",
        name="Test Methodology",
        description="A test methodology",
        content="# Methodology\n\nSteps...",
        tags=["process"],
        agents=["JARVIS_Maître"],
        icon="📋",
    )

    assert doc["id"] is not None
    assert doc["category"] == "methodologies"
    assert doc["name"] == "Test Methodology"
    assert doc["description"] == "A test methodology"
    assert doc["content"] == "# Methodology\n\nSteps..."
    assert doc["tags"] == ["process"]
    assert doc["agents"] == ["JARVIS_Maître"]
    assert doc["icon"] == "📋"
    assert doc["created_at"] is not None
    assert doc["updated_at"] is not None


@pytest.mark.asyncio
async def test_get_library_document(db, sample_doc):
    retrieved = await db.get_library_document(sample_doc["id"])

    assert retrieved is not None
    assert retrieved["id"] == sample_doc["id"]
    assert retrieved["name"] == "Test Library"
    assert retrieved["category"] == "libraries"
    assert retrieved["tags"] == ["test", "python"]
    assert retrieved["agents"] == ["CODEUR", "BASE"]


@pytest.mark.asyncio
async def test_get_library_document_not_found(db):
    retrieved = await db.get_library_document("nonexistent-id")
    assert retrieved is None


@pytest.mark.asyncio
async def test_list_library_documents_all(db, sample_doc):
    doc2 = await db.create_library_document(
        category="prompts",
        name="Test Prompt",
        description="A test prompt",
        content="Prompt content",
        tags=["template"],
        agents=["JARVIS_Maître"],
    )

    docs = await db.list_library_documents()
    assert len(docs) == 2
    assert docs[0]["id"] == doc2["id"]  # Plus récent en premier
    assert docs[1]["id"] == sample_doc["id"]


@pytest.mark.asyncio
async def test_list_library_documents_filter_by_category(db, sample_doc):
    await db.create_library_document(
        category="prompts",
        name="Test Prompt",
        description="A test prompt",
        content="Prompt content",
        tags=["template"],
        agents=["JARVIS_Maître"],
    )

    docs = await db.list_library_documents(category="libraries")
    assert len(docs) == 1
    assert docs[0]["category"] == "libraries"


@pytest.mark.asyncio
async def test_list_library_documents_filter_by_agent(db, sample_doc):
    await db.create_library_document(
        category="prompts",
        name="Test Prompt",
        description="A test prompt",
        content="Prompt content",
        tags=["template"],
        agents=["JARVIS_Maître"],
    )

    docs = await db.list_library_documents(agent="CODEUR")
    assert len(docs) == 1
    assert "CODEUR" in docs[0]["agents"]


@pytest.mark.asyncio
async def test_list_library_documents_filter_by_tag(db, sample_doc):
    await db.create_library_document(
        category="prompts",
        name="Test Prompt",
        description="A test prompt",
        content="Prompt content",
        tags=["template", "user"],
        agents=["JARVIS_Maître"],
    )

    docs = await db.list_library_documents(tag="python")
    assert len(docs) == 1
    assert "python" in docs[0]["tags"]


@pytest.mark.asyncio
async def test_list_library_documents_search(db, sample_doc):
    await db.create_library_document(
        category="prompts",
        name="Unique Name",
        description="A test prompt",
        content="Prompt content",
        tags=["template"],
        agents=["JARVIS_Maître"],
    )

    docs = await db.list_library_documents(search="Unique")
    assert len(docs) == 1
    assert docs[0]["name"] == "Unique Name"

    docs = await db.list_library_documents(search="test")
    assert len(docs) == 2  # Les deux contiennent "test"


@pytest.mark.asyncio
async def test_list_library_documents_multiple_filters(db, sample_doc):
    await db.create_library_document(
        category="libraries",
        name="Another Library",
        description="Another test",
        content="Content",
        tags=["python", "web"],
        agents=["CODEUR"],
    )

    docs = await db.list_library_documents(category="libraries", agent="CODEUR", tag="python")
    assert len(docs) == 2


@pytest.mark.asyncio
async def test_update_library_document_name(db, sample_doc):
    success = await db.update_library_document(doc_id=sample_doc["id"], name="Updated Name")

    assert success is True

    updated = await db.get_library_document(sample_doc["id"])
    assert updated["name"] == "Updated Name"
    assert updated["description"] == sample_doc["description"]  # Inchangé
    assert updated["updated_at"] != sample_doc["updated_at"]


@pytest.mark.asyncio
async def test_update_library_document_multiple_fields(db, sample_doc):
    success = await db.update_library_document(
        doc_id=sample_doc["id"],
        name="New Name",
        description="New Description",
        content="New Content",
        tags=["new", "tags"],
        agents=["BASE"],
        icon="🆕",
    )

    assert success is True

    updated = await db.get_library_document(sample_doc["id"])
    assert updated["name"] == "New Name"
    assert updated["description"] == "New Description"
    assert updated["content"] == "New Content"
    assert updated["tags"] == ["new", "tags"]
    assert updated["agents"] == ["BASE"]
    assert updated["icon"] == "🆕"


@pytest.mark.asyncio
async def test_update_library_document_not_found(db):
    success = await db.update_library_document(doc_id="nonexistent-id", name="New Name")

    assert success is False


@pytest.mark.asyncio
async def test_update_library_document_no_fields(db, sample_doc):
    success = await db.update_library_document(doc_id=sample_doc["id"])
    assert success is False


@pytest.mark.asyncio
async def test_delete_library_document(db, sample_doc):
    success = await db.delete_library_document(sample_doc["id"])
    assert success is True

    retrieved = await db.get_library_document(sample_doc["id"])
    assert retrieved is None


@pytest.mark.asyncio
async def test_delete_library_document_not_found(db):
    success = await db.delete_library_document("nonexistent-id")
    assert success is False


@pytest.mark.asyncio
async def test_library_document_create_model_validation():
    doc = LibraryDocumentCreate(
        category="libraries",
        name="Test",
        description="Test description",
        content="Test content",
        tags=["tag1"],
        agents=["CODEUR"],
    )

    assert doc.category == "libraries"
    assert doc.name == "Test"
    assert doc.icon is None


@pytest.mark.asyncio
async def test_library_document_create_model_invalid_category():
    with pytest.raises(Exception):  # Pydantic validation error
        LibraryDocumentCreate(
            category="invalid_category",
            name="Test",
            description="Test description",
            content="Test content",
        )


@pytest.mark.asyncio
async def test_library_document_update_model():
    update = LibraryDocumentUpdate(name="Updated Name", description="Updated Description")

    assert update.name == "Updated Name"
    assert update.description == "Updated Description"
    assert update.content is None
    assert update.tags is None


@pytest.mark.asyncio
async def test_library_document_update_model_all_none():
    update = LibraryDocumentUpdate()

    assert update.name is None
    assert update.description is None
    assert update.content is None
    assert update.tags is None
    assert update.agents is None
    assert update.icon is None
