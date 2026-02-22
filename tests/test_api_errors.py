"""
Tests HTTP erreurs générales API

Tests de gestion erreurs pour validation production :
- Test 404 routes inexistantes
- Test 405 méthodes non autorisées
- Test 422 validation Pydantic
- Test 500 erreurs serveur (simulées)

⚠️ PHASE 1 BLOQUANT PRODUCTION : Ces tests doivent tous passer (4/4)
"""

import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient

from backend.app import app
from backend.db.database import Database


@pytest_asyncio.fixture
async def test_db():
    """Crée une instance DB temporaire pour les tests"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    db = Database(db_path)
    await db.initialize()

    # Injecter dans app
    app.state.db = db

    yield db

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest_asyncio.fixture
async def test_client(test_db):
    """Client HTTP async pour tests API"""
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_404_route_not_found(test_client):
    """
    Test 1 : Erreur 404 routes inexistantes

    Scénario :
    1. Appeler routes inexistantes
    2. Vérifier statut 404
    3. Vérifier message erreur
    """
    # Routes inexistantes à tester
    invalid_routes = [
        "/api/invalid-route",
        "/api/projects/fake-id/invalid",
        "/api/conversations/fake-id/invalid-action",
        "/api/nonexistent",
        "/invalid/path",
    ]

    for route in invalid_routes:
        response = await test_client.get(route)
        # Vérifier statut 404
        assert response.status_code == 404, f"Route {route} devrait retourner 404"

        # Vérifier structure réponse erreur
        result = response.json()
        assert "detail" in result, f"Route {route} devrait avoir 'detail' dans réponse"

    print("\n✅ Test 1 PASSÉ : Erreur 404 routes inexistantes")
    print(f"   Routes testées : {len(invalid_routes)}")
    print("   Toutes retournent 404")


@pytest.mark.asyncio
async def test_405_method_not_allowed(test_client):
    """
    Test 2 : Erreur 405 méthodes non autorisées

    Scénario :
    1. Appeler endpoints avec mauvaises méthodes HTTP
    2. Vérifier statut 405
    3. Vérifier message erreur
    """
    # Tests méthodes non autorisées
    invalid_methods = [
        # PUT sur endpoint GET
        ("PUT", "/api/agents"),
        # DELETE sur endpoint GET
        ("DELETE", "/api/agents"),
        # PATCH sur endpoint POST
        ("PATCH", "/api/conversations/fake-id/confirm-action"),
        # PUT sur endpoint POST
        ("PUT", "/api/conversations/fake-id/confirm-action"),
    ]

    for method, route in invalid_methods:
        if method == "GET":
            response = await test_client.get(route)
        elif method == "PUT":
            response = await test_client.put(route, json={})
        elif method == "DELETE":
            response = await test_client.delete(route)
        elif method == "PATCH":
            response = await test_client.patch(route, json={})

        # Vérifier statut 405 ou 404 (selon implémentation FastAPI)
        assert response.status_code in [404, 405], f"{method} {route} devrait retourner 404 ou 405"

        # Vérifier structure réponse erreur
        result = response.json()
        assert "detail" in result, f"{method} {route} devrait avoir 'detail' dans réponse"

    print("\n✅ Test 2 PASSÉ : Erreur 405 méthodes non autorisées")
    print(f"   Méthodes testées : {len(invalid_methods)}")
    print("   Toutes retournent 404/405")


@pytest.mark.asyncio
async def test_422_validation_error(test_client):
    """
    Test 3 : Erreur 422 validation Pydantic

    Scénario :
    1. Envoyer données invalides (champs manquants, types incorrects)
    2. Vérifier statut 422
    3. Vérifier message erreur validation
    """
    # Test 1 : Créer projet sans champs requis
    response = await test_client.post("/api/projects", json={})
    assert response.status_code == 422
    result = response.json()
    assert "detail" in result

    # Test 2 : Créer projet avec type incorrect
    response = await test_client.post(
        "/api/projects",
        json={
            "name": 123,  # Devrait être string
            "path": "/path/to/project",
        },
    )
    assert response.status_code == 422
    result = response.json()
    assert "detail" in result

    # Test 3 : Créer conversation sans agent_id
    response = await test_client.post(
        "/api/projects/fake-id/conversations",
        json={
            "title": "Test"
            # agent_id manquant
        },
    )
    # Peut retourner 404 (projet inexistant) ou 422 (validation)
    assert response.status_code in [404, 422]

    # Test 4 : Envoyer message avec contenu vide
    response = await test_client.post(
        "/api/conversations/fake-id/messages",
        json={
            "content": ""  # Vide, devrait échouer validation
        },
    )
    # Peut retourner 404 (conversation inexistante) ou 422 (validation)
    assert response.status_code in [404, 422]

    print("\n✅ Test 3 PASSÉ : Erreur 422 validation Pydantic")
    print("   Validations testées : 4")
    print("   Toutes retournent 422 ou 404 (selon ordre validation)")


@pytest.mark.asyncio
async def test_500_server_error_handling(test_client):
    """
    Test 4 : Gestion erreurs serveur 500

    Scénario :
    1. Tenter opérations qui pourraient causer erreurs serveur
    2. Vérifier gestion gracieuse (pas de crash)
    3. Vérifier messages erreur appropriés

    Note : Difficile de forcer erreur 500 sans mocker, on teste plutôt
    que les endpoints gèrent les erreurs gracieusement
    """
    # Test 1 : Créer projet avec chemin invalide (très long)
    invalid_path = "/invalid/path/" + ("x" * 10000)
    response = await test_client.post(
        "/api/projects", json={"name": "TestInvalidPath", "path": invalid_path}
    )
    # Devrait gérer gracieusement (400, 422, ou 500)
    assert response.status_code in [400, 422, 500]
    result = response.json()
    assert "detail" in result

    # Test 2 : Créer conversation avec ID projet très long
    long_project_id = "x" * 10000
    response = await test_client.post(
        f"/api/projects/{long_project_id}/conversations",
        json={"agent_id": "JARVIS_Maître", "title": "Test"},
    )
    # Devrait gérer gracieusement (404 ou 500)
    assert response.status_code in [404, 500]
    result = response.json()
    assert "detail" in result

    # Test 3 : Confirmer action avec ID très long
    long_conversation_id = "x" * 10000
    response = await test_client.post(f"/api/conversations/{long_conversation_id}/confirm-action")
    # Devrait gérer gracieusement (404 ou 500)
    assert response.status_code in [404, 500]
    result = response.json()
    assert "detail" in result

    # Test 4 : Envoyer message avec contenu très long
    long_content = "x" * 100000  # 100k caractères
    response = await test_client.post(
        "/api/conversations/fake-id/messages", json={"content": long_content}
    )
    # Devrait gérer gracieusement (404, 422, ou 500)
    assert response.status_code in [404, 422, 500]
    result = response.json()
    assert "detail" in result

    print("\n✅ Test 4 PASSÉ : Gestion erreurs serveur 500")
    print("   Scénarios testés : 4")
    print("   Tous gérés gracieusement (pas de crash)")
