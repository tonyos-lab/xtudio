import pytest

from tests.factories import UserFactory


@pytest.mark.django_db
class TestAccountSignals:
    def test_user_creation_triggers_create_user_workspace(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        workspace = tmp_path / user.username
        assert workspace.exists()
        assert workspace.is_dir()

    def test_user_workspace_path_exists_after_registration(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        UserFactory(username="signal_test_user")
        assert (tmp_path / "signal_test_user").exists()

    def test_workspace_not_created_on_user_update(self, settings, tmp_path):
        settings.WORKSPACE_ROOT = tmp_path
        user = UserFactory()
        # Record created workspaces before update
        initial_dirs = set(p.name for p in tmp_path.iterdir() if p.is_dir())
        # Update user — should NOT create a new workspace
        user.first_name = "Updated"
        user.save()
        final_dirs = set(p.name for p in tmp_path.iterdir() if p.is_dir())
        # No new directories should have been created
        assert final_dirs == initial_dirs
