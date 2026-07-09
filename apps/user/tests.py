from django.test import TestCase
from django.contrib.auth import get_user_model
import datetime
import pytz
from service_core.helpers.timezone import (
    localize_datetime,
    localize_datetime_format,
    convert_user_time_to_utc,
    timezone_offset,
)

User = get_user_model()


class MockRequest:
    def __init__(self, user):
        self.user = user


class TimezoneLocalizationTests(TestCase):
    def setUp(self):
        self.user_india = User.objects.create_user(
            username="india_user",
            email="india@example.com",
            password="password123",
            timezone="Asia/Kolkata"
        )
        self.user_ny = User.objects.create_user(
            username="ny_user",
            email="ny@example.com",
            password="password123",
            timezone="America/New_York"
        )
        self.user_utc = User.objects.create_user(
            username="utc_user",
            email="utc@example.com",
            password="password123",
            timezone="UTC"
        )

    def test_timezone_offset(self):
        self.assertIn("Asia/Kolkata", timezone_offset("Asia/Kolkata"))
        self.assertIn("UTC+0530", timezone_offset("Asia/Kolkata"))
        self.assertIn("America/New_York", timezone_offset("America/New_York"))
        # Invalid timezone should default gracefully
        self.assertIn("UTC+0000", timezone_offset("Invalid/Timezone"))

    def test_localize_datetime(self):
        # 10:00 UTC
        utc_dt = datetime.datetime(2026, 7, 8, 10, 0, tzinfo=pytz.utc)

        request_india = MockRequest(self.user_india)
        request_ny = MockRequest(self.user_ny)
        request_utc = MockRequest(self.user_utc)

        # India time should be 15:30 (10:00 + 5:30)
        local_india = localize_datetime(utc_dt, request_india)
        self.assertEqual(local_india.hour, 15)
        self.assertEqual(local_india.minute, 30)

        # NY time (EDT in July is UTC-4) should be 06:00 (10:00 - 4:00)
        local_ny = localize_datetime(utc_dt, request_ny)
        self.assertEqual(local_ny.hour, 6)
        self.assertEqual(local_ny.minute, 0)

        # UTC should remain UTC
        local_utc = localize_datetime(utc_dt, request_utc)
        self.assertEqual(local_utc.hour, 10)
        self.assertEqual(local_utc.minute, 0)

    def test_localize_datetime_format(self):
        utc_dt = datetime.datetime(2026, 7, 8, 10, 0, tzinfo=pytz.utc)
        request_india = MockRequest(self.user_india)

        formatted = localize_datetime_format(utc_dt, request_india, "%d-%m-%Y %I:%M %p")
        self.assertEqual(formatted, "08-07-2026 03:30 PM")

    def test_convert_user_time_to_utc(self):
        # A naive datetime representing user's local time (e.g. 15:30)
        naive_dt = datetime.datetime(2026, 7, 8, 15, 30)
        request_india = MockRequest(self.user_india)

        # India time 15:30 should convert back to 10:00 UTC
        utc_dt = convert_user_time_to_utc(naive_dt, request_india)
        self.assertEqual(utc_dt.hour, 10)
        self.assertEqual(utc_dt.minute, 0)
        self.assertEqual(utc_dt.tzinfo, pytz.utc)
