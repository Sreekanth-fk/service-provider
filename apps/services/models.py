from django.db import models
from service_core.models import BaseModel


class Service(BaseModel):

    name = models.CharField(
        max_length=255
    )

    description = models.TextField(
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name