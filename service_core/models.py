from django.db import models
from django.contrib.auth import get_user_model
from service_core.middleware import get_current_user

User = get_user_model()


class BaseModel(models.Model):
    """
    Abstract Base Model that automatically tracks creation/update timestamps
    and the user (Token/JWT/Session authenticated) who created/updated the record.
    """
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # Resolve the request user from middleware threadlocal context
        user = get_current_user()
        if user and not user.is_anonymous:
            if not self.pk:  # Object is newly created
                self.created_by = user
            self.updated_by = user
            
        super().save(*args, **kwargs)
