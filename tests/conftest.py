import pytest
from django.test import Client

from tests.factories import DocumentFactory, ProjectFactory, UserFactory


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def other_user():
    return UserFactory()


@pytest.fixture
def authenticated_client(user) -> Client:
    c = Client()
    c.force_login(user)
    return c


@pytest.fixture
def project(user):
    return ProjectFactory(owner=user)


@pytest.fixture
def document(project):
    return DocumentFactory(project=project)
