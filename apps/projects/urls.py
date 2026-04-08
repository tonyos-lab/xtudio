from django.urls import path

from apps.projects import views

urlpatterns = [
    path("", views.ProjectListView.as_view(), name="project-list"),
    path("new/", views.ProjectCreateView.as_view(), name="project-create"),
    path("<uuid:project_id>/", views.ProjectDetailView.as_view(), name="project-detail"),
    path("<uuid:project_id>/edit/", views.ProjectUpdateView.as_view(), name="project-edit"),
    path("<uuid:project_id>/archive/", views.ProjectArchiveView.as_view(), name="project-archive"),
    path(
        "<uuid:project_id>/upload/",
        views.RequirementsUploadView.as_view(),
        name="requirements-upload",
    ),
]
