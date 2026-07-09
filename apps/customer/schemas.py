from drf_spectacular.utils import extend_schema
from .serializers import (
    CustomerProfileSerializer,
    UpdateCustomerProfileSerializer,
    CustomerProviderSerializer,
    CustomerServiceSerializer,
    CustomerBookingSerializer,
    CrontabScheduleUpdateSerializer,
    PeriodicTaskTimeResponseSerializer,
)

customer_profile_schema = extend_schema(
    tags=["Customer"],
    summary="Get Customer Profile",
    description="Retrieve the profile details of the authenticated customer user.",
    responses={200: CustomerProfileSerializer},
)

update_customer_profile_schema = extend_schema(
    tags=["Customer"],
    summary="Update Customer Profile",
    description="Update username and email of the authenticated customer user.",
    request=UpdateCustomerProfileSerializer,
    responses={200: UpdateCustomerProfileSerializer},
)

provider_list_schema = extend_schema(
    tags=["Customer"],
    summary="List Providers",
    description="Retrieve a list of all providers. Accessible by authenticated customers.",
    responses={200: CustomerProviderSerializer(many=True)},
)

provider_detail_schema = extend_schema(
    tags=["Customer"],
    summary="Get Provider Detail",
    description="Retrieve detailed information about a specific provider by ID. Accessible by authenticated customers.",
    responses={200: CustomerProviderSerializer},
)

service_list_schema = extend_schema(
    tags=["Customer"],
    summary="List Services",
    description="Retrieve a list of all active services. Accessible by authenticated customers.",
    responses={200: CustomerServiceSerializer(many=True)},
)

customer_booking_list_schema = extend_schema(
    tags=["Customer"],
    summary="List Customer Bookings",
    description="Retrieve a list of all bookings created by the authenticated customer.",
    responses={200: CustomerBookingSerializer(many=True)},
)

admin_periodic_task_time_update_schema = extend_schema(
    tags=["Admin - Periodic Tasks"],
    summary="Update Good Morning Email Schedule",
    description="Update the cron schedule (minute, hour, day, etc.) for the daily Good Morning email task. Admin only access.",
    request=CrontabScheduleUpdateSerializer,
    responses={200: PeriodicTaskTimeResponseSerializer},
)
