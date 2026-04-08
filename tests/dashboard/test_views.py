import pytest
from django.urls import reverse

from tests.factories import ProjectFactory


@pytest.mark.django_db
class TestDashboardView:
    def test_dashboard_requires_login(self, client):
        url = reverse("dashboard")
        response = client.get(url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_dashboard_returns_200_for_authenticated_user(self, authenticated_client):
        url = reverse("dashboard")
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_dashboard_context_contains_total_projects(self, authenticated_client, user):
        ProjectFactory(owner=user)
        ProjectFactory(owner=user)
        url = reverse("dashboard")
        response = authenticated_client.get(url)
        assert response.context["total_projects"] == 2

    def test_dashboard_context_counts_only_user_projects(
        self, authenticated_client, user, other_user
    ):
        ProjectFactory(owner=user)
        ProjectFactory(owner=other_user)
        url = reverse("dashboard")
        response = authenticated_client.get(url)
        assert response.context["total_projects"] == 1

    def test_dashboard_context_contains_active_projects(self, authenticated_client, user):
        ProjectFactory(owner=user, status="active")
        ProjectFactory(owner=user, status="draft")
        url = reverse("dashboard")
        response = authenticated_client.get(url)
        assert response.context["active_projects"] == 1

    def test_dashboard_context_contains_recent_projects(self, authenticated_client, user):
        p = ProjectFactory(owner=user)
        url = reverse("dashboard")
        response = authenticated_client.get(url)
        assert p in response.context["recent_projects"]

    def test_dashboard_context_contains_total_documents(
        self, authenticated_client, user, document
    ):
        url = reverse("dashboard")
        response = authenticated_client.get(url)
        assert response.context["total_documents"] >= 1
