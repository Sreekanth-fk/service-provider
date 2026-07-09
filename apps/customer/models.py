from django.db import models
from django.conf import settings
from service_core.models import BaseModel

class Customer(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Customer: {self.user.username}"


class EmailLog(BaseModel):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="email_logs"
    )
    email_type = models.CharField(max_length=50)
    sent_date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["customer", "email_type", "sent_date"],
                name="unique_customer_email_type_date"
            )
        ]
        verbose_name = "Email Log"
        verbose_name_plural = "Email Logs"

    def __str__(self):
        return f"{self.email_type} to {self.customer.user.email} on {self.sent_date}"
