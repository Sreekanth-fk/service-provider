from rest_framework import serializers

from .models import ChatRoom, ChatMessage


class ChatRoomSerializer(serializers.ModelSerializer):
    booking_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = (
            "id",
            "booking_id",
            "customer",
            "provider",
            "created_at",
        )
        read_only_fields = (
            "id",
            "customer",
            "provider",
            "created_at",
        )


class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(
        source="sender.username", read_only=True
    )
    sender_role = serializers.CharField(
        source="sender.role", read_only=True
    )

    class Meta:
        model = ChatMessage
        fields = (
            "id",
            "room",
            "sender",
            "sender_name",
            "sender_role",
            "message",
            "is_read",
            "created_at",
        )
        read_only_fields = (
            "id",
            "sender",
            "is_read",
            "created_at",
        )


class MarkReadSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        instance.is_read = True
        instance.save()
        return instance
