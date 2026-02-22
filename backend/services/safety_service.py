"""
Service de classification sécurité JARVIS 2.0

Responsabilités :
- Classification SAFE / NON-SAFE
- Génération messages challenge utilisateur

Interdictions :
- Pas d'écriture disque
- Pas de modification état
- Pas d'appel orchestration

Ce service retourne des classifications et messages. Point.
"""


from backend.models.session_state import ProjectState


class SafetyService:
    """Service de classification sécurité"""

    # Actions SAFE (exécution autorisée sans validation)
    SAFE_ACTIONS = {
        "créer fichier simple",
        "ajouter fonction",
        "ajouter classe",
        "ajouter test",
        "corriger typo",
        "ajouter docstring",
        "formater code",
    }

    # Mots-clés NON-SAFE (validation requise)
    NON_SAFE_KEYWORDS = {
        "supprimer",
        "refactoriser",
        "renommer",
        "déplacer",
        "modifier structure",
        "changer architecture",
        "migration",
        "base de données",
        "sécurité",
        "authentification",
    }

    @staticmethod
    def classify_action(user_message: str, project_state: ProjectState, phase: str) -> dict:
        """
        Classifie action : SAFE ou NON-SAFE
        Returns: dict avec is_safe, reason, requires_validation
        """
        message_lower = user_message.lower()

        # Règle 1 : Projet avec dette → toujours NON-SAFE
        if project_state == ProjectState.DEBT:
            return {
                "is_safe": False,
                "reason": "Projet avec dette technique détectée",
                "requires_validation": True,
            }

        # Règle 2 : Mots-clés NON-SAFE détectés
        for keyword in SafetyService.NON_SAFE_KEYWORDS:
            if keyword in message_lower:
                return {
                    "is_safe": False,
                    "reason": f"Action structurante détectée : {keyword}",
                    "requires_validation": True,
                }

        # Règle 3 : Actions SAFE explicites
        for safe_action in SafetyService.SAFE_ACTIONS:
            if safe_action in message_lower:
                return {
                    "is_safe": True,
                    "reason": f"Action simple détectée : {safe_action}",
                    "requires_validation": False,
                }

        # Règle 4 : Nouveau projet → SAFE par défaut
        if project_state == ProjectState.NEW:
            return {
                "is_safe": True,
                "reason": "Nouveau projet, création initiale",
                "requires_validation": False,
            }

        # Règle 5 : Ambiguïté → NON-SAFE (principe précaution)
        return {
            "is_safe": False,
            "reason": "Action ambiguë, clarification nécessaire",
            "requires_validation": True,
        }

    @staticmethod
    def generate_challenge(
        user_message: str, classification: dict, project_state: ProjectState | None = None
    ) -> str:
        """Génère message challenge. Returns: str formaté"""
        reason = classification.get("reason", "Action non classifiée")
        msg_preview = user_message[:100]

        # Challenge projet avec dette
        if project_state == ProjectState.DEBT:
            return f"""⚠️ **VALIDATION REQUISE**

**Raison** : {reason}

Votre projet contient de la dette technique. Avant d'exécuter cette action, je dois m'assurer qu'elle ne va pas aggraver la situation.

**Votre demande** : {msg_preview}

**Questions** :
1. Cette action est-elle critique pour votre besoin actuel ?
2. Souhaitez-vous d'abord traiter la dette technique détectée ?
3. Confirmez-vous l'exécution malgré la dette ?

Répondez pour continuer."""

        # Challenge action structurante
        if "structurante" in reason or "ambiguë" in reason:
            return f"""⚠️ **CLARIFICATION NÉCESSAIRE**

**Raison** : {reason}

**Votre demande** : {msg_preview}

**Questions** :
1. Quels fichiers/modules seront impactés ?
2. Y a-t-il des dépendances à considérer ?
3. Confirmez-vous cette action ?

Répondez pour continuer."""

        # Challenge générique
        return f"""⚠️ **VALIDATION REQUISE**

**Raison** : {reason}

**Votre demande** : {msg_preview}

Confirmez-vous cette action ?

Répondez pour continuer."""
