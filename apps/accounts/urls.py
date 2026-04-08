from django.urls import path

from apps.accounts import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="accounts-register"),
    path("login/", views.LoginView.as_view(), name="accounts-login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("profile/", views.ProfileView.as_view(), name="accounts-profile"),
    path("profile/edit/", views.ProfileEditView.as_view(), name="profile-edit"),
    path("password/change/", views.PasswordChangeView.as_view(), name="password-change"),
    path("verify-email/<str:token>/", views.VerifyEmailView.as_view(), name="verify-email"),
    path("password/reset/", views.CustomPasswordResetView.as_view(), name="password-reset"),
    path(
        "password/reset/confirm/",
        views.CustomPasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
