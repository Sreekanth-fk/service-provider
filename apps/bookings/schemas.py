from drf_spectacular.utils import extend_schema

from .serializers import BookingSerializer, BookingActionSerializer


booking_create_schema = extend_schema(
    tags=["Bookings"],
    summary="Create Booking",
    description="Allows a customer to create a new booking.",
    request=BookingSerializer,
    responses={201: BookingSerializer},
)

customer_booking_list_schema = extend_schema(
    tags=["Bookings"],
    summary="Customer Booking List",
    description="Returns all bookings created by the logged-in customer.",
    responses={200: BookingSerializer(many=True)},
)

provider_booking_list_schema = extend_schema(
    tags=["Bookings"],
    summary="Provider Booking List",
    description="Returns all bookings assigned to the logged-in provider.",
    responses={200: BookingSerializer(many=True)},
)

provider_booking_action_schema = extend_schema(
    tags=["Bookings"],
    summary="Accept or Reject Booking",
    description="Allows a provider to accept or reject an assigned booking. Send action='accept' or action='reject'.",
    request=BookingActionSerializer,
    responses={200: BookingSerializer},
)
