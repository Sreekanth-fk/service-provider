from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.provider.models import Provider
from apps.services.models import Service
from apps.bookings.models import Booking
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from service_core.helpers.timezone import LocalizedDateTimeField, LocalizedDateField

User = get_user_model()


class CustomerUserSerializer(serializers.ModelSerializer):
    """
    Serializer for nested User details in customer app serializers.
    """
    class Meta:
        model = User
        fields = ("id", "username", "email", "role", "timezone")
        read_only_fields = ("id", "role")


class CustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to retrieve Customer profile details.
    """
    created_at = LocalizedDateTimeField(format="%d-%m-%Y %I:%M %p", read_only=True)
    updated_at = LocalizedDateTimeField(format="%d-%m-%Y %I:%M %p", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "role",
            "timezone",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "role",
            "timezone",
            "created_at",
            "updated_at",
        )


class UpdateCustomerProfileSerializer(serializers.ModelSerializer):
    """
    Serializer to update Customer profile details.
    """
    class Meta:
        model = User
        fields = ("username", "email", "timezone")

    def validate_timezone(self, value):
        import pytz
        if value not in pytz.all_timezones_set:
            raise serializers.ValidationError("Invalid timezone.")
        return value

    def validate(self, attrs):
        email = attrs.get("email")
        if email:
            user = self.instance
            queryset = User.objects.filter(email=email)
            if user:
                queryset = queryset.exclude(id=user.id)
            if queryset.exists():
                raise serializers.ValidationError(
                    {"email": "Email already exists."}
                )
        return attrs

    def create(self, validated_data):
        # Fallback create implementation to meet constraint requirements
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CustomerServiceSerializer(serializers.ModelSerializer):
    """
    Serializer for Service records fetched by customers.
    """
    created_at = LocalizedDateTimeField(format="%d-%m-%Y %I:%M %p", read_only=True)
    updated_at = LocalizedDateTimeField(format="%d-%m-%Y %I:%M %p", read_only=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class CustomerProviderSerializer(serializers.ModelSerializer):
    """
    Serializer for listing and retrieving Provider profiles.
    """
    user = CustomerUserSerializer(read_only=True)
    service = CustomerServiceSerializer(read_only=True)

    class Meta:
        model = Provider
        fields = (
            "id",
            "user",
            "phone",
            "service",
            "experience",
            "details",
            "document",
            "is_approved",
        )
        read_only_fields = fields


class CustomerBookingProviderSerializer(serializers.ModelSerializer):
    """
    Simplified nested provider serializer for customer bookings.
    """
    user = CustomerUserSerializer(read_only=True)

    class Meta:
        model = Provider
        fields = ("id", "user", "phone", "experience")
        read_only_fields = fields


class CustomerBookingSerializer(serializers.ModelSerializer):
    """
    Serializer for customer bookings representation.
    """
    customer = CustomerUserSerializer(read_only=True)
    provider = CustomerBookingProviderSerializer(read_only=True)
    service = CustomerServiceSerializer(read_only=True)
    date = LocalizedDateField(format="%d-%m-%Y")

    class Meta:
        model = Booking
        fields = (
            "id",
            "customer",
            "provider",
            "service",
            "date",
            "start_time",
            "end_time",
            "status",
        )
        read_only_fields = fields


class CrontabScheduleUpdateSerializer(serializers.Serializer):
    """Serializer for updating crontab schedule fields."""
    minute = serializers.CharField(max_length=240, required=False, default="*")
    hour = serializers.CharField(max_length=96, required=False, default="*")
    day_of_week = serializers.CharField(max_length=64, required=False, default="*")
    day_of_month = serializers.CharField(max_length=124, required=False, default="*")
    month_of_year = serializers.CharField(max_length=64, required=False, default="*")
    timezone = serializers.CharField(max_length=100, required=False, default="UTC")


class PeriodicTaskTimeResponseSerializer(serializers.ModelSerializer):
    """Read-only serializer for PeriodicTask with nested crontab."""
    crontab = CrontabScheduleUpdateSerializer(read_only=True)
    date_changed = LocalizedDateTimeField(format="%d-%m-%Y %I:%M %p", read_only=True)

    class Meta:
        model = PeriodicTask
        fields = ("name", "task", "crontab", "enabled", "description", "date_changed")
        read_only_fields = fields
