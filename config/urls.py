from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),
    path("", include("apps.dashboard.urls")),
    path("projects/", include("apps.projects.urls")),
    path("documents/", include("apps.documents.urls")),
    path("accounts/", include("allauth.urls")),
]
