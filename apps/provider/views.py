from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Provider
from .schemas import (
    provider_action_schema,
    provider_create_update_schema,
    provider_detail_schema,
    provider_list_schema,
)
from .serializers import ProviderSerializer


class ProviderListAPIView(APIView):
    serializer_class = ProviderSerializer
    permission_classes = (IsAuthenticated,)

    @provider_list_schema
    def get(self, request, *args, **kwargs):
        queryset = Provider.objects.all()

        # Filtering support
        service_id = request.query_params.get("service")
        is_approved = request.query_params.get("is_approved")

        if service_id:
            queryset = queryset.filter(service_id=service_id)

        if is_approved is not None:
            is_approved_bool = is_approved.lower() == "true"
            queryset = queryset.filter(is_approved=is_approved_bool)

        serializer = self.serializer_class(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "status": True,
                "message": "Providers fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ProviderCreateUpdateAPIView(APIView):
    serializer_class = ProviderSerializer
    permission_classes = (IsAuthenticated,)

    @provider_create_update_schema
    def post(self, request, *args, **kwargs):
        provider_id = request.data.get("id")

        if provider_id:
            # UPDATE Flow
            provider = get_object_or_404(Provider, id=provider_id)

            # Check permissions (only owner or staff can edit)
            if provider.user != request.user and not request.user.is_staff:
                return Response(
                    {
                        "status": False,
                        "message": "You do not have permission to update this profile.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = self.serializer_class(
                provider,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            message = "Provider updated successfully."
            response_status = status.HTTP_200_OK
        else:
            # CREATE Flow
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            message = "Provider created successfully."
            response_status = status.HTTP_201_CREATED

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "status": True,
                "message": message,
                "data": serializer.data,
            },
            status=response_status,
        )


class ProviderDetailAPIView(APIView):
    serializer_class = ProviderSerializer
    permission_classes = (IsAuthenticated,)

    @provider_detail_schema
    def get(self, request, pk, *args, **kwargs):
        provider = get_object_or_404(Provider, pk=pk)
        serializer = self.serializer_class(
            provider, context={"request": request}
        )
        return Response(
            {
                "status": True,
                "message": "Provider details fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ProviderActionAPIView(APIView):
    serializer_class = ProviderSerializer
    permission_classes = (IsAuthenticated,)

    @provider_action_schema
    def patch(self, request, pk, *args, **kwargs):
        # Only admin / staff users are allowed to approve or reject
        if not request.user.is_staff and request.user.role != "admin":
            return Response(
                {
                    "status": False,
                    "message": "Only admins can perform this action.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        action = request.data.get("action")
        if action not in ["approve", "reject"]:
            return Response(
                {
                    "status": False,
                    "message": "Invalid action. Must be 'approve' or 'reject'.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        provider = get_object_or_404(Provider, pk=pk)
        provider.is_approved = action == "approve"
        provider.save()

        serializer = self.serializer_class(
            provider, context={"request": request}
        )
        return Response(
            {
                "status": True,
                "message": f"Provider {action}d successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
