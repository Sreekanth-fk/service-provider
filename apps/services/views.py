from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Service
from .serializers import ServiceSerializer
from .schemas import service_list_schema
from .serializers import (
    ServiceSerializer,
    ServiceManageSerializer,
)

from .schemas import (
    service_list_schema,
    service_manage_schema,
)


class ServiceAPIView(APIView):

    serializer_class = ServiceSerializer

    permission_classes = (IsAuthenticated,)

    @service_list_schema
    def get(self, request):

        queryset = Service.objects.filter(
            is_active=True
        ).order_by("name")

        serializer = self.serializer_class(
            queryset,
            many=True
        )

        return Response(
            {
                "success": True,
                "message": "Services fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

class ServiceManageAPIView(APIView):

    serializer_class = ServiceManageSerializer

    permission_classes = (IsAuthenticated,)

    @service_manage_schema
    def post(self, request):

        serializer = self.serializer_class(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Service created successfully.",
                "data": ServiceSerializer(
                    serializer.instance
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @service_manage_schema
    def patch(self, request):

        service = Service.objects.filter(
            id=request.data.get("id")
        ).first()

        if not service:
            return Response(
                {
                    "success": False,
                    "message": "Service not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.serializer_class(
            service,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            {
                "success": True,
                "message": "Service updated successfully.",
                "data": ServiceSerializer(
                    serializer.instance
                ).data,
            },
            status=status.HTTP_200_OK,
        )