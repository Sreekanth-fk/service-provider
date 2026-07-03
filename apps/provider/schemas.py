from drf_spectacular.utils import extend_schema, OpenApiParameter
from .serializers import ProviderSerializer


provider_list_schema = extend_schema(
    tags=["Providers"],
    summary="List Providers",
    description="Retrieve a list of provider profiles. Supports filtering by service ID and approval status.",
    parameters=[
        OpenApiParameter(
            name="service",
            description="Filter by service ID",
            required=False,
            type=int,
        ),
        OpenApiParameter(
            name="is_approved",
            description="Filter by approval status (true/false)",
            required=False,
            type=str,
        ),
    ],
    responses={200: ProviderSerializer(many=True)},
)

provider_create_update_schema = extend_schema(
    tags=["Providers"],
    summary="Create or Update Provider",
    description="Create a new provider profile, or update an existing one if the 'id' field is supplied in the request body.",
    request=ProviderSerializer,
    responses={200: ProviderSerializer},
)

provider_detail_schema = extend_schema(
    tags=["Providers"],
    summary="Get Provider Details",
    description="Fetch details of a specific provider profile by its ID.",
    responses={200: ProviderSerializer},
)

provider_action_schema = extend_schema(
    tags=["Providers"],
    summary="Approve or Reject Provider Profile",
    description="Allows administrators/staff to approve or reject a provider's profile application.",
    responses={200: ProviderSerializer},
)
