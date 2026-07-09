from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.services.models import Service
from apps.services.serializers import ServiceSerializer
from service_core.helpers.timezone import LocalizedDateTimeField
from .models import Provider

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "timezone")
        read_only_fields = ("id", "role")

    def validate_timezone(self, value):
        import pytz
        if value not in pytz.all_timezones_set:
            raise serializers.ValidationError("Invalid timezone.")
        return value


class ProviderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    service = ServiceSerializer(read_only=True)
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source="service",
        write_only=True,
        required=False,
        allow_null=True,
    )
    created_at = LocalizedDateTimeField(
        format="%d-%m-%Y %I:%M %p",
        read_only=True,
    )
    updated_at = LocalizedDateTimeField(
        format="%d-%m-%Y %I:%M %p",
        read_only=True,
    )

    class Meta:
        model = Provider
        fields = [
            "id",
            "user",
            "phone",
            "service",
            "service_id",
            "experience",
            "details",
            "document",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_approved", "created_at", "updated_at"]

    def validate_phone(self, value):
        import re
        if value:
            if not re.match(r"^\+?[0-9]{10,15}$", value):
                raise serializers.ValidationError(
                    "Phone number must be between 10 and 15 digits."
                )
        return value

    def validate_experience(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                "Experience cannot be negative."
            )
        return value

    def validate_details(self, value):
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Details must be at least 10 characters long."
            )
        return value

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user:
            return attrs

        user = request.user

        # During CREATE flow (when instance is not passed to serializer)
        if not self.instance:
            if user.role != "provider":
                raise serializers.ValidationError(
                    {"detail": "Only users with the provider role can create a provider profile."}
                )
            if Provider.objects.filter(user=user).exists():
                raise serializers.ValidationError(
                    {"detail": "A provider profile already exists for this user."}
                )
        else:
            # During UPDATE flow
            if user.role != "provider" and not user.is_staff:
                raise serializers.ValidationError(
                    {"detail": "Only the provider owner or staff can update this profile."}
                )

        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop("user", None)
        request = self.context.get("request")
        current_user = request.user if request else None

        if not current_user:
            raise serializers.ValidationError("User must be authenticated.")

        # Update nested User info if provided
        if user_data:
            for attr, value in user_data.items():
                setattr(current_user, attr, value)
            current_user.save()

        provider = Provider.objects.create(user=current_user, **validated_data)
        return provider

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", None)

        # Handle nested User update
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                setattr(user, attr, value)
            user.save()

        # Handle remaining Provider fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
