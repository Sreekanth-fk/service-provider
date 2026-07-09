from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.provider.models import Provider
from apps.services.models import Service
from apps.bookings.models import Booking
from .serializers import (
    CustomerProfileSerializer,
    UpdateCustomerProfileSerializer,
    CustomerProviderSerializer,
    CustomerServiceSerializer,
    CustomerBookingSerializer,
    CrontabScheduleUpdateSerializer,
    PeriodicTaskTimeResponseSerializer,
)
from .schemas import (
    customer_profile_schema,
    update_customer_profile_schema,
    provider_list_schema,
    provider_detail_schema,
    service_list_schema,
    customer_booking_list_schema,
    admin_periodic_task_time_update_schema,
)
from django_celery_beat.models import CrontabSchedule, PeriodicTask


class CustomerProfileAPIView(APIView):
    """
    API view to retrieve customer profile details.
    """
    serializer_class = CustomerProfileSerializer
    permission_classes = (IsAuthenticated,)

    @customer_profile_schema
    def get(self, request):
        if request.user.role != "customer":
            return Response(
                {
                    "success": False,
                    "message": "Access denied. Only customers can access this resource.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(
            request.user, context={"request": request}
        )
        return Response(
            {
                "success": True,
                "message": "Customer profile fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UpdateCustomerProfileAPIView(APIView):
    """
    API view to update customer profile details.
    """
    serializer_class = UpdateCustomerProfileSerializer
    permission_classes = (IsAuthenticated,)

    @update_customer_profile_schema
    def patch(self, request):
        if request.user.role != "customer":
            return Response(
                {
                    "success": False,
                    "message": "Access denied. Only customers can update their profile.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Customer profile updated successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ProviderListAPIView(APIView):
    """
    API view to list approved providers for customers.
    """
    serializer_class = CustomerProviderSerializer
    permission_classes = (IsAuthenticated,)

    @provider_list_schema
    def get(self, request):
        if request.user.role != "customer":
            return Response(
                {
                    "success": False,
                    "message": "Access denied. Only customers can access this resource.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = Provider.objects.filter(is_approved=True)
        serializer = self.serializer_class(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "success": True,
                "message": "Providers fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ProviderDetailAPIView(APIView):
    """
    API view to get details of a specific approved provider.
    """
    serializer_class = CustomerProviderSerializer
    permission_classes = (IsAuthenticated,)

    @provider_detail_schema
    def get(self, request, pk):
        if request.user.role != "customer":
            return Response(
                {
                    "success": False,
                    "message": "Access denied. Only customers can access this resource.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        provider = get_object_or_404(Provider, pk=pk, is_approved=True)
        serializer = self.serializer_class(
            provider, context={"request": request}
        )
        return Response(
            {
                "success": True,
                "message": "Provider details fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ServiceListAPIView(APIView):
    """
    API view to list active services.
    """
    serializer_class = CustomerServiceSerializer
    permission_classes = (IsAuthenticated,)

    @service_list_schema
    def get(self, request):
        if request.user.role != "customer":
            return Response(
                {
                    "success": False,
                    "message": "Access denied. Only customers can access this resource.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = Service.objects.filter(is_active=True).order_by("name")
        serializer = self.serializer_class(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "success": True,
                "message": "Services fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class AdminPeriodicTaskTimeUpdateView(APIView):
    """
    Admin-only API to update the schedule time of the Good Morning email periodic task.
    """
    serializer_class = CrontabScheduleUpdateSerializer
    permission_classes = (IsAuthenticated,)

    @admin_periodic_task_time_update_schema
    def patch(self, request):
        # Admin check
        if not request.user.is_staff:
            return Response(
                {"success": False, "message": "Only admins can update schedule."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the specific periodic task
        task = get_object_or_404(PeriodicTask, name="send-good-morning-emails")

        # Validate input
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        crontab_data = serializer.validated_data

        # Get or create the crontab schedule (reuses existing if identical)
        crontab, _ = CrontabSchedule.objects.get_or_create(**crontab_data)

        # Update task's crontab
        task.crontab = crontab
        task.save(update_fields=["crontab", "date_changed"])

        # Return updated task
        response_serializer = PeriodicTaskTimeResponseSerializer(task)
        return Response(
            {
                "success": True,
                "message": "Schedule updated successfully.",
                "data": response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )
