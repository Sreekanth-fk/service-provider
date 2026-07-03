from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction

from apps.customer.models import Customer
from apps.provider.models import Provider
from apps.services.models import Service

User = get_user_model()


class CustomerRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ("phone", "address")
        extra_kwargs = {
            "phone": {"required": False, "allow_null": True, "allow_blank": True},
            "address": {"required": False, "allow_null": True, "allow_blank": True},
        }

    def validate_phone(self, value):
        import re
        if value:
            if not re.match(r"^\+?[0-9]{10,15}$", value):
                raise serializers.ValidationError(
                    "Phone number must be between 10 and 15 digits."
                )
        return value

    def validate_address(self, value):
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Address must be at least 5 characters long."
            )
        return value


class ProviderRegistrationSerializer(serializers.ModelSerializer):
    service_id = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(),
        source="service",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Provider
        fields = ("phone", "experience", "details", "service_id")
        extra_kwargs = {
            "phone": {"required": False, "allow_null": True, "allow_blank": True},
            "experience": {"required": False, "allow_null": True},
            "details": {"required": False, "allow_null": True, "allow_blank": True},
        }

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


class RegisterSerializer(serializers.ModelSerializer):
    """
    User Registration Serializer
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )

    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    role = serializers.ChoiceField(
        choices=[("customer", "Customer"), ("provider", "Provider")]
    )

    customer = CustomerRegistrationSerializer(source="customer_profile", required=False)
    provider = ProviderRegistrationSerializer(source="provider_profile", required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, "initial_data"):
            role = self.initial_data.get("role")
            if role == "customer":
                self.fields.pop("provider", None)
            elif role == "provider":
                self.fields.pop("customer", None)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "role",
            "password",
            "confirm_password",
            "customer",
            "provider",
        )

        read_only_fields = ("id",)

    def validate_email(self, value):

        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )

        return value

    def validate(self, attrs):

        if attrs.get("password") != attrs.get("confirm_password"):
            raise serializers.ValidationError(
                {"confirm_password": ["Passwords do not match."]}
            )

        role = attrs.get("role")

        if role == "customer":
            if "customer_profile" not in attrs or attrs.get("customer_profile") is None:
                raise serializers.ValidationError(
                    {"customer": ["Customer details are required."]}
                )
            attrs.pop("provider_profile", None)

        elif role == "provider":
            if "provider_profile" not in attrs or attrs.get("provider_profile") is None:
                raise serializers.ValidationError(
                    {"provider": ["Provider details are required."]}
                )
            attrs.pop("customer_profile", None)

        return attrs

    def create(self, validated_data):

        customer_data = validated_data.pop("customer_profile", None)
        provider_data = validated_data.pop("provider_profile", None)
        role = validated_data.get("role")

        validated_data.pop("confirm_password", None)

        password = validated_data.pop("password")

        with transaction.atomic():
            user = User(**validated_data)
            user.set_password(password)
            user.save()

            if role == "customer":
                Customer.objects.create(user=user, **customer_data)
            elif role == "provider":
                Provider.objects.create(user=user, **provider_data)

        return user

from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(serializers.Serializer):
    """
    User Login Serializer
    """

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    def validate(self, attrs):

        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "Email does not exist."}
            )

        user = authenticate(
            username=user.username,
            password=password
        )

        if user is None:
            raise serializers.ValidationError(
                {"password": "Invalid password."}
            )

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
            }
        }
        
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "role",
        )


class UpdateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )

    def validate_email(self, value):

        user = self.instance

        if User.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError(
                "Email already exists."
            )

        return value

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutSerializer(serializers.Serializer):

    refresh = serializers.CharField()

    def validate(self, attrs):

        self.token = attrs.get("refresh")

        return attrs

    def save(self, **kwargs):

        try:
            RefreshToken(self.token).blacklist()
        except Exception:
            raise serializers.ValidationError(
                {
                    "refresh": ["Invalid refresh token."]
                }
            )       