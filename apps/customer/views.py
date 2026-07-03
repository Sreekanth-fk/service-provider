from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.provider.models import Provider
from apps.services.models import Service
from apps.bookings.models import Booking

from .serializers import (
    CustomerProfileSerializer,
    UpdateCustomerProfileSerializer,
    CustomerProviderSerializer,
    CustomerServiceSerializer,
    CustomerBookingSerializer,
)
from .schemas import (
    customer_profile_schema,
    update_customer_profile_schema,
    provider_list_schema,
    provider_detail_schema,
    service_list_schema,
    customer_booking_list_schema,
)


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


class CustomerBookingListAPIView(APIView):
    """
    API view to list the customer's own bookings.
    """
    serializer_class = CustomerBookingSerializer
    permission_classes = (IsAuthenticated,)

    @customer_booking_list_schema
    def get(self, request):
        if request.user.role != "customer":
            return Response(
                {
                    "success": False,
                    "message": "Access denied. Only customers can access this resource.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = Booking.objects.filter(customer=request.user)
        serializer = self.serializer_class(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "success": True,
                "message": "My bookings fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
