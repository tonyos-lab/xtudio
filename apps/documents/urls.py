from django.urls import path

from apps.documents import views

urlpatterns = [
    path("<uuid:doc_id>/view/", views.DocumentViewView.as_view(), name="document-view"),
    path(
        "<uuid:doc_id>/download/",
        views.DocumentDownloadView.as_view(),
        name="document-download",
    ),
    path(
        "<uuid:doc_id>/delete/",
        views.DocumentDeleteView.as_view(),
        name="document-delete",
    ),
]
