from django.db import models
from django.conf import settings
from apps.services.models import Service
from service_core.models import BaseModel


class Provider(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="provider_profile"
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    experience = models.IntegerField(null=True, blank=True)
    details = models.TextField(blank=True, null=True)
    document = models.FileField(
        upload_to="provider_docs/",
        null=True,
        blank=True
    )
    is_approved = models.BooleanField(default=False)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.service})"
