from django.contrib.auth import get_user_model
from django.test import TestCase, TransactionTestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.bookings.models import Booking
from apps.provider.models import Provider
from apps.services.models import Service

from .models import ChatRoom, ChatMessage

User = get_user_model()


class ChatModelTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="customer1",
            email="customer1@test.com",
            password="testpass123",
            role="customer",
        )
        self.provider_user = User.objects.create_user(
            username="provider1",
            email="provider1@test.com",
            password="testpass123",
            role="provider",
        )
        self.service = Service.objects.create(name="Test Service")
        self.provider = Provider.objects.create(
            user=self.provider_user,
            phone="+1234567890",
            service=self.service,
        )
        self.booking = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service=self.service,
            date="2026-07-15",
            start_time="10:00:00",
            end_time="11:00:00",
        )

    def test_chat_room_created_on_booking(self):
        room = ChatRoom.objects.filter(booking=self.booking).first()
        self.assertIsNotNone(room)
        self.assertEqual(room.customer, self.customer)
        self.assertEqual(room.provider, self.provider_user)

    def test_chat_message_creation(self):
        room = ChatRoom.objects.get(booking=self.booking)
        message = ChatMessage.objects.create(
            room=room,
            sender=self.customer,
            message="Hello, when will you arrive?",
        )
        self.assertEqual(message.room, room)
        self.assertEqual(message.sender, self.customer)
        self.assertEqual(message.message, "Hello, when will you arrive?")
        self.assertFalse(message.is_read)

    def test_chat_room_str(self):
        room = ChatRoom.objects.get(booking=self.booking)
        self.assertIn(str(self.booking.id), str(room))

    def test_chat_message_str(self):
        room = ChatRoom.objects.get(booking=self.booking)
        message = ChatMessage.objects.create(
            room=room,
            sender=self.customer,
            message="Test message",
        )
        self.assertIn(str(message.sender), str(message))
        self.assertIn(str(message.room_id), str(message))


class ChatAPITests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="customer1",
            email="customer1@test.com",
            password="testpass123",
            role="customer",
        )
        self.provider_user = User.objects.create_user(
            username="provider1",
            email="provider1@test.com",
            password="testpass123",
            role="provider",
        )
        self.other_user = User.objects.create_user(
            username="other",
            email="other@test.com",
            password="testpass123",
            role="customer",
        )
        self.service = Service.objects.create(name="Test Service")
        self.provider = Provider.objects.create(
            user=self.provider_user,
            phone="+1234567890",
            service=self.service,
        )
        self.booking = Booking.objects.create(
            customer=self.customer,
            provider=self.provider,
            service=self.service,
            date="2026-07-15",
            start_time="10:00:00",
            end_time="11:00:00",
        )
        self.room = ChatRoom.objects.get(booking=self.booking)

        self.customer_client = APIClient()
        refresh = RefreshToken.for_user(self.customer)
        self.customer_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        self.provider_client = APIClient()
        refresh = RefreshToken.for_user(self.provider_user)
        self.provider_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        self.other_client = APIClient()
        refresh = RefreshToken.for_user(self.other_user)
        self.other_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    def test_chat_room_list_customer(self):
        response = self.customer_client.get("/api/chat/rooms/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)

    def test_chat_room_list_provider(self):
        response = self.provider_client.get("/api/chat/rooms/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)

    def test_chat_room_list_unauthorized(self):
        client = APIClient()
        response = client.get("/api/chat/rooms/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_chat_messages_customer(self):
        ChatMessage.objects.create(
            room=self.room,
            sender=self.customer,
            message="Hello!",
        )
        response = self.customer_client.get(
            f"/api/chat/rooms/{self.room.id}/messages/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(len(response.data["data"]), 1)
        self.assertEqual(response.data["data"][0]["message"], "Hello!")

    def test_chat_messages_unauthorized_user(self):
        response = self.other_client.get(
            f"/api/chat/rooms/{self.room.id}/messages/"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_message_read(self):
        message = ChatMessage.objects.create(
            room=self.room,
            sender=self.provider_user,
            message="I'll reach in 20 minutes.",
        )
        response = self.customer_client.patch(
            f"/api/chat/messages/{message.id}/read/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        message.refresh_from_db()
        self.assertTrue(message.is_read)

    def test_mark_own_message_read(self):
        message = ChatMessage.objects.create(
            room=self.room,
            sender=self.customer,
            message="Hello!",
        )
        response = self.customer_client.patch(
            f"/api/chat/messages/{message.id}/read/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_mark_message_read_unauthorized(self):
        message = ChatMessage.objects.create(
            room=self.room,
            sender=self.provider_user,
            message="Secret message",
        )
        response = self.other_client.patch(
            f"/api/chat/messages/{message.id}/read/"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ChatRoomSignalTests(TestCase):
    def test_chat_room_auto_created_on_booking(self):
        customer = User.objects.create_user(
            username="sig_cust",
            email="sig_cust@test.com",
            password="testpass123",
            role="customer",
        )
        prov_user = User.objects.create_user(
            username="sig_prov",
            email="sig_prov@test.com",
            password="testpass123",
            role="provider",
        )
        service = Service.objects.create(name="Signal Test Service")
        provider = Provider.objects.create(
            user=prov_user,
            phone="+1234567890",
            service=service,
        )
        booking = Booking.objects.create(
            customer=customer,
            provider=provider,
            service=service,
            date="2026-07-20",
            start_time="14:00:00",
            end_time="15:00:00",
        )

        room = ChatRoom.objects.filter(booking=booking).first()
        self.assertIsNotNone(room)
        self.assertEqual(room.customer, customer)
        self.assertEqual(room.provider, prov_user)
