"""
Tests unitaires pour backend/services/project_service.py

Couvre :
- Détection nouveau projet
- Détection projet existant propre
- Détection projet avec dette
- Audit dette technique
- Enrichissement contexte
- Listing fichiers code
"""

import os

from backend.models.session_state import ProjectState
from backend.services.project_service import ProjectService


class TestAnalyzeProjectState:
    """Tests détection état projet"""

    def test_new_project_empty_directory(self, tmp_path):
        """Dossier vide → NEW"""
        state = ProjectService.analyze_project_state(str(tmp_path))
        assert state == ProjectState.NEW

    def test_new_project_nonexistent(self):
        """Dossier inexistant → NEW"""
        state = ProjectService.analyze_project_state("/path/does/not/exist")
        assert state == ProjectState.NEW

    def test_new_project_few_files(self, tmp_path):
        """<3 fichiers code → NEW"""
        (tmp_path / "file1.py").write_text("print('hello')")
        (tmp_path / "file2.js").write_text("console.log('hello')")

        state = ProjectService.analyze_project_state(str(tmp_path))
        assert state == ProjectState.NEW

    def test_clean_project_no_debt(self, tmp_path):
        """≥3 fichiers code sans dette → CLEAN"""
        (tmp_path / "file1.py").write_text("def hello(): pass")
        (tmp_path / "file2.py").write_text("def world(): pass")
        (tmp_path / "file3.py").write_text("def foo(): pass")

        state = ProjectService.analyze_project_state(str(tmp_path))
        assert state == ProjectState.CLEAN

    def test_debt_project_with_todo(self, tmp_path):
        """≥3 fichiers code avec dette → DEBT"""
        (tmp_path / "file1.py").write_text("# TODO: fix this\ndef hello(): pass")
        (tmp_path / "file2.py").write_text("def world(): pass")
        (tmp_path / "file3.py").write_text("def foo(): pass")

        state = ProjectService.analyze_project_state(str(tmp_path))
        assert state == ProjectState.DEBT


class TestAnalyzeDebt:
    """Tests audit dette technique"""

    def test_no_debt_clean_code(self, tmp_path):
        """Code propre → 0 problème"""
        (tmp_path / "file1.py").write_text("def hello(): pass")
        (tmp_path / "file2.py").write_text("def world(): pass")

        report = ProjectService.analyze_debt(str(tmp_path))

        assert report["total_issues"] == 0
        assert report["files_with_debt"] == []
        assert report["debt_by_type"] == {}
        assert "✅" in report["summary"]

    def test_debt_detected_todo(self, tmp_path):
        """TODO détecté → 1 problème"""
        (tmp_path / "file1.py").write_text("# TODO: fix this\ndef hello(): pass")

        report = ProjectService.analyze_debt(str(tmp_path))

        assert report["total_issues"] == 1
        assert len(report["files_with_debt"]) == 1
        assert "TODO" in report["debt_by_type"]
        assert report["debt_by_type"]["TODO"] == 1
        assert "⚠️" in report["summary"]

    def test_debt_multiple_patterns(self, tmp_path):
        """Plusieurs patterns → comptage correct"""
        (tmp_path / "file1.py").write_text("# TODO: fix\n# FIXME: bug\n# HACK: temp")

        report = ProjectService.analyze_debt(str(tmp_path))

        assert report["total_issues"] == 3
        assert report["debt_by_type"]["TODO"] == 1
        assert report["debt_by_type"]["FIXME"] == 1
        assert report["debt_by_type"]["HACK"] == 1

    def test_debt_multiple_files(self, tmp_path):
        """Dette dans plusieurs fichiers → agrégation correcte"""
        (tmp_path / "file1.py").write_text("# TODO: fix")
        (tmp_path / "file2.py").write_text("# TODO: also fix")

        report = ProjectService.analyze_debt(str(tmp_path))

        assert report["total_issues"] == 2
        assert len(report["files_with_debt"]) == 2
        assert report["debt_by_type"]["TODO"] == 2

    def test_debt_nonexistent_project(self):
        """Projet inexistant → rapport vide"""
        report = ProjectService.analyze_debt("/path/does/not/exist")

        assert report["total_issues"] == 0
        assert report["summary"] == "Projet inexistant"

    def test_debt_no_code_files(self, tmp_path):
        """Aucun fichier code → rapport vide"""
        (tmp_path / "readme.txt").write_text("README")

        report = ProjectService.analyze_debt(str(tmp_path))

        assert report["total_issues"] == 0
        assert report["summary"] == "Aucun fichier code"


class TestBuildEnrichedContext:
    """Tests enrichissement contexte"""

    def test_context_new_project(self):
        """Contexte projet NEW"""
        project = {
            "name": "TestProject",
            "path": "/test/path",
            "description": "Test description",
        }
        file_tree = {"name": "project", "type": "directory", "items": []}

        context = ProjectService.build_enriched_context(project, file_tree, ProjectState.NEW)

        assert "TestProject" in context
        assert "/test/path" in context
        assert "NOUVEAU (dossier vide)" in context
        assert "MODE PROJET" in context

    def test_context_clean_project(self):
        """Contexte projet CLEAN"""
        project = {
            "name": "TestProject",
            "path": "/test/path",
            "description": "Test description",
        }
        file_tree = {"name": "project", "type": "directory", "items": []}

        context = ProjectService.build_enriched_context(project, file_tree, ProjectState.CLEAN)

        assert "PROPRE (sans dette)" in context

    def test_context_debt_project_with_report(self):
        """Contexte projet DEBT avec rapport"""
        project = {
            "name": "TestProject",
            "path": "/test/path",
            "description": "Test description",
        }
        file_tree = {"name": "project", "type": "directory", "items": []}
        debt_report = {
            "total_issues": 5,
            "summary": "⚠️ 5 problème(s) : TODO (3), FIXME (2)",
        }

        context = ProjectService.build_enriched_context(
            project, file_tree, ProjectState.DEBT, debt_report
        )

        assert "DETTE DÉTECTÉE" in context
        assert "⚠️ 5 problème(s)" in context

    def test_context_max_length(self):
        """Contexte limité à 1500 chars"""
        project = {
            "name": "TestProject",
            "path": "/test/path",
            "description": "x" * 200,  # Description longue
        }
        file_tree = {
            "name": "project",
            "type": "directory",
            "items": [{"name": f"file{i}.py", "type": "file"} for i in range(100)],
        }

        context = ProjectService.build_enriched_context(project, file_tree, ProjectState.NEW)

        assert len(context) <= 1500


class TestListCodeFiles:
    """Tests listing fichiers code"""

    def test_list_python_files(self, tmp_path):
        """Liste fichiers .py"""
        (tmp_path / "file1.py").write_text("code")
        (tmp_path / "file2.py").write_text("code")
        (tmp_path / "readme.txt").write_text("text")

        files = ProjectService._list_code_files(str(tmp_path))

        assert len(files) == 2
        assert all(f.endswith(".py") for f in files)

    def test_list_javascript_files(self, tmp_path):
        """Liste fichiers .js"""
        (tmp_path / "file1.js").write_text("code")
        (tmp_path / "file2.ts").write_text("code")

        files = ProjectService._list_code_files(str(tmp_path))

        assert len(files) == 2

    def test_ignore_hidden_directories(self, tmp_path):
        """Ignore dossiers cachés"""
        hidden_dir = tmp_path / ".git"
        hidden_dir.mkdir()
        (hidden_dir / "file.py").write_text("code")
        (tmp_path / "file.py").write_text("code")

        files = ProjectService._list_code_files(str(tmp_path))

        assert len(files) == 1
        assert ".git" not in files[0]

    def test_ignore_node_modules(self, tmp_path):
        """Ignore node_modules"""
        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "file.js").write_text("code")
        (tmp_path / "app.js").write_text("code")

        files = ProjectService._list_code_files(str(tmp_path))

        assert len(files) == 1
        # Vérifier que le fichier retourné est app.js (pas celui dans node_modules)
        assert os.path.basename(files[0]) == "app.js"
        # Vérifier que node_modules n'est pas dans le chemin relatif
        rel_path = os.path.relpath(files[0], str(tmp_path))
        assert "node_modules" not in rel_path

    def test_max_files_limit(self, tmp_path):
        """Limite max_files respectée"""
        for i in range(150):
            (tmp_path / f"file{i}.py").write_text("code")

        files = ProjectService._list_code_files(str(tmp_path), max_files=50)

        assert len(files) == 50

    def test_nonexistent_directory(self):
        """Dossier inexistant → liste vide"""
        files = ProjectService._list_code_files("/path/does/not/exist")

        assert files == []
