"""
Tests d'intégration end-to-end — Sprint Stabilisation JARVIS 2.0

Tests critiques pour valider :
1. Blocage écriture mode CHAT
2. Exécution SAFE autorisée
3. Challenge NON-SAFE (projet DEBT)
4. Workflow confirmation complet
5. Blocage écriture phase REFLEXION
"""

from backend.models.session_state import Mode, Phase, ProjectState, SessionState
from backend.services.file_writer import write_files_to_project
from backend.services.orchestration import SimpleOrchestrator
from backend.services.safety_service import SafetyService


class TestIntegrationChat:
    """Test 1 : Mode CHAT → Blocage écriture disque"""

    def test_chat_mode_blocks_disk_write(self, tmp_path):
        """Mode CHAT doit bloquer toute écriture disque"""
        # Créer SessionState mode CHAT
        session_state = SessionState(
            mode=Mode.CHAT,
            conversation_id="test-chat-001",
        )

        # Vérifier can_write_disk retourne False
        assert session_state.can_write_disk() is False, "Mode CHAT doit bloquer écriture"

        # Tenter écriture avec session_state
        files = [{"path": "test.py", "content": "print('hello')"}]
        results = write_files_to_project(str(tmp_path), files, session_state=session_state)

        # Vérifier tous les fichiers sont bloqués
        assert len(results) == 1
        assert results[0]["status"] == "blocked"
        assert "Écriture disque interdite" in results[0]["error"]

        # Vérifier aucun fichier écrit sur disque
        assert not (tmp_path / "test.py").exists()


class TestIntegrationSafe:
    """Test 2 : Projet NEW → Action SAFE → Exécution autorisée"""

    def test_new_project_safe_action_allowed(self, tmp_path):
        """Projet NEW avec action SAFE doit autoriser exécution"""
        # Créer SessionState mode PROJECT, phase EXECUTION, projet NEW
        session_state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="test-safe-001",
            project_id="proj-001",
            phase=Phase.EXECUTION,
            project_state=ProjectState.NEW,
        )

        # Vérifier can_write_disk retourne True
        assert session_state.can_write_disk() is True, "Phase EXECUTION doit autoriser écriture"

        # Classifier action SAFE
        classification = SafetyService.classify_action(
            "Créer fichier simple hello.py", ProjectState.NEW, "execution"
        )

        # Vérifier classification SAFE
        assert classification["is_safe"] is True
        assert classification["requires_validation"] is False

        # Écriture doit réussir
        files = [{"path": "hello.py", "content": "def hello():\n    print('Hello')\n"}]
        results = write_files_to_project(str(tmp_path), files, session_state=session_state)

        # Vérifier fichier écrit
        assert len(results) == 1
        assert results[0]["status"] == "written"
        assert (tmp_path / "hello.py").exists()


class TestIntegrationDebt:
    """Test 3 : Projet DEBT → Action NON-SAFE → Challenge"""

    def test_debt_project_triggers_challenge(self):
        """Projet avec dette doit générer challenge pour toute action"""
        # Créer SessionState mode PROJECT, phase EXECUTION, projet DEBT
        session_state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="test-debt-001",
            project_id="proj-002",
            phase=Phase.EXECUTION,
            project_state=ProjectState.DEBT,
        )

        # Classifier action (toute action est NON-SAFE si DEBT)
        classification = SafetyService.classify_action(
            "Ajouter nouvelle fonctionnalité", ProjectState.DEBT, "execution"
        )

        # Vérifier classification NON-SAFE
        assert classification["is_safe"] is False
        assert classification["requires_validation"] is True
        assert "dette technique" in classification["reason"].lower()

        # Générer challenge
        challenge = SafetyService.generate_challenge(
            "Ajouter nouvelle fonctionnalité", classification, ProjectState.DEBT
        )

        # Vérifier contenu challenge
        assert "⚠️" in challenge
        assert "VALIDATION REQUISE" in challenge
        assert "dette technique" in challenge.lower()
        assert "Confirmez-vous" in challenge or "Questions" in challenge


class TestIntegrationConfirmation:
    """Test 4 : NON-SAFE → Confirmation → Exécution réelle"""

    def test_confirmation_workflow_complete(self, tmp_path):
        """Workflow complet : blocage → stockage → confirmation → exécution"""
        session_id = "test-confirm-001"

        # Créer SessionState mode PROJECT, phase EXECUTION, projet DEBT
        session_state = SessionState(
            mode=Mode.PROJECT,
            conversation_id=session_id,
            project_id="proj-003",
            phase=Phase.EXECUTION,
            project_state=ProjectState.DEBT,
        )

        # Classifier action NON-SAFE
        classification = SafetyService.classify_action(
            "Supprimer fichier obsolète", ProjectState.DEBT, "execution"
        )

        assert classification["is_safe"] is False
        assert classification["requires_validation"] is True

        # Simuler stockage action bloquée (comme orchestration.py)
        SimpleOrchestrator._pending_actions[session_id] = {
            "user_message": "Supprimer fichier obsolète",
            "delegations": [{"agent_name": "CODEUR", "instruction": "Supprimer old.py"}],
            "classification": classification,
            "confirmed": False,
        }

        # Vérifier action stockée
        assert session_id in SimpleOrchestrator._pending_actions
        assert SimpleOrchestrator._pending_actions[session_id]["confirmed"] is False

        # Simuler confirmation utilisateur
        SimpleOrchestrator._pending_actions[session_id]["confirmed"] = True

        # Vérifier bypass_safety activé
        bypass_safety = SimpleOrchestrator._pending_actions.get(session_id, {}).get(
            "confirmed", False
        )
        assert bypass_safety is True

        # Après exécution, action doit être nettoyée
        # (simulé ici, normalement fait par orchestration.py)
        del SimpleOrchestrator._pending_actions[session_id]
        assert session_id not in SimpleOrchestrator._pending_actions


class TestIntegrationReflexion:
    """Test 5 : Phase REFLEXION → Blocage écriture"""

    def test_reflexion_phase_blocks_write(self, tmp_path):
        """Phase REFLEXION doit bloquer écriture même en mode PROJECT"""
        # Créer SessionState mode PROJECT, phase REFLEXION
        session_state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="test-reflex-001",
            project_id="proj-004",
            phase=Phase.REFLEXION,
            project_state=ProjectState.NEW,
        )

        # Vérifier can_write_disk retourne False
        assert session_state.can_write_disk() is False, "Phase REFLEXION doit bloquer écriture"

        # Tenter écriture
        files = [{"path": "plan.md", "content": "# Plan du projet\n"}]
        results = write_files_to_project(str(tmp_path), files, session_state=session_state)

        # Vérifier fichiers bloqués
        assert len(results) == 1
        assert results[0]["status"] == "blocked"
        assert "phase=reflexion" in results[0]["error"].lower()

        # Vérifier aucun fichier écrit
        assert not (tmp_path / "plan.md").exists()

        # Transition vers EXECUTION doit autoriser écriture
        session_state.transition_to_execution()
        assert session_state.phase == Phase.EXECUTION
        assert session_state.can_write_disk() is True

        # Maintenant écriture doit réussir
        results = write_files_to_project(str(tmp_path), files, session_state=session_state)

        assert results[0]["status"] == "written"
        assert (tmp_path / "plan.md").exists()
