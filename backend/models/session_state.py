"""
Modèle d'état de session JARVIS 2.0

Responsabilités :
- Définition des états (Mode, Phase, ProjectState)
- Gestion des transitions d'état
- Validation des transitions
- Gate de validation pour actions critiques

Interdictions :
- Pas de logique métier (SAFE/NON-SAFE)
- Pas d'analyse projet
- Pas d'audit dette
- Pas d'orchestration
- Pas d'écriture disque

C'est un modèle d'état pur, pas un moteur métier.
"""

from dataclasses import dataclass
from enum import Enum


class Mode(str, Enum):
    """Mode de fonctionnement JARVIS"""

    CHAT = "chat"
    PROJECT = "project"


class Phase(str, Enum):
    """Phase interne du mode PROJECT"""

    REFLEXION = "reflexion"
    EXECUTION = "execution"


class ProjectState(str, Enum):
    """État du projet analysé"""

    NEW = "new"  # Dossier vide ou quasi-vide
    CLEAN = "clean"  # Code existant sans dette
    DEBT = "debt"  # Dette technique détectée


@dataclass
class SessionState:
    """
    État de session JARVIS

    Attributes:
        mode: Mode actuel (CHAT ou PROJECT)
        phase: Phase actuelle (REFLEXION ou EXECUTION, uniquement en mode PROJECT)
        project_state: État du projet (uniquement en mode PROJECT)
        conversation_id: ID de la conversation
        project_id: ID du projet (None en mode CHAT)
    """

    mode: Mode
    conversation_id: str
    project_id: str | None = None
    phase: Phase | None = None
    project_state: ProjectState | None = None

    def __post_init__(self):
        """Validation cohérence état après initialisation"""
        if self.mode == Mode.CHAT:
            # Mode CHAT : pas de phase, pas de project_state, pas de project_id
            if self.phase is not None:
                raise ValueError("Mode CHAT ne peut pas avoir de phase")
            if self.project_state is not None:
                raise ValueError("Mode CHAT ne peut pas avoir de project_state")
            if self.project_id is not None:
                raise ValueError("Mode CHAT ne peut pas avoir de project_id")

        elif self.mode == Mode.PROJECT:
            # Mode PROJECT : phase obligatoire, project_id obligatoire
            if self.phase is None:
                raise ValueError("Mode PROJECT requiert une phase")
            if self.project_id is None:
                raise ValueError("Mode PROJECT requiert un project_id")
            # project_state peut être None temporairement (avant analyse)

    def transition_to_execution(self) -> None:
        """
        Transition REFLEXION → EXECUTION

        Raises:
            ValueError: Si transition invalide
        """
        if self.mode != Mode.PROJECT:
            raise ValueError("Transition phase uniquement en mode PROJECT")
        if self.phase != Phase.REFLEXION:
            raise ValueError(f"Transition EXECUTION impossible depuis phase {self.phase}")

        self.phase = Phase.EXECUTION

    def transition_to_reflexion(self) -> None:
        """
        Transition EXECUTION → REFLEXION (retour arrière)

        Raises:
            ValueError: Si transition invalide
        """
        if self.mode != Mode.PROJECT:
            raise ValueError("Transition phase uniquement en mode PROJECT")
        if self.phase != Phase.EXECUTION:
            raise ValueError(f"Transition REFLEXION impossible depuis phase {self.phase}")

        self.phase = Phase.REFLEXION

    def set_project_state(self, state: ProjectState) -> None:
        """
        Définit l'état du projet après analyse

        Args:
            state: État du projet (NEW, CLEAN, DEBT)

        Raises:
            ValueError: Si mode invalide
        """
        if self.mode != Mode.PROJECT:
            raise ValueError("project_state uniquement en mode PROJECT")

        self.project_state = state

    def require_validation(self) -> bool:
        """
        Gate de validation : détermine si une validation utilisateur est requise

        Returns:
            True si validation requise, False sinon

        Règles :
            - Mode CHAT : jamais de validation (pas d'exécution)
            - Mode PROJECT + Phase REFLEXION : jamais de validation (pas d'exécution)
            - Mode PROJECT + Phase EXECUTION + Projet avec DEBT : validation requise
            - Mode PROJECT + Phase EXECUTION + Projet NEW/CLEAN : dépend de SafetyService
        """
        if self.mode == Mode.CHAT:
            return False

        if self.phase == Phase.REFLEXION:
            return False

        # Phase EXECUTION
        if self.project_state == ProjectState.DEBT:
            # Projet avec dette : validation systématique
            return True

        # Projet NEW ou CLEAN : validation dépend de SafetyService (NON-SAFE)
        # Cette méthode ne décide pas, elle retourne False (SafetyService décidera)
        return False

    def can_write_disk(self) -> bool:
        """
        Détermine si l'écriture disque est autorisée

        Returns:
            True si écriture autorisée, False sinon

        Règles :
            - Mode CHAT : jamais d'écriture
            - Mode PROJECT + Phase REFLEXION : jamais d'écriture
            - Mode PROJECT + Phase EXECUTION : écriture autorisée
        """
        if self.mode == Mode.CHAT:
            return False

        if self.phase == Phase.REFLEXION:
            return False

        # Phase EXECUTION
        return True

    def to_dict(self) -> dict:
        """Sérialisation pour logs et API"""
        return {
            "mode": self.mode.value,
            "phase": self.phase.value if self.phase else None,
            "project_state": self.project_state.value if self.project_state else None,
            "conversation_id": self.conversation_id,
            "project_id": self.project_id,
        }

    @classmethod
    def from_conversation(cls, conversation: dict) -> "SessionState":
        """
        Factory : crée SessionState depuis une conversation DB

        Args:
            conversation: Dict conversation depuis Database

        Returns:
            SessionState initialisé
        """
        project_id = conversation.get("project_id")

        if project_id:
            # Mode PROJECT : phase REFLEXION par défaut
            return cls(
                mode=Mode.PROJECT,
                conversation_id=conversation["id"],
                project_id=project_id,
                phase=Phase.REFLEXION,
                project_state=None,  # Sera défini après analyse
            )
        else:
            # Mode CHAT
            return cls(
                mode=Mode.CHAT,
                conversation_id=conversation["id"],
            )
