from datetime import datetime
from pathlib import Path

from backend.models.file import DirectoryListing, FileContent, FileInfo


class FileServiceError(Exception):
    pass


class PathTraversalError(FileServiceError):
    pass


class FileNotFoundError(FileServiceError):
    pass


class FileTooLargeError(FileServiceError):
    pass


class UnsupportedFileTypeError(FileServiceError):
    pass


class PermissionDeniedError(FileServiceError):
    pass


class EncodingError(FileServiceError):
    pass


class FileService:
    ALLOWED_EXTENSIONS = {
        ".txt",
        ".md",
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
        ".sass",
        ".less",
        ".xml",
        ".csv",
        ".log",
        ".sql",
        ".sh",
        ".bat",
        ".ps1",
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
    }

    MAX_FILE_SIZE = 1024 * 1024
    MAX_TREE_DEPTH = 5

    IGNORED_PATTERNS = {
        "__pycache__",
        "node_modules",
        ".git",
        ".venv",
        "venv",
        "dist",
        "build",
        ".next",
        ".nuxt",
        "target",
        ".pytest_cache",
        ".mypy_cache",
        ".tox",
        "coverage",
        ".coverage",
        "htmlcov",
    }

    @staticmethod
    def validate_path(project_path: str, requested_path: str) -> str:
        """
        Valide et normalise un chemin.
        Lève PathTraversalError si tentative de sortir du projet.
        Retourne le chemin absolu validé.
        """
        try:
            project_abs = Path(project_path).resolve()

            if requested_path:
                requested_abs = (project_abs / requested_path).resolve()
            else:
                requested_abs = project_abs

            if not str(requested_abs).startswith(str(project_abs)):
                raise PathTraversalError("Path outside project")

            if not requested_abs.exists():
                raise FileNotFoundError(f"Path not found: {requested_path}")

            return str(requested_abs)
        except (ValueError, OSError) as e:
            raise PathTraversalError(f"Invalid path: {e}")

    @staticmethod
    def list_directory(project_path: str, subpath: str = "") -> DirectoryListing:
        """Liste le contenu d'un dossier avec métadonnées"""
        abs_path = FileService.validate_path(project_path, subpath)
        path_obj = Path(abs_path)

        if not path_obj.is_dir():
            raise FileServiceError(f"Not a directory: {subpath}")

        items = []
        try:
            for item in sorted(path_obj.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                if item.name in FileService.IGNORED_PATTERNS:
                    continue

                if item.name.startswith(".") and item.name not in {
                    ".env",
                    ".gitignore",
                    ".editorconfig",
                }:
                    continue

                relative_path = str(item.relative_to(Path(project_path)))

                if item.is_dir():
                    items.append(
                        FileInfo(
                            name=item.name,
                            path=relative_path,
                            type="directory",
                            size=None,
                            extension=None,
                            modified_at=datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                        )
                    )
                else:
                    items.append(
                        FileInfo(
                            name=item.name,
                            path=relative_path,
                            type="file",
                            size=item.stat().st_size,
                            extension=item.suffix.lower() if item.suffix else None,
                            modified_at=datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                        )
                    )
        except PermissionError:
            raise PermissionDeniedError(f"Permission denied: {subpath}")

        return DirectoryListing(path=subpath, items=items, total_count=len(items))

    @staticmethod
    def read_file(project_path: str, file_path: str) -> FileContent:
        """Lit un fichier avec validation complète"""
        abs_path = FileService.validate_path(project_path, file_path)
        path_obj = Path(abs_path)

        if not path_obj.is_file():
            raise FileServiceError(f"Not a file: {file_path}")

        if path_obj.suffix.lower() not in FileService.ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeError(f"Extension not allowed: {path_obj.suffix}")

        size = path_obj.stat().st_size
        if size > FileService.MAX_FILE_SIZE:
            raise FileTooLargeError(
                f"File too large: {size} bytes (max {FileService.MAX_FILE_SIZE})"
            )

        try:
            content = path_obj.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            raise EncodingError("Cannot decode file (binary?)")
        except PermissionError:
            raise PermissionDeniedError("Permission denied by OS")

        return FileContent(path=file_path, content=content, size=size, encoding="utf-8")

    @staticmethod
    def get_file_tree(project_path: str, max_depth: int = 3) -> dict:
        """Génère une arborescence complète (limitée en profondeur)"""

        def build_tree(path: Path, current_depth: int) -> dict:
            if current_depth >= max_depth:
                return {"name": path.name, "type": "directory", "truncated": True}

            items = []
            try:
                for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                    if item.name in FileService.IGNORED_PATTERNS:
                        continue

                    if item.name.startswith(".") and item.name not in {".env", ".gitignore"}:
                        continue

                    if item.is_dir():
                        items.append(build_tree(item, current_depth + 1))
                    else:
                        items.append(
                            {
                                "name": item.name,
                                "type": "file",
                                "size": item.stat().st_size,
                                "extension": item.suffix.lower() if item.suffix else None,
                            }
                        )
            except PermissionError:
                pass

            return {"name": path.name, "type": "directory", "items": items}

        project_abs = Path(project_path).resolve()
        if not project_abs.exists():
            raise FileNotFoundError(f"Project path not found: {project_path}")

        return build_tree(project_abs, 0)

    @staticmethod
    def search_files(project_path: str, pattern: str, max_results: int = 50) -> list[FileInfo]:
        """Recherche de fichiers par nom/pattern"""
        project_abs = Path(project_path).resolve()
        if not project_abs.exists():
            raise FileNotFoundError(f"Project path not found: {project_path}")

        results = []
        pattern_lower = pattern.lower()

        def search_recursive(path: Path, depth: int = 0):
            if depth > FileService.MAX_TREE_DEPTH or len(results) >= max_results:
                return

            try:
                for item in path.iterdir():
                    if item.name in FileService.IGNORED_PATTERNS:
                        continue

                    if pattern_lower in item.name.lower():
                        relative_path = str(item.relative_to(project_abs))
                        results.append(
                            FileInfo(
                                name=item.name,
                                path=relative_path,
                                type="directory" if item.is_dir() else "file",
                                size=item.stat().st_size if item.is_file() else None,
                                extension=item.suffix.lower()
                                if item.is_file() and item.suffix
                                else None,
                                modified_at=datetime.fromtimestamp(
                                    item.stat().st_mtime
                                ).isoformat(),
                            )
                        )

                    if item.is_dir() and len(results) < max_results:
                        search_recursive(item, depth + 1)
            except PermissionError:
                pass

        search_recursive(project_abs)
        return results
