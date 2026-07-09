from django.urls import path

from .views import (
    ChatRoomListAPIView,
    ChatMessageListAPIView,
    MarkMessageReadAPIView,
)

app_name = "chat"

urlpatterns = [
    path("rooms/", ChatRoomListAPIView.as_view(), name="chat-room-list"),
    path(
        "rooms/<int:room_id>/messages/",
        ChatMessageListAPIView.as_view(),
        name="chat-message-list",
    ),
    path(
        "messages/<int:pk>/read/",
        MarkMessageReadAPIView.as_view(),
        name="mark-message-read",
    ),
]
