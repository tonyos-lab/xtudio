from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "email_verified", "date_joined", "is_active")
    list_filter = ("email_verified", "is_active", "is_staff")
    search_fields = ("username", "email")
    fieldsets = UserAdmin.fieldsets + (  # type: ignore[operator]
        ("Profile", {"fields": ("bio", "avatar", "google_id", "email_verified")}),
    )
