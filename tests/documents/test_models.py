import uuid

import pytest

from apps.documents.models import Document
from tests.factories import DocumentFactory


@pytest.mark.django_db
class TestDocumentModel:
    def test_document_has_uuid_primary_key(self):
        doc = DocumentFactory()
        assert isinstance(doc.id, uuid.UUID)

    def test_document_default_source_is_upload(self):
        doc = DocumentFactory()
        assert doc.source == Document.SOURCE_UPLOAD

    def test_document_ordering_is_newest_first(self):
        doc1 = DocumentFactory()
        doc2 = DocumentFactory(project=doc1.project)
        docs = list(Document.objects.filter(project=doc1.project))
        assert docs[0] == doc2  # newest first

    def test_document_str_returns_filename(self):
        doc = DocumentFactory(filename="my_doc.pdf")
        assert str(doc) == "my_doc.pdf"

    def test_document_source_constants(self):
        assert Document.SOURCE_UPLOAD == "upload"
        assert Document.SOURCE_AGENT == "agent"
        assert Document.SOURCE_SYSTEM == "system"
