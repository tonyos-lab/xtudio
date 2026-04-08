import logging
import mimetypes
from pathlib import Path
from typing import Any

from django.core.exceptions import PermissionDenied, ValidationError
from django.http import FileResponse

from apps.documents.models import Document
from apps.projects.models import Project
from apps.workspace.services import WorkspaceService, sanitize_filename

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB


def validate_upload(file_obj: Any) -> None:
    ext = Path(file_obj.name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"File type '{ext}' not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    if file_obj.size > MAX_FILE_SIZE_BYTES:
        raise ValidationError(
            f"File size {file_obj.size} bytes exceeds maximum {MAX_FILE_SIZE_BYTES} bytes (10MB)."
        )


class DocumentService:
    @staticmethod
    def upload(
        project: Project,
        uploaded_by: Any,
        file_obj: Any,
        original_filename: str,
    ) -> Document:
        validate_upload(file_obj)

        safe_filename = sanitize_filename(original_filename)

        if Document.objects.filter(project=project, filename=safe_filename).exists():
            raise ValidationError(
                f'"{safe_filename}" already exists in this project. Remove the existing file first.'
            )

        content = file_obj.read()

        saved_path = WorkspaceService.save_file(
            username=project.owner.username,
            project_id=str(project.id),
            filename=safe_filename,
            content=content,
        )

        ext = Path(safe_filename).suffix.lstrip(".").lower()
        document = Document.objects.create(
            project=project,
            filename=safe_filename,
            original_filename=original_filename,
            file_type=ext,
            file_size=len(content),
            file_path=str(saved_path),
            source=Document.SOURCE_UPLOAD,
            uploaded_by=uploaded_by,
        )

        try:
            from apps.audit_trail.constants import AuditCategory, AuditOperation
            from apps.audit_trail.services import AuditService

            AuditService.log_success(
                category=AuditCategory.DOCUMENT,
                operation=AuditOperation.UPLOAD,
                action=f'Document "{safe_filename}" uploaded to project "{project.name}"',
                user=uploaded_by,
                project_id=project.id,
            )
        except Exception as exc:
            logger.warning("Failed to write audit log for document upload: %s", exc)

        return document

    @staticmethod
    def get_for_project(project: Project) -> list[Document]:
        return list(Document.objects.filter(project=project).order_by("-created_at"))

    @staticmethod
    def delete(document: Document, user: Any) -> None:
        if document.project.owner != user:
            raise PermissionDenied

        try:
            file_path = WorkspaceService.get_file_path(
                username=user.username,
                project_id=str(document.project.id),
                filename=document.filename,
            )
            file_path.unlink(missing_ok=True)
        except Exception as exc:
            logger.warning("Could not delete file from disk for document %s: %s", document.id, exc)

        try:
            from apps.audit_trail.constants import AuditCategory, AuditOperation
            from apps.audit_trail.services import AuditService

            project_name = document.project.name
            AuditService.log_success(
                category=AuditCategory.DOCUMENT,
                operation=AuditOperation.DELETE,
                action=f'Document "{document.filename}" deleted from project "{project_name}"',
                user=user,
                project_id=document.project.id,
            )
        except Exception as exc:
            logger.warning("Failed to write audit log for document delete: %s", exc)

        document.delete()

    @staticmethod
    def get_file_response(document: Document, user: Any, inline: bool = True) -> FileResponse:
        if document.project.owner != user:
            raise PermissionDenied

        file_path = WorkspaceService.get_file_path(
            username=user.username,
            project_id=str(document.project.id),
            filename=document.filename,
        )

        inline_types: dict[str, str] = {
            ".md": "text/plain",
            ".txt": "text/plain",
            ".pdf": "application/pdf",
        }
        ext = Path(document.filename).suffix.lower()
        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or inline_types.get(ext, "application/octet-stream")
        response = FileResponse(
            open(file_path, "rb"),  # noqa: WPS515
            content_type=content_type,
        )
        disposition = "inline" if inline else "attachment"
        response["Content-Disposition"] = f'{disposition}; filename="{document.original_filename}"'
        return response
