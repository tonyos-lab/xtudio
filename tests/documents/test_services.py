import io

import pytest
from django.core.exceptions import PermissionDenied, ValidationError

from apps.documents.models import Document
from apps.documents.services import DocumentService
from apps.workspace.services import WorkspaceService
from tests.factories import DocumentFactory, ProjectFactory, UserFactory


def make_upload_file(name: str, content: bytes):
    f = io.BytesIO(content)
    f.name = name
    f.size = len(content)
    return f


@pytest.mark.django_db
class TestDocumentService:
    def test_document_service_upload_creates_document_record(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        f = make_upload_file("req.pdf", b"%PDF-1.4 test")
        doc = DocumentService.upload(project, user, f, "req.pdf")
        assert doc.pk is not None
        assert Document.objects.filter(pk=doc.pk).exists()

    def test_document_service_upload_saves_file_to_workspace(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        content = b"Hello document content"
        f = make_upload_file("hello.txt", content)
        doc = DocumentService.upload(project, user, f, "hello.txt")
        saved_path = tmp_path / user.username / str(project.id) / "docs" / doc.filename
        assert saved_path.exists()
        assert saved_path.read_bytes() == content

    def test_document_service_upload_writes_audit_log(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        from apps.audit_trail.models import AuditLog

        initial = AuditLog.objects.count()
        f = make_upload_file("audit.pdf", b"%PDF test")
        DocumentService.upload(project, user, f, "audit.pdf")
        assert AuditLog.objects.count() > initial

    def test_document_service_upload_raises_on_invalid_file_type(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        f = make_upload_file("bad.exe", b"MZ executable")
        with pytest.raises(ValidationError):
            DocumentService.upload(project, user, f, "bad.exe")

    def test_document_service_upload_raises_on_oversized_file(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        large = b"x" * (11 * 1024 * 1024)
        f = make_upload_file("huge.pdf", large)
        with pytest.raises(ValidationError):
            DocumentService.upload(project, user, f, "huge.pdf")

    def test_document_service_get_for_project_returns_correct_documents(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        d1 = DocumentFactory(project=project)
        d2 = DocumentFactory(project=project)
        other_project = ProjectFactory(owner=user)
        DocumentFactory(project=other_project)
        docs = DocumentService.get_for_project(project)
        assert d1 in docs
        assert d2 in docs
        assert len(docs) == 2

    def test_document_service_get_file_response_raises_permission_denied_for_wrong_user(
        self, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        other_user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        content = b"test content"
        f = make_upload_file("test.txt", content)
        doc = DocumentService.upload(project, user, f, "test.txt")
        with pytest.raises(PermissionDenied):
            DocumentService.get_file_response(doc, other_user)

    def test_document_service_get_file_response_raises_file_not_found(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        # Document record exists but file is missing from disk
        doc = DocumentFactory(project=project, filename="missing.pdf")
        with pytest.raises(FileNotFoundError):
            DocumentService.get_file_response(doc, user)

    def test_document_service_get_file_response_inline_sets_correct_disposition(
        self, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        content = b"inline content"
        f = make_upload_file("inline.txt", content)
        doc = DocumentService.upload(project, user, f, "inline.txt")
        response = DocumentService.get_file_response(doc, user, inline=True)
        assert "inline" in response["Content-Disposition"]
        response.close()

    def test_document_service_get_file_response_download_sets_attachment_disposition(
        self, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        content = b"download content"
        f = make_upload_file("download.txt", content)
        doc = DocumentService.upload(project, user, f, "download.txt")
        response = DocumentService.get_file_response(doc, user, inline=False)
        assert "attachment" in response["Content-Disposition"]
        response.close()

    def test_document_service_upload_raises_on_duplicate_filename(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        f1 = make_upload_file("dup.txt", b"first")
        DocumentService.upload(project, user, f1, "dup.txt")
        f2 = make_upload_file("dup.txt", b"second")
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            DocumentService.upload(project, user, f2, "dup.txt")

    def test_document_service_delete_removes_db_record(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        f = make_upload_file("todel.txt", b"bye")
        doc = DocumentService.upload(project, user, f, "todel.txt")
        doc_id = doc.pk
        from apps.documents.models import Document

        DocumentService.delete(doc, user)
        assert not Document.objects.filter(pk=doc_id).exists()

    def test_document_service_delete_raises_permission_denied_for_wrong_user(
        self, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        other_user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        f = make_upload_file("owned.txt", b"data")
        doc = DocumentService.upload(project, user, f, "owned.txt")
        from django.core.exceptions import PermissionDenied

        with pytest.raises(PermissionDenied):
            DocumentService.delete(doc, other_user)

    def test_document_service_delete_writes_audit_log(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        f = make_upload_file("audit_del.txt", b"x")
        doc = DocumentService.upload(project, user, f, "audit_del.txt")
        from apps.audit_trail.models import AuditLog

        count_before = AuditLog.objects.count()
        DocumentService.delete(doc, user)
        assert AuditLog.objects.count() > count_before
