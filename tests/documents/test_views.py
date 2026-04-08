import io

import pytest
from django.urls import reverse

from apps.documents.services import DocumentService
from apps.workspace.services import WorkspaceService
from tests.factories import DocumentFactory, ProjectFactory, UserFactory


def create_test_file_on_disk(
    project, user, settings, tmp_path, filename="test.txt", content=b"content"
):
    settings.WORKSPACE_ROOT = tmp_path
    WorkspaceService.create_project_workspace(user.username, str(project.id))
    f = io.BytesIO(content)
    f.name = filename
    f.size = len(content)
    return DocumentService.upload(project, user, f, filename)


@pytest.mark.django_db
class TestDocumentViewView:
    def test_document_view_requires_login(self, client, document):
        url = reverse("document-view", kwargs={"doc_id": document.id})
        response = client.get(url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_document_view_returns_file_inline_for_owner(
        self, authenticated_client, user, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        project = ProjectFactory(owner=user)
        doc = create_test_file_on_disk(project, user, settings, tmp_path, "test.txt", b"hello")
        url = reverse("document-view", kwargs={"doc_id": doc.id})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "inline" in response["Content-Disposition"]

    def test_document_view_returns_403_for_non_owner(self, client, user, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        project = ProjectFactory(owner=user)
        doc = create_test_file_on_disk(project, user, settings, tmp_path, "test.txt", b"hello")
        other_user = UserFactory()
        client.force_login(other_user)
        url = reverse("document-view", kwargs={"doc_id": doc.id})
        response = client.get(url)
        assert response.status_code == 403

    def test_document_download_returns_file_as_attachment_for_owner(
        self, authenticated_client, user, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        project = ProjectFactory(owner=user)
        doc = create_test_file_on_disk(project, user, settings, tmp_path, "test.txt", b"hello")
        url = reverse("document-download", kwargs={"doc_id": doc.id})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "attachment" in response["Content-Disposition"]

    def test_document_download_returns_403_for_non_owner(self, client, user, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        project = ProjectFactory(owner=user)
        doc = create_test_file_on_disk(project, user, settings, tmp_path, "test.txt", b"hello")
        other_user = UserFactory()
        client.force_login(other_user)
        url = reverse("document-download", kwargs={"doc_id": doc.id})
        response = client.get(url)
        assert response.status_code == 403

    def test_document_view_returns_404_for_missing_file(
        self, authenticated_client, user, project, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        doc = DocumentFactory(project=project, filename="ghost.txt")
        url = reverse("document-view", kwargs={"doc_id": doc.id})
        response = authenticated_client.get(url)
        assert response.status_code in (403, 404)


@pytest.mark.django_db
class TestDocumentDownloadView:
    def test_document_download_requires_login(self, client, document):
        url = reverse("document-download", kwargs={"doc_id": document.id})
        response = client.get(url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_document_download_returns_file_as_attachment(
        self, authenticated_client, user, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        project = ProjectFactory(owner=user)
        doc = create_test_file_on_disk(project, user, settings, tmp_path, "dl.txt", b"data")
        url = reverse("document-download", kwargs={"doc_id": doc.id})
        response = authenticated_client.get(url)
        assert response.status_code == 200
        assert "attachment" in response["Content-Disposition"]

    def test_document_download_returns_403_for_non_owner(self, client, user, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        project = ProjectFactory(owner=user)
        doc = create_test_file_on_disk(project, user, settings, tmp_path, "dl.txt", b"data")
        other_user = UserFactory()
        client.force_login(other_user)
        url = reverse("document-download", kwargs={"doc_id": doc.id})
        response = client.get(url)
        assert response.status_code == 403

    def test_document_download_returns_404_for_missing_file(
        self, authenticated_client, user, project, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        WorkspaceService.create_project_workspace(user.username, str(project.id))
        doc = DocumentFactory(project=project, filename="missing_dl.txt")
        url = reverse("document-download", kwargs={"doc_id": doc.id})
        response = authenticated_client.get(url)
        assert response.status_code in (403, 404)


@pytest.mark.django_db
class TestDocumentDeleteView:
    def test_document_delete_requires_login(self, client, document):
        url = reverse("document-delete", kwargs={"doc_id": document.id})
        response = client.post(url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_document_delete_removes_document_for_owner(
        self, authenticated_client, user, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        project = ProjectFactory(owner=user)
        doc = create_test_file_on_disk(project, user, settings, tmp_path, "del.txt", b"bye")
        doc_id = doc.id
        url = reverse("document-delete", kwargs={"doc_id": doc_id})
        response = authenticated_client.post(url)
        assert response.status_code == 302
        from apps.documents.models import Document

        assert not Document.objects.filter(pk=doc_id).exists()

    def test_document_delete_denied_for_non_owner(self, client, user, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        project = ProjectFactory(owner=user)
        doc = create_test_file_on_disk(project, user, settings, tmp_path, "kept.txt", b"keep")
        other_user = UserFactory()
        client.force_login(other_user)
        url = reverse("document-delete", kwargs={"doc_id": doc.id})
        response = client.post(url)
        # Redirects back to project but document still exists
        assert response.status_code == 302
        from apps.documents.models import Document

        assert Document.objects.filter(pk=doc.id).exists()
