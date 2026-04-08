import io

import pytest
from django.urls import reverse

from apps.projects.models import Project
from tests.factories import ProjectFactory, UserFactory


@pytest.mark.django_db
class TestProjectListView:
    def test_project_list_view_requires_login(self, client):
        url = reverse("project-list")
        response = client.get(url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_project_list_view_returns_200_for_authenticated_user(self, authenticated_client):
        url = reverse("project-list")
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_project_list_view_shows_only_user_projects(
        self, authenticated_client, user, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        p1 = ProjectFactory(owner=user)
        other_user = UserFactory()
        ProjectFactory(owner=other_user)
        url = reverse("project-list")
        response = authenticated_client.get(url)
        assert p1.name.encode() in response.content


@pytest.mark.django_db
class TestProjectCreateView:
    def test_project_create_view_get_returns_200(self, authenticated_client):
        url = reverse("project-create")
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_project_create_view_get_requires_login(self, client):
        url = reverse("project-create")
        response = client.get(url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_project_create_view_creates_project_on_post(
        self, authenticated_client, user, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        url = reverse("project-create")
        response = authenticated_client.post(
            url,
            {
                "name": "New Test Project",
                "description": "A description",
                "tech_stack": "Django",
            },
        )
        assert response.status_code == 302
        assert Project.objects.filter(owner=user, name="New Test Project").exists()

    def test_project_create_view_invalid_post_returns_200(self, authenticated_client):
        url = reverse("project-create")
        response = authenticated_client.post(url, {"name": ""})
        assert response.status_code == 200


@pytest.mark.django_db
class TestProjectDetailView:
    def test_project_detail_view_returns_200_for_owner(self, authenticated_client, project):
        url = reverse("project-detail", kwargs={"project_id": project.id})
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_project_detail_view_returns_404_for_other_user(
        self, client, project, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        other_user = UserFactory()
        client.force_login(other_user)
        url = reverse("project-detail", kwargs={"project_id": project.id})
        response = client.get(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestProjectUpdateView:
    def test_project_update_view_get_returns_200_for_owner(self, authenticated_client, project):
        url = reverse("project-edit", kwargs={"project_id": project.id})
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_project_update_view_get_requires_login(self, client, project):
        url = reverse("project-edit", kwargs={"project_id": project.id})
        response = client.get(url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_project_update_view_get_returns_404_for_non_owner(self, client, project):
        other_user = UserFactory()
        client.force_login(other_user)
        url = reverse("project-edit", kwargs={"project_id": project.id})
        response = client.get(url)
        assert response.status_code == 404

    def test_project_update_view_post_updates_project(self, authenticated_client, project):
        url = reverse("project-edit", kwargs={"project_id": project.id})
        response = authenticated_client.post(
            url,
            {"name": "Updated Name", "description": "New desc", "tech_stack": "Flask"},
        )
        assert response.status_code == 302
        project.refresh_from_db()
        assert project.name == "Updated Name"

    def test_project_update_view_invalid_post_returns_200(self, authenticated_client, project):
        url = reverse("project-edit", kwargs={"project_id": project.id})
        response = authenticated_client.post(url, {"name": ""})
        assert response.status_code == 200


@pytest.mark.django_db
class TestProjectArchiveView:
    def test_project_archive_view_archives_project(self, authenticated_client, project):
        url = reverse("project-archive", kwargs={"project_id": project.id})
        response = authenticated_client.post(url)
        assert response.status_code == 302
        project.refresh_from_db()
        assert project.status == Project.STATUS_ARCHIVED

    def test_project_archive_view_requires_login(self, client, project):
        url = reverse("project-archive", kwargs={"project_id": project.id})
        response = client.post(url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_project_archive_view_returns_404_for_non_owner(self, client, project):
        other_user = UserFactory()
        client.force_login(other_user)
        url = reverse("project-archive", kwargs={"project_id": project.id})
        response = client.post(url)
        assert response.status_code == 404


@pytest.mark.django_db
class TestRequirementsUploadView:
    def test_requirements_upload_accepts_valid_pdf(
        self, authenticated_client, user, project, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        from apps.workspace.services import WorkspaceService

        WorkspaceService.create_project_workspace(user.username, str(project.id))
        url = reverse("requirements-upload", kwargs={"project_id": project.id})
        pdf_content = b"%PDF-1.4 test pdf content"
        f = io.BytesIO(pdf_content)
        f.name = "requirements.pdf"
        f.size = len(pdf_content)
        response = authenticated_client.post(url, {"files": f}, format="multipart")
        assert response.status_code == 302

    def test_requirements_upload_accepts_multiple_files(
        self, authenticated_client, user, project, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        from apps.workspace.services import WorkspaceService

        WorkspaceService.create_project_workspace(user.username, str(project.id))
        url = reverse("requirements-upload", kwargs={"project_id": project.id})
        f1 = io.BytesIO(b"content1")
        f1.name = "file1.txt"
        f1.size = 8
        f2 = io.BytesIO(b"content2")
        f2.name = "file2.md"
        f2.size = 8
        response = authenticated_client.post(url, {"files": [f1, f2]}, format="multipart")
        assert response.status_code == 302

    def test_requirements_upload_rejects_invalid_file_type(
        self, authenticated_client, user, project, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        from apps.workspace.services import WorkspaceService

        WorkspaceService.create_project_workspace(user.username, str(project.id))
        url = reverse("requirements-upload", kwargs={"project_id": project.id})
        f = io.BytesIO(b"#!/bin/bash\necho bad")
        f.name = "bad.sh"
        f.size = 20
        response = authenticated_client.post(url, {"files": f}, format="multipart")
        assert response.status_code == 302
        from apps.documents.models import Document

        assert not Document.objects.filter(project=project, filename="bad.sh").exists()

    def test_requirements_upload_rejects_oversized_file(
        self, authenticated_client, user, project, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        from apps.workspace.services import WorkspaceService

        WorkspaceService.create_project_workspace(user.username, str(project.id))
        url = reverse("requirements-upload", kwargs={"project_id": project.id})
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB
        f = io.BytesIO(large_content)
        f.name = "huge.pdf"
        f.size = len(large_content)
        response = authenticated_client.post(url, {"files": f}, format="multipart")
        assert response.status_code == 302
        from apps.documents.models import Document

        assert not Document.objects.filter(project=project, filename="huge.pdf").exists()

    def test_requirements_upload_no_files_redirects(
        self, authenticated_client, project, settings, tmp_path
    ):
        settings.WORKSPACE_ROOT = tmp_path
        url = reverse("requirements-upload", kwargs={"project_id": project.id})
        response = authenticated_client.post(url, {})
        assert response.status_code == 302
