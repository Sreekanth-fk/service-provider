from django.urls import path

from .views import (
    ProviderActionAPIView,
    ProviderCreateUpdateAPIView,
    ProviderDetailAPIView,
    ProviderListAPIView,
)

app_name = "provider"

urlpatterns = [
    path("", ProviderListAPIView.as_view(), name="provider-list"),
    path("create-update/",ProviderCreateUpdateAPIView.as_view(),name="provider-create-update",),
    path("<int:pk>/", ProviderDetailAPIView.as_view(), name="provider-detail"),
    path("<int:pk>/action/",ProviderActionAPIView.as_view(),name="provider-action",),
]
