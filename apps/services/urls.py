from django.urls import path

from .views import ServiceAPIView,ServiceManageAPIView

urlpatterns = [
    path("api/services/", ServiceAPIView.as_view(), name="service-list"),
    path("manage/", ServiceManageAPIView.as_view(), name="service-manage"),
]
