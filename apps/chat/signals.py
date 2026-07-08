from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.bookings.models import Booking
from .models import ChatRoom


@receiver(post_save, sender=Booking)
def create_chat_room_on_booking(sender, instance, created, **kwargs):
    if created:
        ChatRoom.objects.get_or_create(
            booking=instance,
            defaults={
                "customer": instance.customer,
                "provider": instance.provider.user,
            },
        )
