from django.conf import settings
from django.db import models
from service_core.models import BaseModel


class ChatRoom(BaseModel):
    booking = models.OneToOneField(
        "bookings.Booking",
        on_delete=models.CASCADE,
        related_name="chat_room",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_rooms_as_customer",
    )
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_rooms_as_provider",
    )
    # created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom: Booking {self.booking_id}"


class ChatMessage(BaseModel):
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"Message by {self.sender} in Room {self.room_id}"
