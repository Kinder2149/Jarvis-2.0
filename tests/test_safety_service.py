"""
Tests unitaires pour backend/services/safety_service.py

Couvre :
- Classification SAFE/NON-SAFE
- Règles dette technique
- Règles mots-clés NON-SAFE
- Règles actions SAFE
- Génération messages challenge
"""

from backend.models.session_state import ProjectState
from backend.services.safety_service import SafetyService


class TestClassifyAction:
    """Tests classification SAFE/NON-SAFE"""

    def test_debt_project_always_non_safe(self):
        """Projet avec dette → toujours NON-SAFE"""
        result = SafetyService.classify_action(
            "Ajouter une fonction simple", ProjectState.DEBT, "execution"
        )

        assert result["is_safe"] is False
        assert "dette technique" in result["reason"]
        assert result["requires_validation"] is True

    def test_non_safe_keyword_supprimer(self):
        """Mot-clé 'supprimer' → NON-SAFE"""
        result = SafetyService.classify_action(
            "Supprimer le fichier config.py", ProjectState.CLEAN, "execution"
        )

        assert result["is_safe"] is False
        assert "supprimer" in result["reason"]
        assert result["requires_validation"] is True

    def test_non_safe_keyword_refactoriser(self):
        """Mot-clé 'refactoriser' → NON-SAFE"""
        result = SafetyService.classify_action(
            "Refactoriser la structure du projet", ProjectState.CLEAN, "execution"
        )

        assert result["is_safe"] is False
        assert "refactoriser" in result["reason"]
        assert result["requires_validation"] is True

    def test_safe_action_creer_fichier(self):
        """Action SAFE 'créer fichier simple' → SAFE"""
        result = SafetyService.classify_action(
            "Créer fichier simple hello.py", ProjectState.CLEAN, "execution"
        )

        assert result["is_safe"] is True
        assert "créer fichier simple" in result["reason"]
        assert result["requires_validation"] is False

    def test_safe_action_ajouter_fonction(self):
        """Action SAFE 'ajouter fonction' → SAFE"""
        result = SafetyService.classify_action(
            "Ajouter fonction calculate() dans utils.py", ProjectState.CLEAN, "execution"
        )

        assert result["is_safe"] is True
        assert "ajouter fonction" in result["reason"]
        assert result["requires_validation"] is False

    def test_new_project_safe_by_default(self):
        """Nouveau projet → SAFE par défaut"""
        result = SafetyService.classify_action(
            "Créer la structure du projet", ProjectState.NEW, "execution"
        )

        assert result["is_safe"] is True
        assert "Nouveau projet" in result["reason"]
        assert result["requires_validation"] is False

    def test_ambiguous_action_non_safe(self):
        """Action ambiguë → NON-SAFE (principe précaution)"""
        result = SafetyService.classify_action("Améliorer le code", ProjectState.CLEAN, "execution")

        assert result["is_safe"] is False
        assert "ambiguë" in result["reason"]
        assert result["requires_validation"] is True

    def test_multiple_non_safe_keywords(self):
        """Plusieurs mots-clés NON-SAFE → NON-SAFE"""
        result = SafetyService.classify_action(
            "Supprimer et refactoriser le module auth", ProjectState.CLEAN, "execution"
        )

        assert result["is_safe"] is False
        assert result["requires_validation"] is True


class TestGenerateChallenge:
    """Tests génération messages challenge"""

    def test_challenge_debt_project(self):
        """Challenge projet avec dette"""
        classification = {
            "is_safe": False,
            "reason": "Projet avec dette technique détectée",
            "requires_validation": True,
        }

        challenge = SafetyService.generate_challenge(
            "Ajouter une nouvelle fonctionnalité", classification, ProjectState.DEBT
        )

        assert "⚠️" in challenge
        assert "VALIDATION REQUISE" in challenge
        assert "dette technique" in challenge
        assert "Ajouter une nouvelle fonctionnalité" in challenge
        assert "Questions" in challenge

    def test_challenge_structural_action(self):
        """Challenge action structurante"""
        classification = {
            "is_safe": False,
            "reason": "Action structurante détectée : refactoriser",
            "requires_validation": True,
        }

        challenge = SafetyService.generate_challenge(
            "Refactoriser le code", classification, ProjectState.CLEAN
        )

        assert "⚠️" in challenge
        assert "CLARIFICATION NÉCESSAIRE" in challenge
        assert "structurante" in challenge
        assert "Refactoriser le code" in challenge
        assert "fichiers/modules" in challenge

    def test_challenge_ambiguous_action(self):
        """Challenge action ambiguë"""
        classification = {
            "is_safe": False,
            "reason": "Action ambiguë, clarification nécessaire",
            "requires_validation": True,
        }

        challenge = SafetyService.generate_challenge(
            "Améliorer le projet", classification, ProjectState.CLEAN
        )

        assert "⚠️" in challenge
        assert "CLARIFICATION NÉCESSAIRE" in challenge
        assert "ambiguë" in challenge
        assert "Améliorer le projet" in challenge

    def test_challenge_generic(self):
        """Challenge générique"""
        classification = {
            "is_safe": False,
            "reason": "Autre raison",
            "requires_validation": True,
        }

        challenge = SafetyService.generate_challenge(
            "Faire quelque chose", classification, ProjectState.CLEAN
        )

        assert "⚠️" in challenge
        assert "VALIDATION REQUISE" in challenge
        assert "Faire quelque chose" in challenge
        assert "Confirmez-vous cette action" in challenge

    def test_challenge_truncates_long_message(self):
        """Message long tronqué à 100 chars"""
        long_message = "B" * 200
        classification = {
            "is_safe": False,
            "reason": "Test",
            "requires_validation": True,
        }

        challenge = SafetyService.generate_challenge(
            long_message, classification, ProjectState.CLEAN
        )

        # Vérifier que le message est tronqué à 100 chars
        assert long_message[:100] in challenge
        # Vérifier qu'il n'y a pas plus de 100 'B' consécutifs
        assert "B" * 101 not in challenge


class TestSafetyRules:
    """Tests règles métier sécurité"""

    def test_safe_actions_list(self):
        """Vérifier liste actions SAFE"""
        assert "créer fichier simple" in SafetyService.SAFE_ACTIONS
        assert "ajouter fonction" in SafetyService.SAFE_ACTIONS
        assert "ajouter classe" in SafetyService.SAFE_ACTIONS
        assert "ajouter test" in SafetyService.SAFE_ACTIONS
        assert "corriger typo" in SafetyService.SAFE_ACTIONS

    def test_non_safe_keywords_list(self):
        """Vérifier liste mots-clés NON-SAFE"""
        assert "supprimer" in SafetyService.NON_SAFE_KEYWORDS
        assert "refactoriser" in SafetyService.NON_SAFE_KEYWORDS
        assert "renommer" in SafetyService.NON_SAFE_KEYWORDS
        assert "migration" in SafetyService.NON_SAFE_KEYWORDS
        assert "base de données" in SafetyService.NON_SAFE_KEYWORDS

    def test_case_insensitive_detection(self):
        """Détection insensible à la casse"""
        result_lower = SafetyService.classify_action(
            "supprimer fichier", ProjectState.CLEAN, "execution"
        )

        result_upper = SafetyService.classify_action(
            "SUPPRIMER FICHIER", ProjectState.CLEAN, "execution"
        )

        assert result_lower["is_safe"] == result_upper["is_safe"]
        assert result_lower["requires_validation"] == result_upper["requires_validation"]
