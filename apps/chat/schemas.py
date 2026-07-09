from drf_spectacular.utils import extend_schema

from .serializers import (
    ChatRoomSerializer,
    ChatMessageSerializer,
    MarkReadSerializer,
)

chat_room_list_schema = extend_schema(
    tags=["Chat"],
    summary="Chat Room List",
    description="Returns all chat rooms for the authenticated user (customer or provider).",
    responses={200: ChatRoomSerializer(many=True)},
)

chat_message_list_schema = extend_schema(
    tags=["Chat"],
    summary="Chat Messages",
    description="Returns all messages for a specific chat room, ordered by creation time.",
    responses={200: ChatMessageSerializer(many=True)},
)

mark_message_read_schema = extend_schema(
    tags=["Chat"],
    summary="Mark Message Read",
    description="Mark a specific chat message as read by the recipient.",
    request=MarkReadSerializer,
    responses={200: ChatMessageSerializer},
)
