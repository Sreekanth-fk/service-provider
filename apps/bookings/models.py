from django.conf import settings
from django.db import models


class Booking(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pending"),
        ("ACCEPTED", "Accepted"),
        ("REJECTED", "Rejected"),
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_bookings",
    )

    provider = models.ForeignKey(
        "provider.Provider",
        on_delete=models.CASCADE,
        related_name="provider_bookings",
    )

    service = models.ForeignKey("services.Service", on_delete=models.CASCADE)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    address = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="PENDING"
    )

    def __str__(self):
        return f"{self.customer} - {self.service} ({self.status})"
