"""User admin configuration."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.user.models import PasswordResetOTP, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin with role and status fields."""

    list_display = ("email", "username", "role", "status", "is_active", "date_joined")
    list_filter = ("role", "status", "is_active", "is_staff")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Extended", {"fields": ("role", "status", "image", "phone", "address", "last_active_at")}),
    )


@admin.register(PasswordResetOTP)
class PasswordResetOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "otp", "is_used", "created_at")
    list_filter = ("is_used",)
    search_fields = ("user__email",)
    readonly_fields = ("otp", "created_at")
