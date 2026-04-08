import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from apps.documents.models import Document
from apps.documents.services import DocumentService

logger = logging.getLogger(__name__)


class DocumentViewView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"

    def get(self, request, doc_id):
        document = get_object_or_404(Document, pk=doc_id)
        try:
            return DocumentService.get_file_response(document, request.user, inline=True)
        except PermissionDenied:
            raise
        except FileNotFoundError:
            raise Http404("File not found on disk.")
        except Exception as exc:
            logger.error("Error serving document %s: %s", doc_id, exc)
            raise Http404("Could not serve file.")


class DocumentDownloadView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"

    def get(self, request, doc_id):
        document = get_object_or_404(Document, pk=doc_id)
        try:
            return DocumentService.get_file_response(document, request.user, inline=False)
        except PermissionDenied:
            raise
        except FileNotFoundError:
            raise Http404("File not found on disk.")
        except Exception as exc:
            logger.error("Error downloading document %s: %s", doc_id, exc)
            raise Http404("Could not serve file.")


class DocumentDeleteView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"

    def post(self, request, doc_id):
        document = get_object_or_404(Document, pk=doc_id)
        project_id = document.project.id
        try:
            DocumentService.delete(document, request.user)
            messages.success(request, f'"{document.filename}" removed.')
        except PermissionDenied:
            messages.error(request, "You do not have permission to remove this document.")
        except Exception as exc:
            logger.error("Error deleting document %s: %s", doc_id, exc)
            messages.error(request, "Could not remove document.")
        return redirect("project-detail", project_id=project_id)
