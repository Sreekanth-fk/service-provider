from django.urls import path

from apps.bookings.views import CustomerBookingListAPIView
from .views import (
    CustomerProfileAPIView,
    UpdateCustomerProfileAPIView,
    ProviderListAPIView,
    ProviderDetailAPIView,
    ServiceListAPIView,
    AdminPeriodicTaskTimeUpdateView,
)

app_name = "customer"

urlpatterns = [
    path("profile/", CustomerProfileAPIView.as_view(), name="profile"),
    path("profile/update/", UpdateCustomerProfileAPIView.as_view(), name="update_profile"),
    path("providers/", ProviderListAPIView.as_view(), name="provider_list"),
    path("providers/<int:pk>/", ProviderDetailAPIView.as_view(), name="provider_detail"),
    path("services/", ServiceListAPIView.as_view(), name="service_list"),
    path("bookings/", CustomerBookingListAPIView.as_view(), name="booking_list"),
    path(
        "admin/periodic-tasks/send-good-morning-emails/time/",
        AdminPeriodicTaskTimeUpdateView.as_view(),
        name="periodic_task_time_update",
    ),
]
