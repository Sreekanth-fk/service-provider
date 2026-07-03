from django.db import models
from django.contrib.auth.models import AbstractUser


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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.username} ({self.role})"