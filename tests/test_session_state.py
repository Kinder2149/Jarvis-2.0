"""
Tests unitaires pour backend/models/session_state.py

Couvre :
- Création SessionState (CHAT et PROJECT)
- Validation cohérence état
- Transitions de phase
- Gate validation
- Autorisation écriture disque
- Sérialisation
- Factory from_conversation
"""

import pytest

from backend.models.session_state import (
    Mode,
    Phase,
    ProjectState,
    SessionState,
)


class TestSessionStateCreation:
    """Tests création et validation cohérence"""

    def test_create_chat_mode_valid(self):
        """Mode CHAT : création valide sans phase ni project_id"""
        state = SessionState(
            mode=Mode.CHAT,
            conversation_id="conv-123",
        )

        assert state.mode == Mode.CHAT
        assert state.conversation_id == "conv-123"
        assert state.phase is None
        assert state.project_state is None
        assert state.project_id is None

    def test_create_chat_mode_with_phase_raises(self):
        """Mode CHAT : erreur si phase fournie"""
        with pytest.raises(ValueError, match="Mode CHAT ne peut pas avoir de phase"):
            SessionState(
                mode=Mode.CHAT,
                conversation_id="conv-123",
                phase=Phase.REFLEXION,
            )

    def test_create_chat_mode_with_project_state_raises(self):
        """Mode CHAT : erreur si project_state fourni"""
        with pytest.raises(ValueError, match="Mode CHAT ne peut pas avoir de project_state"):
            SessionState(
                mode=Mode.CHAT,
                conversation_id="conv-123",
                project_state=ProjectState.NEW,
            )

    def test_create_chat_mode_with_project_id_raises(self):
        """Mode CHAT : erreur si project_id fourni"""
        with pytest.raises(ValueError, match="Mode CHAT ne peut pas avoir de project_id"):
            SessionState(
                mode=Mode.CHAT,
                conversation_id="conv-123",
                project_id="proj-456",
            )

    def test_create_project_mode_valid(self):
        """Mode PROJECT : création valide avec phase et project_id"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.REFLEXION,
        )

        assert state.mode == Mode.PROJECT
        assert state.conversation_id == "conv-123"
        assert state.project_id == "proj-456"
        assert state.phase == Phase.REFLEXION
        assert state.project_state is None  # Pas encore analysé

    def test_create_project_mode_without_phase_raises(self):
        """Mode PROJECT : erreur si phase manquante"""
        with pytest.raises(ValueError, match="Mode PROJECT requiert une phase"):
            SessionState(
                mode=Mode.PROJECT,
                conversation_id="conv-123",
                project_id="proj-456",
            )

    def test_create_project_mode_without_project_id_raises(self):
        """Mode PROJECT : erreur si project_id manquant"""
        with pytest.raises(ValueError, match="Mode PROJECT requiert un project_id"):
            SessionState(
                mode=Mode.PROJECT,
                conversation_id="conv-123",
                phase=Phase.REFLEXION,
            )


class TestPhaseTransitions:
    """Tests transitions de phase"""

    def test_transition_reflexion_to_execution(self):
        """Transition REFLEXION → EXECUTION valide"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.REFLEXION,
        )

        state.transition_to_execution()

        assert state.phase == Phase.EXECUTION

    def test_transition_execution_to_reflexion(self):
        """Transition EXECUTION → REFLEXION valide (retour arrière)"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.EXECUTION,
        )

        state.transition_to_reflexion()

        assert state.phase == Phase.REFLEXION

    def test_transition_to_execution_from_chat_raises(self):
        """Transition phase impossible en mode CHAT"""
        state = SessionState(
            mode=Mode.CHAT,
            conversation_id="conv-123",
        )

        with pytest.raises(ValueError, match="Transition phase uniquement en mode PROJECT"):
            state.transition_to_execution()

    def test_transition_to_execution_from_execution_raises(self):
        """Transition EXECUTION → EXECUTION impossible"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.EXECUTION,
        )

        with pytest.raises(ValueError, match="Transition EXECUTION impossible depuis phase"):
            state.transition_to_execution()

    def test_transition_to_reflexion_from_reflexion_raises(self):
        """Transition REFLEXION → REFLEXION impossible"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.REFLEXION,
        )

        with pytest.raises(ValueError, match="Transition REFLEXION impossible depuis phase"):
            state.transition_to_reflexion()


class TestProjectState:
    """Tests gestion project_state"""

    def test_set_project_state_valid(self):
        """Définition project_state valide en mode PROJECT"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.REFLEXION,
        )

        state.set_project_state(ProjectState.CLEAN)

        assert state.project_state == ProjectState.CLEAN

    def test_set_project_state_in_chat_raises(self):
        """Définition project_state impossible en mode CHAT"""
        state = SessionState(
            mode=Mode.CHAT,
            conversation_id="conv-123",
        )

        with pytest.raises(ValueError, match="project_state uniquement en mode PROJECT"):
            state.set_project_state(ProjectState.NEW)


class TestValidationGate:
    """Tests gate de validation"""

    def test_require_validation_chat_mode(self):
        """Mode CHAT : jamais de validation"""
        state = SessionState(
            mode=Mode.CHAT,
            conversation_id="conv-123",
        )

        assert state.require_validation() is False

    def test_require_validation_reflexion_phase(self):
        """Phase REFLEXION : jamais de validation"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.REFLEXION,
        )

        assert state.require_validation() is False

    def test_require_validation_execution_with_debt(self):
        """Phase EXECUTION + Projet DEBT : validation requise"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.EXECUTION,
            project_state=ProjectState.DEBT,
        )

        assert state.require_validation() is True

    def test_require_validation_execution_new_project(self):
        """Phase EXECUTION + Projet NEW : pas de validation (SafetyService décidera)"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.EXECUTION,
            project_state=ProjectState.NEW,
        )

        assert state.require_validation() is False

    def test_require_validation_execution_clean_project(self):
        """Phase EXECUTION + Projet CLEAN : pas de validation (SafetyService décidera)"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.EXECUTION,
            project_state=ProjectState.CLEAN,
        )

        assert state.require_validation() is False


class TestDiskWriteAuthorization:
    """Tests autorisation écriture disque"""

    def test_can_write_disk_chat_mode(self):
        """Mode CHAT : jamais d'écriture disque"""
        state = SessionState(
            mode=Mode.CHAT,
            conversation_id="conv-123",
        )

        assert state.can_write_disk() is False

    def test_can_write_disk_reflexion_phase(self):
        """Phase REFLEXION : jamais d'écriture disque"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.REFLEXION,
        )

        assert state.can_write_disk() is False

    def test_can_write_disk_execution_phase(self):
        """Phase EXECUTION : écriture disque autorisée"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.EXECUTION,
        )

        assert state.can_write_disk() is True


class TestSerialization:
    """Tests sérialisation"""

    def test_to_dict_chat_mode(self):
        """Sérialisation mode CHAT"""
        state = SessionState(
            mode=Mode.CHAT,
            conversation_id="conv-123",
        )

        data = state.to_dict()

        assert data == {
            "mode": "chat",
            "phase": None,
            "project_state": None,
            "conversation_id": "conv-123",
            "project_id": None,
        }

    def test_to_dict_project_mode(self):
        """Sérialisation mode PROJECT"""
        state = SessionState(
            mode=Mode.PROJECT,
            conversation_id="conv-123",
            project_id="proj-456",
            phase=Phase.EXECUTION,
            project_state=ProjectState.CLEAN,
        )

        data = state.to_dict()

        assert data == {
            "mode": "project",
            "phase": "execution",
            "project_state": "clean",
            "conversation_id": "conv-123",
            "project_id": "proj-456",
        }


class TestFactory:
    """Tests factory from_conversation"""

    def test_from_conversation_chat_mode(self):
        """Factory : conversation sans project_id → mode CHAT"""
        conversation = {
            "id": "conv-123",
            "agent_id": "JARVIS_Maître",
            "project_id": None,
        }

        state = SessionState.from_conversation(conversation)

        assert state.mode == Mode.CHAT
        assert state.conversation_id == "conv-123"
        assert state.project_id is None
        assert state.phase is None
        assert state.project_state is None

    def test_from_conversation_project_mode(self):
        """Factory : conversation avec project_id → mode PROJECT"""
        conversation = {
            "id": "conv-123",
            "agent_id": "JARVIS_Maître",
            "project_id": "proj-456",
        }

        state = SessionState.from_conversation(conversation)

        assert state.mode == Mode.PROJECT
        assert state.conversation_id == "conv-123"
        assert state.project_id == "proj-456"
        assert state.phase == Phase.REFLEXION  # Phase par défaut
        assert state.project_state is None  # Pas encore analysé
