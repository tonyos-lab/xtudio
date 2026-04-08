import pytest

from apps.workspace.exceptions import WorkspaceError
from apps.workspace.services import WorkspaceService


@pytest.mark.django_db
class TestWorkspaceService:
    def test_create_user_workspace_creates_directory(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        path = WorkspaceService.create_user_workspace("testuser")
        assert path.exists()
        assert path.is_dir()
        assert path.name == "testuser"

    def test_create_project_workspace_creates_docs_and_src_folders(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        project_path = WorkspaceService.create_project_workspace("testuser", "proj-123")
        assert (project_path / "docs").is_dir()
        assert (project_path / "src").is_dir()

    def test_save_file_saves_to_correct_location(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        WorkspaceService.create_project_workspace("testuser", "proj-123")
        saved = WorkspaceService.save_file("testuser", "proj-123", "test.txt", b"hello world")
        assert saved.exists()
        assert saved.read_bytes() == b"hello world"
        assert saved.name == "test.txt"

    def test_save_file_raises_on_path_traversal(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        WorkspaceService.create_project_workspace("testuser", "proj-123")
        with pytest.raises(WorkspaceError):
            WorkspaceService.save_file("testuser", "proj-123", "../../../etc/passwd", b"bad")

    def test_list_documents_returns_correct_file_list(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        WorkspaceService.create_project_workspace("testuser", "proj-123")
        WorkspaceService.save_file("testuser", "proj-123", "a.txt", b"aaa")
        WorkspaceService.save_file("testuser", "proj-123", "b.pdf", b"bbb")
        docs = WorkspaceService.list_documents("testuser", "proj-123")
        filenames = [d["filename"] for d in docs]
        assert "a.txt" in filenames
        assert "b.pdf" in filenames

    def test_list_documents_returns_empty_list_for_missing_folder(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        result = WorkspaceService.list_documents("nobody", "no-project")
        assert result == []

    def test_get_file_path_raises_on_path_traversal(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        WorkspaceService.create_project_workspace("testuser", "proj-123")
        with pytest.raises(WorkspaceError):
            WorkspaceService.get_file_path("testuser", "proj-123", "../../../etc/passwd")

    def test_get_file_path_raises_file_not_found(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        WorkspaceService.create_project_workspace("testuser", "proj-123")
        with pytest.raises(FileNotFoundError):
            WorkspaceService.get_file_path("testuser", "proj-123", "nonexistent.pdf")

    def test_validate_path_raises_workspace_error_when_outside_base(self, tmp_path):
        base = tmp_path / "base"
        base.mkdir()
        outside = tmp_path / "outside" / "file.txt"
        with pytest.raises(WorkspaceError):
            WorkspaceService.validate_path(base, outside)

    def test_validate_path_accepts_valid_path(self, tmp_path):
        base = tmp_path / "base"
        base.mkdir()
        inside = base / "file.txt"
        WorkspaceService.validate_path(base, inside)  # Should not raise
