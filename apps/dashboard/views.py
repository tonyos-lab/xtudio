from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.documents.models import Document
from apps.projects.models import Project


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/dashboard.html"
    login_url = "/accounts/login/"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        user_projects = Project.objects.filter(owner=user)
        ctx["total_projects"] = user_projects.count()
        ctx["active_projects"] = user_projects.filter(status=Project.STATUS_ACTIVE).count()
        ctx["total_documents"] = Document.objects.filter(project__owner=user).count()
        ctx["recent_projects"] = user_projects.order_by("-created_at")[:5]
        ctx["page_title"] = "Dashboard"
        return ctx
