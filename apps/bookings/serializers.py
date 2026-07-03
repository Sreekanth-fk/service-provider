from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.provider.models import Provider
from apps.services.models import Service
from apps.services.serializers import ServiceSerializer
from .models import Booking

User = get_user_model()


class BookingActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=[("accept", "Accept"), ("reject", "Reject")]
    )


class BookingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "role")


class ProviderNestedSerializer(serializers.ModelSerializer):
    user = BookingUserSerializer(read_only=True)

    class Meta:
        model = Provider
        fields = ("id", "user", "phone", "experience")


class BookingSerializer(serializers.ModelSerializer):
    customer = BookingUserSerializer(read_only=True)
    provider = ProviderNestedSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)

    provider_id = serializers.PrimaryKeyRelatedField(
        queryset=Provider.objects.all(), source="provider", write_only=True
    )
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), source="service", write_only=True
    )

    class Meta:
        model = Booking
        fields = (
            "id",
            "customer",
            "provider",
            "provider_id",
            "service",
            "service_id",
            "date",
            "start_time",
            "end_time",
            "address",
            "status",
        )
        read_only_fields = ("id", "customer", "status")

    def validate_date(self, value):
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Booking date cannot be in the past.")
        return value

    def validate_address(self, value):
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError("Address must be at least 5 characters long.")
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user:
            raise serializers.ValidationError("User must be authenticated.")

        if request.user.role != "customer":
            raise serializers.ValidationError(
                "Only customers can create bookings."
            )

        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError(
                {"end_time": ["End time must be after start time."]}
            )

        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data["customer"] = request.user
        return super().create(validated_data)
