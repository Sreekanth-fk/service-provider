from django.contrib import admin

from .models import Provider


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "phone",
        "service",
        "experience",
        "is_approved",
    )
    list_filter = (
        "is_approved",
        "service",
    )
    search_fields = (
        "user__username",
        "user__email",
        "phone",
    )
