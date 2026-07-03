from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "provider",
        "service",
        "date",
        "start_time",
        "end_time",
        "status",
    )
    list_filter = (
        "status",
        "date",
    )
    search_fields = (
        "customer__username",
        "customer__email",
        "provider__user__username",
        "provider__user__email",
        "service__name",
    )
