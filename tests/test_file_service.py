import tempfile
from pathlib import Path

import pytest

from backend.services.file_service import (
    FileNotFoundError,
    FileService,
    FileTooLargeError,
    PathTraversalError,
    UnsupportedFileTypeError,
)


@pytest.fixture
def temp_project():
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        (project_path / "test.txt").write_text("Hello World", encoding="utf-8")
        (project_path / "test.py").write_text("print('test')", encoding="utf-8")
        (project_path / "subdir").mkdir()
        (project_path / "subdir" / "nested.md").write_text("# Test", encoding="utf-8")

        yield str(project_path)


def test_validate_path_valid(temp_project):
    result = FileService.validate_path(temp_project, "test.txt")
    assert result.endswith("test.txt")


def test_validate_path_traversal_attack(temp_project):
    with pytest.raises(PathTraversalError):
        FileService.validate_path(temp_project, "../../../etc/passwd")


def test_validate_path_not_exists(temp_project):
    with pytest.raises(FileNotFoundError):
        FileService.validate_path(temp_project, "nonexistent.txt")


def test_list_directory_valid(temp_project):
    listing = FileService.list_directory(temp_project)

    assert listing.total_count >= 3
    assert any(item.name == "test.txt" for item in listing.items)
    assert any(item.name == "subdir" for item in listing.items)


def test_list_directory_empty(temp_project):
    empty_dir = Path(temp_project) / "empty"
    empty_dir.mkdir()

    listing = FileService.list_directory(temp_project, "empty")
    assert listing.total_count == 0


def test_read_file_valid(temp_project):
    content = FileService.read_file(temp_project, "test.txt")

    assert content.path == "test.txt"
    assert content.content == "Hello World"
    assert content.size == 11
    assert content.encoding == "utf-8"


def test_read_file_nested(temp_project):
    content = FileService.read_file(temp_project, "subdir/nested.md")

    assert content.content == "# Test"


def test_read_file_too_large(temp_project):
    large_file = Path(temp_project) / "large.txt"
    large_file.write_bytes(b"x" * (FileService.MAX_FILE_SIZE + 1))

    with pytest.raises(FileTooLargeError):
        FileService.read_file(temp_project, "large.txt")


def test_read_file_invalid_extension(temp_project):
    exe_file = Path(temp_project) / "test.exe"
    exe_file.write_bytes(b"binary content")

    with pytest.raises(UnsupportedFileTypeError):
        FileService.read_file(temp_project, "test.exe")


def test_get_file_tree(temp_project):
    tree = FileService.get_file_tree(temp_project, max_depth=2)

    assert tree["type"] == "directory"
    assert "items" in tree
    assert len(tree["items"]) >= 3


def test_get_file_tree_depth_limit(temp_project):
    deep_dir = Path(temp_project) / "a" / "b" / "c" / "d"
    deep_dir.mkdir(parents=True)
    (deep_dir / "deep.txt").write_text("deep")

    tree = FileService.get_file_tree(temp_project, max_depth=2)

    assert tree["type"] == "directory"


def test_search_files_pattern(temp_project):
    results = FileService.search_files(temp_project, "test")

    assert len(results) >= 2
    assert any("test.txt" in r.name for r in results)
    assert any("test.py" in r.name for r in results)


def test_search_files_max_results(temp_project):
    for i in range(10):
        (Path(temp_project) / f"file{i}.txt").write_text(f"content {i}")

    results = FileService.search_files(temp_project, "file", max_results=5)
    assert len(results) <= 10


def test_list_directory_ignores_patterns(temp_project):
    (Path(temp_project) / "node_modules").mkdir()
    (Path(temp_project) / "__pycache__").mkdir()

    listing = FileService.list_directory(temp_project)

    assert not any(item.name == "node_modules" for item in listing.items)
    assert not any(item.name == "__pycache__" for item in listing.items)


def test_validate_path_empty_subpath(temp_project):
    result = FileService.validate_path(temp_project, "")
    assert result == str(Path(temp_project).resolve())
