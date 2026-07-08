from django.contrib import admin

from .models import ChatRoom, ChatMessage


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking",
        "customer",
        "provider",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = (
        "customer__username",
        "provider__username",
        "booking__id",
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "room",
        "sender",
        "message",
        "is_read",
        "created_at",
    )
    list_filter = (
        "is_read",
        "created_at",
    )
    search_fields = (
        "message",
        "sender__username",
    )
