from django.urls import path

from apps.dashboard import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("", views.DashboardView.as_view(), name="dashboard-home"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard-slash"),
]
