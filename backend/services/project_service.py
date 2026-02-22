"""
Service d'analyse de projet JARVIS 2.0

Responsabilités :
- Analyse état projet (NEW, CLEAN, DEBT)
- Audit dette technique
- Enrichissement contexte projet

Interdictions :
- Pas de décision d'exécution
- Pas d'appel safety_service
- Pas de modification session_state
- Pas d'écriture disque

Ce service retourne des données. Point.
"""

import os
from pathlib import Path

from backend.models.session_state import ProjectState
from backend.services.project_context import format_file_tree


class ProjectService:
    """Service d'analyse de projet"""

    # Extensions analysées pour dette technique
    CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx"}

    # Patterns dette technique (simple mais efficace)
    DEBT_PATTERNS = {
        "TODO": "Tâche non terminée",
        "FIXME": "Bug connu à corriger",
        "HACK": "Solution temporaire",
        "XXX": "Code problématique",
        "DEPRECATED": "Code obsolète",
        "# type: ignore": "Erreur type ignorée",
        "any": "Type any (Python/TS)",
        "console.log": "Debug oublié (JS)",
        "print(": "Debug oublié (Python)",
    }

    @staticmethod
    def analyze_project_state(project_path: str) -> ProjectState:
        """
        Analyse l'état du projet

        Args:
            project_path: Chemin absolu du projet

        Returns:
            ProjectState (NEW, CLEAN, DEBT)

        Règles :
            - Dossier vide ou <3 fichiers code → NEW
            - Fichiers code sans dette → CLEAN
            - Dette détectée → DEBT
        """
        if not os.path.exists(project_path):
            return ProjectState.NEW

        # Compter fichiers code
        code_files = ProjectService._list_code_files(project_path)

        if len(code_files) < 3:
            return ProjectState.NEW

        # Analyser dette
        debt_report = ProjectService.analyze_debt(project_path)

        if debt_report["total_issues"] > 0:
            return ProjectState.DEBT

        return ProjectState.CLEAN

    @staticmethod
    def analyze_debt(project_path: str) -> dict:
        """
        Audit dette technique

        Returns: dict avec total_issues, files_with_debt, debt_by_type, summary
        """
        if not os.path.exists(project_path):
            return {
                "total_issues": 0,
                "files_with_debt": [],
                "debt_by_type": {},
                "summary": "Projet inexistant",
            }

        code_files = ProjectService._list_code_files(project_path)
        if not code_files:
            return {
                "total_issues": 0,
                "files_with_debt": [],
                "debt_by_type": {},
                "summary": "Aucun fichier code",
            }

        files_with_debt = []
        debt_by_type = dict.fromkeys(ProjectService.DEBT_PATTERNS, 0)

        for file_path in code_files:
            try:
                with open(file_path, encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                file_issues = []
                for pattern in ProjectService.DEBT_PATTERNS:
                    count = content.count(pattern)
                    if count > 0:
                        debt_by_type[pattern] += count
                        file_issues.append(f"{pattern} ({count})")

                if file_issues:
                    files_with_debt.append(
                        {
                            "path": os.path.relpath(file_path, project_path),
                            "issues": file_issues,
                        }
                    )
            except Exception:
                continue

        total_issues = sum(debt_by_type.values())

        if total_issues == 0:
            summary = "✅ Aucune dette technique détectée"
        else:
            top_issues = sorted(
                [(k, v) for k, v in debt_by_type.items() if v > 0], key=lambda x: x[1], reverse=True
            )[:3]
            summary = f"⚠️ {total_issues} problème(s) : " + ", ".join(
                [f"{k} ({v})" for k, v in top_issues]
            )

        return {
            "total_issues": total_issues,
            "files_with_debt": files_with_debt,
            "debt_by_type": {k: v for k, v in debt_by_type.items() if v > 0},
            "summary": summary,
        }

    @staticmethod
    def build_enriched_context(
        project: dict,
        file_tree: dict,
        project_state: ProjectState,
        debt_report: dict | None = None,
    ) -> str:
        """
        Construit contexte projet enrichi

        Args:
            project: Dict projet depuis Database
            file_tree: Arborescence fichiers
            project_state: État projet (NEW, CLEAN, DEBT)
            debt_report: Rapport dette (optionnel)

        Returns:
            Contexte enrichi (max 1500 chars)
        """
        # GARDE CRITIQUE : Vérifier project existe avant toute manipulation
        if not project or not isinstance(project, dict):
            return "MODE PROJET: Méthodologie obligatoire\nÉTAT: Projet non trouvé"
        
        # Extraction description sécurisée (gérer None explicitement)
        desc_raw = project.get("description") or ""
        description = desc_raw[:80] if desc_raw else "Nouveau projet"
        if not description:
            description = "Nouveau projet"

        # Arborescence compressée
        tree_output = format_file_tree(file_tree, max_depth=3, max_files=50)
        if len(tree_output) > 600:
            tree_output = tree_output[:600] + "\n..."

        # État projet
        state_label = {
            ProjectState.NEW: "NOUVEAU (dossier vide)",
            ProjectState.CLEAN: "PROPRE (sans dette)",
            ProjectState.DEBT: "DETTE DÉTECTÉE",
        }[project_state]

        # Contexte de base
        context = f"""PROJET: {project["name"]}
PATH: {project["path"]}
DESC: {description}
ÉTAT: {state_label}

STRUCTURE:
{tree_output}

MODE PROJET: Méthodologie obligatoire"""

        # Ajouter dette si présente
        if project_state == ProjectState.DEBT and debt_report:
            debt_summary = debt_report.get("summary", "")
            if debt_summary and len(context) + len(debt_summary) < 1400:
                context += f"\n\nDETTE: {debt_summary}"

        # Limite finale
        if len(context) > 1500:
            context = context[:1500]

        return context

    @staticmethod
    def _list_code_files(project_path: str, max_files: int = 100) -> list[str]:
        """
        Liste fichiers code du projet

        Args:
            project_path: Chemin projet
            max_files: Limite fichiers (performance)

        Returns:
            Liste chemins absolus fichiers code
        """
        code_files = []

        try:
            for root, dirs, files in os.walk(project_path):
                # Ignorer dossiers cachés et dépendances
                dirs[:] = [
                    d
                    for d in dirs
                    if not d.startswith(".")
                    and d not in {"node_modules", "venv", "__pycache__", "dist", "build"}
                ]

                for file in files:
                    if len(code_files) >= max_files:
                        break

                    ext = Path(file).suffix
                    if ext in ProjectService.CODE_EXTENSIONS:
                        code_files.append(os.path.join(root, file))

                if len(code_files) >= max_files:
                    break

        except Exception:
            # Erreur accès dossier, retourner ce qu'on a
            pass

        return code_files
