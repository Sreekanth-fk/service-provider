import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import ChatRoom, ChatMessage

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        user = await self.authenticate_user()
        if user is None:
            await self.close(code=4001)
            return

        self.scope["user"] = user

        if not await self.validate_room_access():
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON."}))
            return

        message_text = data.get("message", "").strip()
        if not message_text:
            await self.send(
                text_data=json.dumps({"error": "Message cannot be empty."})
            )
            return

        message_data = await self.save_message(message_text)
        if message_data is None:
            await self.send(
                text_data=json.dumps({"error": "Could not save message."})
            )
            return

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "room": int(self.room_id),
                "sender": self.scope["user"].role,
                "message": message_data["message"],
                "created_at": message_data["created_at"],
                "is_read": message_data["is_read"],
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def authenticate_user(self):
        query_string = self.scope.get("query_string", b"").decode()
        token = None
        for param in query_string.split("&"):
            if param.startswith("token="):
                token = param.split("=", 1)[1]
                break

        if token is None:
            return None

        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            return await database_sync_to_async(User.objects.get)(id=user_id)
        except (TokenError, User.DoesNotExist):
            return None

    async def validate_room_access(self):
        try:
            room = await database_sync_to_async(ChatRoom.objects.get)(
                id=self.room_id
            )
        except ChatRoom.DoesNotExist:
            return False

        user = self.scope["user"]
        return room.customer_id == user.id or room.provider_id == user.id

    @database_sync_to_async
    def save_message(self, message_text):
        try:
            room = ChatRoom.objects.get(id=self.room_id)
            message = ChatMessage.objects.create(
                room=room,
                sender=self.scope["user"],
                message=message_text,
            )
            return {
                "message": message.message,
                "created_at": message.created_at.isoformat(),
                "is_read": message.is_read,
            }
        except ChatRoom.DoesNotExist:
            return None
