from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.provider.models import Provider
from .models import Booking
from .schemas import (
    booking_create_schema,
    customer_booking_list_schema,
    provider_booking_action_schema,
    provider_booking_list_schema,
)
from .serializers import BookingSerializer


class BookingCreateAPIView(APIView):
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)

    @booking_create_schema
    def post(self, request, *args, **kwargs):
        if request.user.role != "customer":
            return Response(
                {
                    "status": False,
                    "message": "Only customers can create bookings.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "status": True,
                "message": "Booking created successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomerBookingListAPIView(APIView):
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)

    @customer_booking_list_schema
    def get(self, request, *args, **kwargs):
        queryset = Booking.objects.filter(customer=request.user)
        serializer = self.serializer_class(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "status": True,
                "message": "My bookings fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ProviderBookingListAPIView(APIView):
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)

    @provider_booking_list_schema
    def get(self, request, *args, **kwargs):
        provider = get_object_or_404(Provider, user=request.user)
        queryset = Booking.objects.filter(provider=provider)
        serializer = self.serializer_class(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "status": True,
                "message": "Provider bookings fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ProviderBookingActionAPIView(APIView):
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)

    @provider_booking_action_schema
    def patch(self, request, pk, *args, **kwargs):
        action = request.data.get("action")
        if action not in ["accept", "reject"]:
            return Response(
                {
                    "status": False,
                    "message": "Invalid action. Must be 'accept' or 'reject'.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        provider = get_object_or_404(Provider, user=request.user)
        booking = get_object_or_404(Booking, pk=pk)

        if booking.provider != provider:
            return Response(
                {
                    "status": False,
                    "message": "You do not have permission to manage this booking.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if action == "accept":
            booking.status = "ACCEPTED"
        elif action == "reject":
            booking.status = "REJECTED"

        booking.save()

        serializer = self.serializer_class(
            booking, context={"request": request}
        )
        return Response(
            {
                "status": True,
                "message": f"Booking {action}ed successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
