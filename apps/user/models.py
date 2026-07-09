from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import pytz


def validate_timezone_name(value):
    if value not in pytz.all_timezones_set:
        raise ValidationError(f"'{value}' is not a valid timezone.")


class User(AbstractUser):
    """
    Custom User Model
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        CUSTOMER = "customer", "Customer"
        PROVIDER = "provider", "Provider"

    email = models.EmailField(
        unique=True,
        verbose_name="Email Address"
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )

    timezone = models.CharField(
        max_length=100,
        default="UTC",
        validators=[validate_timezone_name]
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"