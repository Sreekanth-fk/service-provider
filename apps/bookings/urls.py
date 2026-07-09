from django.urls import path

from .views import (
    BookingCreateAPIView,
    CustomerBookingListAPIView,
    ProviderBookingActionAPIView,
    ProviderBookingListAPIView,
)

urlpatterns = [
    path("create/", BookingCreateAPIView.as_view()),
    path("my-bookings/", CustomerBookingListAPIView.as_view()),
    # Provider APIs
    path("provider-bookings/", ProviderBookingListAPIView.as_view()),
    path("provider-bookings/<int:pk>/action/", ProviderBookingActionAPIView.as_view(),),
]
