import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView

from apps.documents.services import DocumentService
from apps.projects.forms import ProjectForm
from apps.projects.models import Project
from apps.projects.services import ProjectService

logger = logging.getLogger(__name__)


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = "projects/list.html"
    context_object_name = "projects"
    login_url = "/accounts/login/"

    def get_queryset(self):
        return ProjectService.get_for_user(self.request.user)


class ProjectCreateView(LoginRequiredMixin, View):
    template_name = "projects/form.html"
    login_url = "/accounts/login/"

    def get(self, request):
        form = ProjectForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = ProjectService.create(
                owner=request.user,
                name=form.cleaned_data["name"],
                description=form.cleaned_data.get("description", ""),
                tech_stack=form.cleaned_data.get("tech_stack", ""),
            )
            messages.success(request, f'Project "{project.name}" created successfully.')
            return redirect("project-detail", project_id=project.pk)
        return render(request, self.template_name, {"form": form})


class ProjectDetailView(LoginRequiredMixin, View):
    template_name = "projects/detail.html"
    login_url = "/accounts/login/"

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id, owner=request.user)
        documents = DocumentService.get_for_project(project)
        return render(
            request,
            self.template_name,
            {
                "project": project,
                "documents": documents,
            },
        )


class ProjectUpdateView(LoginRequiredMixin, View):
    template_name = "projects/form.html"
    login_url = "/accounts/login/"

    def get(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id, owner=request.user)
        form = ProjectForm(instance=project)
        documents = DocumentService.get_for_project(project)
        ctx = {"form": form, "project": project, "documents": documents}
        return render(request, self.template_name, ctx)

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id, owner=request.user)
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            ProjectService.update(
                project=project,
                name=form.cleaned_data["name"],
                description=form.cleaned_data.get("description", ""),
                tech_stack=form.cleaned_data.get("tech_stack", ""),
            )
            messages.success(request, "Project updated successfully.")
            return redirect("project-detail", project_id=project.pk)
        documents = DocumentService.get_for_project(project)
        ctx = {"form": form, "project": project, "documents": documents}
        return render(request, self.template_name, ctx)


class ProjectArchiveView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id, owner=request.user)
        ProjectService.archive(project)
        messages.success(request, f'Project "{project.name}" archived.')
        return redirect("project-list")


class RequirementsUploadView(LoginRequiredMixin, View):
    login_url = "/accounts/login/"

    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id, owner=request.user)
        files = request.FILES.getlist("files")

        if not files:
            messages.error(request, "No files selected.")
            return redirect("project-detail", project_id=project_id)

        success_count = 0
        for f in files:
            try:
                DocumentService.upload(project, request.user, f, f.name)
                success_count += 1
            except ValidationError as e:
                messages.error(request, f"{f.name}: {e}")
            except Exception as e:
                logger.error("Error uploading file %s: %s", f.name, e)
                messages.error(request, f"{f.name}: Upload failed.")

        if success_count:
            messages.success(request, f"{success_count} file(s) uploaded successfully.")

        return redirect("project-detail", project_id=project_id)
