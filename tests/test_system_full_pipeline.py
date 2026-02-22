"""
Test système intégral JARVIS 2.0 — Pipeline complet avec API réelle

Tests end-to-end sans mocks :
- Création conversation réelle
- Mode PROJECT + Phase EXECUTION
- Délégation réelle CODEUR
- Écriture fichiers réels
- Vérification DB
- Workflow confirmation complet

⚠️ ATTENTION : Ces tests utilisent l'API Mistral réelle et écrivent des fichiers réels
"""

import shutil
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio

from backend.agents.agent_factory import get_agent
from backend.db.database import Database
from backend.models.session_state import Mode, Phase, ProjectState, SessionState
from backend.services.function_executor import FunctionExecutor
from backend.services.orchestration import SimpleOrchestrator


@pytest_asyncio.fixture
async def db_instance():
    """Crée une instance DB temporaire pour les tests"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    db = Database(db_path)
    await db.initialize()
    yield db

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def temp_project_dir():
    """Crée un dossier projet temporaire"""
    temp_dir = tempfile.mkdtemp(prefix="jarvis_test_")
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def orchestrator():
    """Instance orchestrateur"""
    return SimpleOrchestrator()


class TestSystemFullPipeline:
    """Tests système complets avec API réelle"""

    @pytest.mark.asyncio
    async def test_a_safe_action_complete_pipeline(
        self, db_instance, temp_project_dir, orchestrator
    ):
        """
        Test A — Pipeline complet action SAFE

        Scénario :
        1. Créer projet + conversation
        2. Mode PROJECT + Phase EXECUTION
        3. Envoyer message SAFE (créer fichier simple)
        4. Vérifier délégation CODEUR
        5. Vérifier fichier écrit
        6. Vérifier DB contient réponse assistant
        """
        # 1. Créer projet
        project = await db_instance.create_project(name="Test SAFE Pipeline", path=temp_project_dir)
        assert project is not None
        project_id = project["id"]

        # 2. Créer conversation
        conversation = await db_instance.create_conversation(
            agent_id="JARVIS_Maître", project_id=project_id, title="Test SAFE Action"
        )
        assert conversation is not None
        conversation_id = conversation["id"]

        # 3. Créer SessionState mode PROJECT + phase EXECUTION
        session_state = SessionState(
            mode=Mode.PROJECT,
            conversation_id=conversation_id,
            project_id=project_id,
            phase=Phase.EXECUTION,
            project_state=ProjectState.NEW,
        )

        # Vérifier can_write_disk() autorise écriture
        assert session_state.can_write_disk() is True

        # 4. Créer FunctionExecutor
        function_executor = FunctionExecutor(db_instance=db_instance, project_path=temp_project_dir)

        # 5. Envoyer message SAFE via agent JARVIS_Maître
        user_message = (
            "Créer un fichier simple hello.py avec une fonction hello() qui affiche 'Hello World'"
        )

        # Ajouter message user en DB
        await db_instance.add_message(conversation_id, "user", user_message)

        # Récupérer historique
        conversation_history = await db_instance.get_conversation_history(conversation_id)

        # Appeler agent JARVIS_Maître
        agent = get_agent("JARVIS_Maître")
        response = await agent.handle(
            conversation_history, session_id=conversation_id, function_executor=function_executor
        )

        assert response is not None
        assert len(response) > 0

        # 6. Orchestration : process_response pour délégation
        final_response, delegation_results = await orchestrator.process_response(
            response=response,
            conversation_history=conversation_history,
            session_id=conversation_id,
            project_path=temp_project_dir,
            function_executor=function_executor,
            session_state=session_state,
        )

        # 7. Vérifier délégation exécutée
        assert delegation_results is not None
        assert len(delegation_results) > 0

        # Vérifier au moins une délégation CODEUR réussie
        codeur_delegations = [d for d in delegation_results if d["agent_name"] == "CODEUR"]
        assert len(codeur_delegations) > 0
        assert codeur_delegations[0]["success"] is True

        # 8. Vérifier fichiers écrits
        files_written = codeur_delegations[0].get("files_written", [])
        assert len(files_written) > 0

        # Vérifier au moins un fichier avec status="written"
        written_files = [f for f in files_written if f.get("status") == "written"]
        assert len(written_files) > 0

        # Vérifier fichier existe réellement sur disque
        first_file_path = written_files[0]["path"]
        full_path = Path(temp_project_dir) / first_file_path
        assert full_path.exists(), f"Fichier {first_file_path} devrait exister"

        # Vérifier contenu fichier
        content = full_path.read_text(encoding="utf-8")
        assert len(content) > 0
        assert "def hello" in content or "hello" in content.lower()

        # 9. Sauvegarder réponse assistant en DB
        await db_instance.add_message(conversation_id, "assistant", final_response)

        # 10. Vérifier DB contient message assistant
        messages = await db_instance.get_messages(conversation_id)
        assert len(messages) >= 2  # user + assistant

        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        assert len(assistant_messages) >= 1
        assert len(assistant_messages[0]["content"]) > 0

        print(f"\n✅ Test A SAFE complet : {len(written_files)} fichier(s) écrit(s)")
        print(f"   Fichiers : {[f['path'] for f in written_files]}")

    @pytest.mark.asyncio
    async def test_b_non_safe_action_with_confirmation(
        self, db_instance, temp_project_dir, orchestrator
    ):
        """
        Test B — Pipeline complet action NON-SAFE avec confirmation

        Scénario :
        1. Créer projet + conversation
        2. Mode PROJECT + Phase EXECUTION + Projet DEBT
        3. Envoyer message NON-SAFE (supprimer fichier)
        4. Vérifier challenge généré
        5. Vérifier action stockée dans _pending_actions
        6. Simuler confirmation (modifier flag confirmed=True)
        7. Relancer orchestration
        8. Vérifier exécution réelle après confirmation
        """
        # 1. Créer projet
        project = await db_instance.create_project(
            name="Test NON-SAFE Pipeline", path=temp_project_dir
        )
        project_id = project["id"]

        # Créer fichier existant à supprimer
        test_file = Path(temp_project_dir) / "old_file.py"
        test_file.write_text("# Fichier obsolète\nprint('old')\n", encoding="utf-8")
        assert test_file.exists()

        # 2. Créer conversation
        conversation = await db_instance.create_conversation(
            agent_id="JARVIS_Maître", project_id=project_id, title="Test NON-SAFE Action"
        )
        conversation_id = conversation["id"]

        # 3. Créer SessionState mode PROJECT + phase EXECUTION + DEBT
        session_state = SessionState(
            mode=Mode.PROJECT,
            conversation_id=conversation_id,
            project_id=project_id,
            phase=Phase.EXECUTION,
            project_state=ProjectState.DEBT,  # Projet avec dette
        )

        # 4. Créer FunctionExecutor
        function_executor = FunctionExecutor(db_instance=db_instance, project_path=temp_project_dir)

        # 5. Envoyer message NON-SAFE (action structurante)
        user_message = "Supprimer le fichier old_file.py qui est obsolète"

        await db_instance.add_message(conversation_id, "user", user_message)
        conversation_history = await db_instance.get_conversation_history(conversation_id)

        # 6. Appeler agent JARVIS_Maître
        agent = get_agent("JARVIS_Maître")
        response = await agent.handle(
            conversation_history, session_id=conversation_id, function_executor=function_executor
        )

        # 7. Orchestration : devrait détecter NON-SAFE et générer challenge
        final_response, delegation_results = await orchestrator.process_response(
            response=response,
            conversation_history=conversation_history,
            session_id=conversation_id,
            project_path=temp_project_dir,
            function_executor=function_executor,
            session_state=session_state,
        )

        # 8. Vérifier challenge généré (pas d'exécution)
        assert "⚠️" in final_response or "VALIDATION" in final_response
        assert delegation_results == [] or delegation_results is None

        # 9. Vérifier action stockée dans _pending_actions
        assert conversation_id in SimpleOrchestrator._pending_actions
        pending = SimpleOrchestrator._pending_actions[conversation_id]
        assert pending["confirmed"] is False
        assert "delegations" in pending
        assert "original_response" in pending  # Vérifier présence réponse originale

        print("\n✅ Test B NON-SAFE : Challenge généré, action stockée")
        print(f"   Réponse originale stockée : {len(pending['original_response'])} chars")

        # 10. Simuler confirmation utilisateur
        SimpleOrchestrator._pending_actions[conversation_id]["confirmed"] = True

        # 11. Relancer orchestration avec bypass_safety activé
        # Utiliser réponse originale (pas de reconstruction artificielle)
        original_response = pending["original_response"]

        # Relancer process_response avec réponse originale
        (
            final_response_confirmed,
            delegation_results_confirmed,
        ) = await orchestrator.process_response(
            response=original_response,
            conversation_history=conversation_history,
            session_id=conversation_id,
            project_path=temp_project_dir,
            function_executor=function_executor,
            session_state=session_state,
        )

        # 12. Vérifier exécution réelle après confirmation
        assert delegation_results_confirmed is not None
        assert len(delegation_results_confirmed) > 0

        # Vérifier délégation CODEUR exécutée
        codeur_delegations = [
            d for d in delegation_results_confirmed if d["agent_name"] == "CODEUR"
        ]
        assert len(codeur_delegations) > 0

        # 13. Vérifier action nettoyée de _pending_actions
        assert conversation_id not in SimpleOrchestrator._pending_actions

        # 14. Sauvegarder réponse en DB
        await db_instance.add_message(conversation_id, "assistant", final_response_confirmed)

        # 15. Vérifier DB
        messages = await db_instance.get_messages(conversation_id)
        assistant_messages = [m for m in messages if m["role"] == "assistant"]
        assert len(assistant_messages) >= 1

        print("✅ Test B NON-SAFE : Confirmation → Exécution réussie")
        print(f"   Délégations : {len(delegation_results_confirmed)}")
        print(f"   Action nettoyée : {conversation_id not in SimpleOrchestrator._pending_actions}")


# Tests peuvent être exécutés avec : pytest -v tests/test_system_full_pipeline.py
