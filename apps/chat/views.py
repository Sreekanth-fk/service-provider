from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ChatRoom, ChatMessage
from .schemas import (
    chat_room_list_schema,
    chat_message_list_schema,
    mark_message_read_schema,
)
from .serializers import (
    ChatRoomSerializer,
    ChatMessageSerializer,
    MarkReadSerializer,
)


class ChatRoomListAPIView(APIView):
    serializer_class = ChatRoomSerializer
    permission_classes = (IsAuthenticated,)

    @chat_room_list_schema
    def get(self, request):
        queryset = ChatRoom.objects.filter(
            customer=request.user
        ) | ChatRoom.objects.filter(
            provider=request.user
        )
        queryset = queryset.order_by("-created_at")

        serializer = self.serializer_class(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "success": True,
                "message": "Chat rooms fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ChatMessageListAPIView(APIView):
    serializer_class = ChatMessageSerializer
    permission_classes = (IsAuthenticated,)

    @chat_message_list_schema
    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)

        if room.customer != request.user and room.provider != request.user:
            return Response(
                {
                    "success": False,
                    "message": "You do not have access to this chat room.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = ChatMessage.objects.filter(room=room).order_by("created_at")
        serializer = self.serializer_class(
            queryset, many=True, context={"request": request}
        )
        return Response(
            {
                "success": True,
                "message": "Messages fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class MarkMessageReadAPIView(APIView):
    serializer_class = ChatMessageSerializer
    permission_classes = (IsAuthenticated,)

    @mark_message_read_schema
    def patch(self, request, pk):
        message = get_object_or_404(ChatMessage, id=pk)

        if message.sender == request.user:
            return Response(
                {
                    "success": False,
                    "message": "You cannot mark your own message as read.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        room = message.room
        if request.user != room.customer and request.user != room.provider:
            return Response(
                {
                    "success": False,
                    "message": "You do not have access to this message.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        message.is_read = True
        message.save()

        serializer = ChatMessageSerializer(
            message, context={"request": request}
        )
        return Response(
            {
                "success": True,
                "message": "Message marked as read.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
