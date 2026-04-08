import pytest
from django.urls import reverse

from tests.factories import UserFactory


@pytest.mark.django_db
class TestRegisterView:
    def test_register_view_get_returns_200(self, client):
        url = reverse("accounts-register")
        response = client.get(url)
        assert response.status_code == 200

    def test_register_view_post_creates_user(self, client, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        url = reverse("accounts-register")
        response = client.post(
            url,
            {
                "email": "newuser@example.com",
                "password": "securepass123",
                "password_confirm": "securepass123",
            },
        )
        assert response.status_code == 302
        from django.contrib.auth import get_user_model

        user_model = get_user_model()
        assert user_model.objects.filter(email="newuser@example.com").exists()


@pytest.mark.django_db
class TestLoginView:
    def test_login_view_get_returns_200(self, client):
        url = reverse("accounts-login")
        response = client.get(url)
        assert response.status_code == 200

    def test_login_view_post_authenticates_user(self, client, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory(username="logintest")
        url = reverse("accounts-login")
        response = client.post(
            url,
            {
                "email": user.email,
                "password": "testpass123",
            },
        )
        assert response.status_code == 302

    def test_login_view_post_invalid_credentials_shows_error(self, client):
        url = reverse("accounts-login")
        response = client.post(
            url,
            {
                "email": "wrong@example.com",
                "password": "wrongpass",
            },
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestLogoutView:
    def test_logout_redirects_to_login(self, authenticated_client):
        url = reverse("logout")
        response = authenticated_client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestProfileView:
    def test_profile_view_requires_login(self, client):
        url = reverse("profile")
        response = client.get(url)
        assert response.status_code == 302
        assert "login" in response.url

    def test_profile_view_returns_200_for_authenticated_user(self, authenticated_client):
        url = reverse("profile")
        response = authenticated_client.get(url)
        assert response.status_code == 200

    def test_profile_edit_view_updates_user(self, authenticated_client, user):
        url = reverse("profile-edit")
        response = authenticated_client.post(
            url,
            {
                "first_name": "Updated",
                "last_name": "Name",
                "bio": "My bio",
            },
        )
        assert response.status_code == 302
        user.refresh_from_db()
        assert user.first_name == "Updated"
