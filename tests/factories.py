import factory
from django.contrib.auth import get_user_model

from apps.documents.models import Document
from apps.projects.models import Project

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f"Project {n}")
    description = "Test project description"
    status = "draft"


class DocumentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Document

    project = factory.SubFactory(ProjectFactory)
    filename = factory.Sequence(lambda n: f"document_{n}.pdf")
    original_filename = factory.Sequence(lambda n: f"document_{n}.pdf")
    file_type = "pdf"
    file_size = 1024
    file_path = factory.Sequence(lambda n: f"workspace/user/project/docs/document_{n}.pdf")
    source = "upload"
