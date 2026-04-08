import re
from pathlib import Path
from typing import Any

from django.conf import settings

from apps.workspace.exceptions import WorkspaceError


def _get_workspace_root() -> Path:
    return Path(settings.WORKSPACE_ROOT)


def sanitize_filename(filename: str) -> str:
    name = Path(filename).stem
    ext = Path(filename).suffix.lower()
    safe_name = re.sub(r"[^\w\-_\.]", "_", name)
    return f"{safe_name}{ext}"


class WorkspaceService:
    @staticmethod
    def get_user_path(username: str) -> Path:
        return _get_workspace_root() / username

    @staticmethod
    def get_project_path(username: str, project_id: str) -> Path:
        return _get_workspace_root() / username / project_id

    @staticmethod
    def get_docs_path(username: str, project_id: str) -> Path:
        return _get_workspace_root() / username / project_id / "docs"

    @staticmethod
    def get_src_path(username: str, project_id: str) -> Path:
        return _get_workspace_root() / username / project_id / "src"

    @staticmethod
    def create_user_workspace(username: str) -> Path:
        user_path = _get_workspace_root() / username
        user_path.mkdir(parents=True, exist_ok=True)
        return user_path

    @staticmethod
    def create_project_workspace(username: str, project_id: str) -> Path:
        project_path = _get_workspace_root() / username / project_id
        docs_path = project_path / "docs"
        src_path = project_path / "src"
        docs_path.mkdir(parents=True, exist_ok=True)
        src_path.mkdir(parents=True, exist_ok=True)
        return project_path

    @staticmethod
    def save_file(
        username: str,
        project_id: str,
        filename: str,
        content: bytes,
    ) -> Path:
        docs_path = _get_workspace_root() / username / project_id / "docs"
        docs_path.mkdir(parents=True, exist_ok=True)
        # Check raw filename for traversal before sanitizing
        raw_target = (docs_path / filename).resolve()
        WorkspaceService.validate_path(docs_path, raw_target)
        safe_filename = sanitize_filename(filename)
        target = docs_path / safe_filename
        WorkspaceService.validate_path(docs_path, target)
        target.write_bytes(content)
        return target

    @staticmethod
    def list_documents(username: str, project_id: str) -> list[dict[str, Any]]:
        docs_path = _get_workspace_root() / username / project_id / "docs"
        if not docs_path.exists():
            return []
        results = []
        for f in sorted(docs_path.iterdir()):
            if f.is_file():
                results.append(
                    {
                        "filename": f.name,
                        "file_type": f.suffix.lstrip(".").lower(),
                        "file_size": f.stat().st_size,
                        "file_path": str(f),
                        "modified_at": f.stat().st_mtime,
                    }
                )
        return results

    @staticmethod
    def get_file_path(username: str, project_id: str, filename: str) -> Path:
        docs_path = _get_workspace_root() / username / project_id / "docs"
        target = docs_path / filename
        WorkspaceService.validate_path(docs_path, target)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {filename}")
        return target

    @staticmethod
    def validate_path(base: Path, target: Path) -> None:
        try:
            target.resolve().relative_to(base.resolve())
        except ValueError as exc:
            raise WorkspaceError(
                f"Path traversal detected: '{target}' is not under '{base}'"
            ) from exc
