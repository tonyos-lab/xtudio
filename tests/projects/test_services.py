import pytest

from apps.projects.models import Project
from apps.projects.services import ProjectService
from tests.factories import ProjectFactory, UserFactory


@pytest.mark.django_db
class TestProjectService:
    def test_project_service_create_creates_project_record(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectService.create(owner=user, name="Test Project")
        assert project.pk is not None
        assert project.name == "Test Project"
        assert project.owner == user

    def test_project_service_create_calls_create_project_workspace(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectService.create(owner=user, name="WS Project")
        docs_path = tmp_path / user.username / str(project.id) / "docs"
        src_path = tmp_path / user.username / str(project.id) / "src"
        assert docs_path.is_dir()
        assert src_path.is_dir()

    def test_project_service_create_sets_workspace_path(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectService.create(owner=user, name="WS Path Project")
        assert project.workspace_path != ""
        assert str(project.id) in project.workspace_path

    def test_project_service_create_writes_audit_log(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        from apps.audit_trail.models import AuditLog

        initial_count = AuditLog.objects.count()
        ProjectService.create(owner=user, name="Audit Project")
        assert AuditLog.objects.count() > initial_count

    def test_project_service_create_sends_notification(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        from apps.notification_hub.models import Notification

        initial_count = Notification.objects.count()
        ProjectService.create(owner=user, name="Notif Project")
        assert Notification.objects.count() > initial_count

    def test_project_service_get_for_user_returns_only_user_projects(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user1 = UserFactory()
        user2 = UserFactory()
        p1 = ProjectFactory(owner=user1)
        p2 = ProjectFactory(owner=user1)
        ProjectFactory(owner=user2)
        projects = list(ProjectService.get_for_user(user1))
        assert p1 in projects
        assert p2 in projects
        assert len(projects) == 2

    def test_project_service_archive_sets_status_archived(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user, status="active")
        ProjectService.archive(project)
        project.refresh_from_db()
        assert project.status == Project.STATUS_ARCHIVED

    def test_project_service_update_changes_name(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user, name="Old Name")
        result = ProjectService.update(project, name="New Name")
        project.refresh_from_db()
        assert result.name == "New Name"
        assert project.name == "New Name"

    def test_project_service_update_changes_description(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        ProjectService.update(project, description="Updated description")
        project.refresh_from_db()
        assert project.description == "Updated description"

    def test_project_service_update_writes_audit_log(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        from apps.audit_trail.models import AuditLog

        count_before = AuditLog.objects.count()
        ProjectService.update(project, name="Changed")
        assert AuditLog.objects.count() > count_before

    def test_project_service_update_ignores_non_allowed_fields(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        original_owner = project.owner
        ProjectService.update(project, owner=UserFactory())
        project.refresh_from_db()
        assert project.owner == original_owner

    def test_project_service_archive_writes_audit_log(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        project = ProjectFactory(owner=user)
        from apps.audit_trail.models import AuditLog

        count_before = AuditLog.objects.count()
        ProjectService.archive(project)
        assert AuditLog.objects.count() > count_before
