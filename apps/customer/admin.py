from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "user__email",)
    search_fields = ("user__username", "user__email", "phone")
