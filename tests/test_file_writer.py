"""
Tests pour le service d'écriture de fichiers — parse_code_blocks, write_files_to_project.
"""


import pytest

from backend.services.file_writer import (
    ExtensionNotAllowedError,
    PathSecurityError,
    _clean_content,
    _normalize_path,
    parse_code_blocks,
    validate_write_path,
    write_files_to_project,
)


class TestNormalizePath:
    def test_forward_slashes(self):
        assert _normalize_path("src\\main.py") == "src/main.py"

    def test_remove_dot_slash(self):
        assert _normalize_path("./src/main.py") == "src/main.py"

    def test_already_clean(self):
        assert _normalize_path("src/main.py") == "src/main.py"


class TestCleanContent:
    def test_removes_leading_fence(self):
        content = "```python\nprint('hello')\n```"
        result = _clean_content(content)
        assert result == "print('hello')\n"

    def test_removes_trailing_fence(self):
        content = "x = 1\n```"
        result = _clean_content(content)
        assert result == "x = 1\n"

    def test_strips_empty_lines(self):
        content = "\n\nprint('hello')\n\n"
        result = _clean_content(content)
        assert result == "print('hello')\n"

    def test_adds_trailing_newline(self):
        content = "x = 1"
        result = _clean_content(content)
        assert result == "x = 1\n"

    def test_clean_content_already_clean(self):
        content = "def add(a, b):\n    return a + b\n"
        result = _clean_content(content)
        assert result == content

    def test_fence_with_language(self):
        content = '```json\n{"key": "value"}\n```'
        result = _clean_content(content)
        assert result == '{"key": "value"}\n'


class TestParseCodeBlocks:
    def test_header_hash_then_block(self):
        response = "Voici le fichier :\n# src/main.py\n```python\nprint('hello')\n```"
        files = parse_code_blocks(response)
        assert len(files) == 1
        assert files[0]["path"] == "src/main.py"
        assert "print('hello')" in files[0]["content"]

    def test_header_bold_then_block(self):
        response = "**src/utils.py**\n```python\ndef add(a, b): return a + b\n```"
        files = parse_code_blocks(response)
        assert len(files) == 1
        assert files[0]["path"] == "src/utils.py"

    def test_header_backtick_then_block(self):
        response = '`config.json`\n```json\n{"key": "value"}\n```'
        files = parse_code_blocks(response)
        assert len(files) == 1
        assert files[0]["path"] == "config.json"

    def test_inline_path_in_fence(self):
        response = "```python src/calc.py\ndef multiply(a, b): return a * b\n```"
        files = parse_code_blocks(response)
        assert len(files) == 1
        assert files[0]["path"] == "src/calc.py"

    def test_multiple_files(self):
        response = "# src/a.py\n```python\na = 1\n```\n\n# src/b.py\n```python\nb = 2\n```"
        files = parse_code_blocks(response)
        assert len(files) == 2
        paths = {f["path"] for f in files}
        assert paths == {"src/a.py", "src/b.py"}

    def test_no_code_blocks(self):
        response = "Pas de code ici, juste du texte."
        files = parse_code_blocks(response)
        assert files == []

    def test_code_block_without_path_not_extracted(self):
        response = "Voici un exemple :\n```python\nprint('no path')\n```"
        files = parse_code_blocks(response)
        assert files == []

    def test_content_cleaned_of_markdown_artifacts(self):
        response = "# src/main.py\n```python\n```python\nprint('hello')\n```\n```"
        files = parse_code_blocks(response)
        assert len(files) == 1
        assert not files[0]["content"].startswith("```")
        assert "print('hello')" in files[0]["content"]

    def test_content_has_trailing_newline(self):
        response = "# src/app.py\n```python\nx = 1\n```"
        files = parse_code_blocks(response)
        assert files[0]["content"].endswith("\n")

    def test_dedup_same_path(self):
        response = "# src/main.py\n```python\nv1\n```\n\n# src/main.py\n```python\nv2\n```"
        files = parse_code_blocks(response)
        assert len(files) == 1


class TestValidateWritePath:
    def test_valid_path(self, tmp_path):
        target = validate_write_path(str(tmp_path), "src/main.py")
        assert str(target).startswith(str(tmp_path))

    def test_path_traversal_blocked(self, tmp_path):
        with pytest.raises(PathSecurityError):
            validate_write_path(str(tmp_path), "../../etc/passwd")

    def test_disallowed_extension(self, tmp_path):
        with pytest.raises(ExtensionNotAllowedError):
            validate_write_path(str(tmp_path), "malware.exe")

    def test_allowed_extension_py(self, tmp_path):
        target = validate_write_path(str(tmp_path), "script.py")
        assert target.suffix == ".py"


class TestWriteFilesToProject:
    def test_write_single_file(self, tmp_path):
        files = [{"path": "hello.py", "content": "print('hello')"}]
        results = write_files_to_project(str(tmp_path), files)
        assert len(results) == 1
        assert results[0]["status"] == "written"
        assert (tmp_path / "hello.py").read_text(encoding="utf-8") == "print('hello')"

    def test_write_creates_subdirs(self, tmp_path):
        files = [{"path": "src/utils/helpers.py", "content": "x = 1"}]
        results = write_files_to_project(str(tmp_path), files)
        assert results[0]["status"] == "written"
        assert (tmp_path / "src" / "utils" / "helpers.py").exists()

    def test_write_multiple_files(self, tmp_path):
        files = [
            {"path": "a.py", "content": "a = 1"},
            {"path": "b.py", "content": "b = 2"},
        ]
        results = write_files_to_project(str(tmp_path), files)
        assert all(r["status"] == "written" for r in results)
        assert (tmp_path / "a.py").exists()
        assert (tmp_path / "b.py").exists()

    def test_rejects_path_traversal(self, tmp_path):
        files = [{"path": "../../evil.py", "content": "bad"}]
        results = write_files_to_project(str(tmp_path), files)
        assert results[0]["status"] == "rejected"

    def test_rejects_bad_extension(self, tmp_path):
        files = [{"path": "virus.exe", "content": "bad"}]
        results = write_files_to_project(str(tmp_path), files)
        assert results[0]["status"] == "rejected"

    def test_overwrites_existing_file(self, tmp_path):
        (tmp_path / "file.py").write_text("old", encoding="utf-8")
        files = [{"path": "file.py", "content": "new"}]
        results = write_files_to_project(str(tmp_path), files)
        assert results[0]["status"] == "written"
        assert (tmp_path / "file.py").read_text(encoding="utf-8") == "new"
