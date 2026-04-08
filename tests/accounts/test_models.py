import pytest

from tests.factories import UserFactory


@pytest.mark.django_db
class TestUserModel:
    def test_user_created_with_correct_defaults(self):
        user = UserFactory()
        assert user.pk is not None
        assert user.username.startswith("user_")
        assert "@example.com" in user.email

    def test_user_email_verified_defaults_to_false(self):
        user = UserFactory()
        assert user.email_verified is False

    def test_user_str_returns_username(self):
        user = UserFactory()
        assert str(user) == user.username
