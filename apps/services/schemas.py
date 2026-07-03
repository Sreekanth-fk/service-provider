from drf_spectacular.utils import extend_schema

from .serializers import ServiceSerializer


service_list_schema = extend_schema(
    tags=["Services"],
    summary="Service List",
    description="Returns all active services.",
    responses={
        200: ServiceSerializer(many=True),
    },
)
from .serializers import ServiceManageSerializer


service_manage_schema = extend_schema(
    tags=["Services"],
    summary="Create / Update Service",
    description="Create or Update Service.",
    request=ServiceManageSerializer,
    responses={
        200: ServiceSerializer,
        201: ServiceSerializer,
    },
)