"""
Service d'écriture de fichiers — JARVIS 2.0
Écrit les fichiers produits par les agents dans le dossier projet.
Sécurisé : validation de chemin, extensions autorisées, pas de sortie du projet.
"""

import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)

# Extensions autorisées en écriture
WRITABLE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".html",
    ".css",
    ".scss",
    ".md",
    ".txt",
    ".sh",
    ".bat",
    ".ps1",
    ".sql",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".java",
    ".go",
    ".rs",
    ".php",
    ".rb",
    ".swift",
    ".kt",
    ".vue",
    ".svelte",
    ".gitignore",
    ".env.example",
}

# Pattern pour détecter les blocs de code avec chemin de fichier
# Supporte :
#   # chemin/vers/fichier.py
#   ```python
#   code...
#   ```
# ou :
#   ```python chemin/vers/fichier.py
#   code...
#   ```
# ou :
#   **chemin/vers/fichier.py**
#   ```python
#   code...
#   ```
PATTERN_FILE_HEADER = re.compile(
    r"(?:^|\n)"
    r"(?:"
    r"#+\s*`?([^\n`]+\.\w+)`?"  # # chemin/fichier.ext ou # `chemin/fichier.ext`
    r"|"
    r"\*\*([^\n*]+\.\w+)\*\*"  # **chemin/fichier.ext**
    r"|"
    r"`([^\n`]+\.\w+)`"  # `chemin/fichier.ext` seul sur une ligne
    r")"
    r"\s*\n"
    r"```\w*\s*\n"  # ```langage
    r"(.*?)"  # contenu
    r"\n```",  # ```
    re.DOTALL,
)

PATTERN_INLINE_PATH = re.compile(
    r"```(\w+)\s+([\w/\\.\-]+\.\w+)\s*\n"  # ```python chemin/fichier.ext
    r"(.*?)"  # contenu
    r"\n```",
    re.DOTALL,
)


class FileWriteError(Exception):
    pass


class PathSecurityError(FileWriteError):
    pass


class ExtensionNotAllowedError(FileWriteError):
    pass


def parse_code_blocks(response: str) -> list[dict]:
    """
    Parse la réponse d'un agent pour extraire les blocs de code avec chemins de fichiers.

    Returns:
        Liste de dicts {path, content, language}
    """
    files = []
    seen_paths = set()

    # Pattern 1 : chemin en header puis bloc de code
    for match in PATTERN_FILE_HEADER.finditer(response):
        path = match.group(1) or match.group(2) or match.group(3)
        path = path.strip().strip("`").strip()
        content = match.group(4)

        if path and path not in seen_paths:
            files.append(
                {
                    "path": _normalize_path(path),
                    "content": _clean_content(content),
                }
            )
            seen_paths.add(path)

    # Pattern 2 : ```langage chemin/fichier.ext
    for match in PATTERN_INLINE_PATH.finditer(response):
        language = match.group(1)
        path = match.group(2).strip()
        content = match.group(3)

        if path and path not in seen_paths:
            files.append(
                {
                    "path": _normalize_path(path),
                    "content": _clean_content(content),
                }
            )
            seen_paths.add(path)

    # Logging détaillé si échec
    logger.info(f"Parsing markdown : {len(files)} blocs de code détectés")

    if len(files) == 0:
        logger.warning("⚠️ PARSING ÉCHOUÉ : Aucun bloc de code détecté")
        logger.warning(f"Aperçu de la réponse (500 premiers chars) :\n{response[:500]}")

        # Détection patterns alternatifs pour diagnostic
        alt_patterns = [
            (r"##\s+([^\n]+\.\w+)", "Pattern avec ## (2 dièses)"),
            (r"#\s+([^\n]+\.\w+)\s+```", "Pattern sans newline après chemin"),
            (r"```\w+\s+#\s+([^\n]+\.\w+)", "Pattern avec ``` avant #"),
        ]

        for pattern, desc in alt_patterns:
            matches = re.findall(pattern, response)
            if matches:
                logger.warning(f"Pattern alternatif détecté ({desc}) : {matches[:3]}")

    return files


def _normalize_path(path: str) -> str:
    """Normalise un chemin de fichier (remplace \\ par /, supprime ./ en début)."""
    path = path.replace("\\", "/")
    if path.startswith("./"):
        path = path[2:]
    return path


# Pattern pour détecter les artefacts markdown résiduels
_PATTERN_FENCE_START = re.compile(r"^```\w*\s*\n?", re.MULTILINE)
_PATTERN_FENCE_END = re.compile(r"\n?```\s*$", re.MULTILINE)


def _clean_content(content: str) -> str:
    """
    Nettoie le contenu extrait d'un bloc de code :
    - Supprime les marqueurs markdown résiduels (```python, ```)
    - Supprime les lignes vides en début/fin
    """
    # Supprimer les fences markdown en début
    content = _PATTERN_FENCE_START.sub("", content, count=1)
    # Supprimer les fences markdown en fin
    content = _PATTERN_FENCE_END.sub("", content, count=1)
    # Supprimer les lignes vides en début/fin
    content = content.strip("\n")
    # Ajouter un newline final (convention fichier)
    if content and not content.endswith("\n"):
        content += "\n"
    return content


def validate_write_path(project_path: str, file_path: str) -> Path:
    """
    Valide qu'un chemin d'écriture est sûr.

    Returns:
        Path absolu validé

    Raises:
        PathSecurityError: si le chemin sort du projet
        ExtensionNotAllowedError: si l'extension n'est pas autorisée
    """
    project_abs = Path(project_path).resolve()
    target = (project_abs / file_path).resolve()

    # Vérifier que le fichier reste dans le projet
    if not str(target).startswith(str(project_abs)):
        raise PathSecurityError(f"Chemin interdit (sortie du projet) : {file_path}")

    # Vérifier l'extension
    suffix = target.suffix.lower()
    if suffix and suffix not in WRITABLE_EXTENSIONS:
        raise ExtensionNotAllowedError(f"Extension non autorisée en écriture : {suffix}")

    return target


def write_files_to_project(
    project_path: str,
    files: list[dict],
    session_state=None,
) -> list[dict]:
    """
    Écrit une liste de fichiers dans le dossier projet.

    Args:
        project_path: Chemin absolu du projet
        files: Liste de dicts {path, content}
        session_state: SessionState optionnel pour vérification can_write_disk()

    Returns:
        Liste de dicts {path, status, error?} pour chaque fichier
    """
    # 🚨 PROTECTION CRITIQUE : Vérifier autorisation écriture disque
    if session_state and not session_state.can_write_disk():
        logger.warning(
            "🚨 ÉCRITURE DISQUE BLOQUÉE : mode=%s, phase=%s",
            session_state.mode.value if session_state.mode else "unknown",
            session_state.phase.value if session_state.phase else "none",
        )
        # Retourner tous les fichiers comme "blocked"
        return [
            {
                "path": f["path"],
                "status": "blocked",
                "error": f"Écriture disque interdite (mode={session_state.mode.value}, phase={session_state.phase.value if session_state.phase else 'none'})",
            }
            for f in files
        ]

    results = []

    for file_info in files:
        file_path = file_info["path"]
        content = file_info["content"]

        try:
            target = validate_write_path(project_path, file_path)

            # Créer les dossiers parents si nécessaire
            target.parent.mkdir(parents=True, exist_ok=True)

            # Écrire le fichier
            target.write_text(content, encoding="utf-8")

            logger.info("Fichier écrit : %s", target)
            results.append(
                {
                    "path": file_path,
                    "status": "written",
                    "size": len(content),
                }
            )

        except (PathSecurityError, ExtensionNotAllowedError) as e:
            logger.warning("Écriture refusée : %s — %s", file_path, e)
            results.append(
                {
                    "path": file_path,
                    "status": "rejected",
                    "error": str(e),
                }
            )

        except Exception as e:
            logger.exception("Erreur écriture : %s", file_path)
            results.append(
                {
                    "path": file_path,
                    "status": "error",
                    "error": str(e),
                }
            )

    return results
