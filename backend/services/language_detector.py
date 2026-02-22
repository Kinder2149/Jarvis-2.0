"""
Détection automatique du langage et framework d'un projet.
"""

import json
from pathlib import Path


def detect_language_and_framework(project_path: str) -> dict:
    """
    Détecte le langage et le framework d'un projet.

    Returns:
        dict: {
            "language": "python" | "javascript" | "typescript" | "unknown",
            "framework": "fastapi" | "flask" | "express" | "react" | "none" | "unknown",
            "test_framework": "pytest" | "jest" | "mocha" | "none" | "unknown",
            "confidence": float (0-1)
        }
    """
    project_path = Path(project_path)

    # Vérifier fichiers de configuration
    has_package_json = (project_path / "package.json").exists()
    has_requirements_txt = (project_path / "requirements.txt").exists()
    has_pyproject_toml = (project_path / "pyproject.toml").exists()
    has_tsconfig = (project_path / "tsconfig.json").exists()

    # Détection langage
    language = "unknown"
    framework = "unknown"
    test_framework = "unknown"
    confidence = 0.0

    # JavaScript/TypeScript
    if has_package_json:
        language = "typescript" if has_tsconfig else "javascript"
        confidence = 0.9

        # Lire package.json pour détecter framework
        try:
            with open(project_path / "package.json", encoding="utf-8") as f:
                package_data = json.load(f)
                deps = {
                    **package_data.get("dependencies", {}),
                    **package_data.get("devDependencies", {}),
                }

                if "express" in deps:
                    framework = "express"
                elif "react" in deps:
                    framework = "react"
                elif "next" in deps:
                    framework = "nextjs"
                elif "vue" in deps:
                    framework = "vue"
                else:
                    framework = "none"

                if "jest" in deps:
                    test_framework = "jest"
                elif "mocha" in deps:
                    test_framework = "mocha"
                else:
                    test_framework = "none"
        except Exception:
            pass

    # Python
    elif has_requirements_txt or has_pyproject_toml:
        language = "python"
        confidence = 0.9

        # Lire requirements.txt pour détecter framework
        requirements_content = ""
        if has_requirements_txt:
            try:
                with open(project_path / "requirements.txt", encoding="utf-8") as f:
                    requirements_content = f.read().lower()
            except Exception:
                pass

        if "fastapi" in requirements_content:
            framework = "fastapi"
        elif "flask" in requirements_content:
            framework = "flask"
        elif "django" in requirements_content:
            framework = "django"
        else:
            framework = "none"

        if "pytest" in requirements_content:
            test_framework = "pytest"
        elif "unittest" in requirements_content:
            test_framework = "unittest"
        else:
            test_framework = "none"

    # Fallback : compter les extensions de fichiers
    else:
        py_count = len(list(project_path.rglob("*.py")))
        js_count = len(list(project_path.rglob("*.js")))
        ts_count = len(list(project_path.rglob("*.ts")))

        if py_count > js_count and py_count > ts_count:
            language = "python"
            confidence = 0.5
        elif ts_count > 0:
            language = "typescript"
            confidence = 0.5
        elif js_count > 0:
            language = "javascript"
            confidence = 0.5

        framework = "none"
        test_framework = "none"

    return {
        "language": language,
        "framework": framework,
        "test_framework": test_framework,
        "confidence": confidence,
    }


def get_language_specific_rules(language: str, framework: str) -> str:
    """
    Retourne les règles spécifiques au langage/framework détecté.

    Returns:
        str: Instructions spécifiques pour le CODEUR
    """
    rules = []

    if language == "python":
        rules.append("- Imports ABSOLUS simples (pas de relatifs)")
        rules.append("- Indentation 4 espaces")
        rules.append("- Type hints recommandés")

        if framework == "fastapi":
            rules.append("- Utilise Pydantic v2 (.model_dump(), .model_validate())")
        elif framework == "flask":
            rules.append("- Utilise Flask blueprints pour organisation")

    elif language in ["javascript", "typescript"]:
        rules.append("- Imports ES6 (import/export)")
        rules.append("- Indentation 2 espaces")

        if framework == "express":
            rules.append("- Utilise middleware Express")
            rules.append("- Gestion erreurs avec try/catch")
        elif framework == "react":
            rules.append("- Composants fonctionnels avec hooks")
            rules.append("- Props avec PropTypes ou TypeScript")

    return "\n".join(rules) if rules else "Aucune règle spécifique détectée"
