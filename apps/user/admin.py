from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom User Admin
    """

    list_display = (
        "id",
        "username",
        "email",
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "username",
        "email",
    )

    ordering = ("id",)

    fieldsets = (
        (None, {
            "fields": (
                "username",
                "password",
            )
        }),
        ("Personal Information", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "role",
            )
        }),
        ("Permissions", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Important Dates", {
            "fields": (
                "last_login",
                "date_joined",
                "created_at",
                "updated_at",
            )
        }),
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "last_login",
        "date_joined",
    )