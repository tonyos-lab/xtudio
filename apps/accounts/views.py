import logging

from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeDoneView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView, UpdateView

from apps.accounts.forms import LoginForm, ProfileEditForm, RegisterForm

logger = logging.getLogger(__name__)

User = get_user_model()


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        form = RegisterForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            first_name = form.cleaned_data.get("first_name", "")
            last_name = form.cleaned_data.get("last_name", "")
            username = email.split("@")[0]
            # Ensure unique username
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            auth.login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, f"Welcome to xtudio, {user.username}!")
            return redirect("dashboard")
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("dashboard")
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            try:
                user_obj = User.objects.get(email=email)
                user = auth.authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    auth.login(request, user)
                    next_url = request.GET.get("next", "")
                    if next_url:
                        return redirect(next_url)
                    return redirect("dashboard")
                else:
                    messages.error(request, "Invalid email or password.")
            except User.DoesNotExist:
                messages.error(request, "Invalid email or password.")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def get(self, request):
        auth.logout(request)
        return redirect("accounts-login")

    def post(self, request):
        auth.logout(request)
        return redirect("accounts-login")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"
    login_url = "/accounts/login/"


class ProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = ProfileEditForm
    template_name = "accounts/profile_edit.html"
    login_url = "/accounts/login/"

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, "Profile updated successfully.")
        return "/accounts/profile/"


class PasswordChangeView(LoginRequiredMixin, PasswordChangeDoneView):
    template_name = "accounts/password_change.html"
    login_url = "/accounts/login/"


class VerifyEmailView(View):
    template_name = "accounts/verify_email_pending.html"

    def get(self, request, token: str):
        return render(request, self.template_name, {"token": token})


class CustomPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.txt"
    success_url = "/accounts/password/reset/done/"


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = "/accounts/login/"
