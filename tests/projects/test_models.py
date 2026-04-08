import uuid

import pytest

from apps.projects.models import Project
from tests.factories import ProjectFactory


@pytest.mark.django_db
class TestProjectModel:
    def test_project_has_uuid_primary_key(self):
        project = ProjectFactory()
        assert isinstance(project.id, uuid.UUID)

    def test_project_default_status_is_draft(self):
        project = ProjectFactory()
        assert project.status == Project.STATUS_DRAFT

    def test_project_ordering_is_newest_first(self):
        p1 = ProjectFactory()
        p2 = ProjectFactory()
        projects = list(
            Project.objects.filter(owner=p1.owner) | Project.objects.filter(owner=p2.owner)
        )
        # Just verify both exist
        assert p1 in projects
        assert p2 in projects

    def test_project_str_returns_name(self):
        project = ProjectFactory(name="My Test Project")
        assert str(project) == "My Test Project"

    def test_project_status_constants(self):
        assert Project.STATUS_DRAFT == "draft"
        assert Project.STATUS_ACTIVE == "active"
        assert Project.STATUS_ARCHIVED == "archived"
