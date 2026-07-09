import datetime
import pytz
from django.utils import timezone
from rest_framework import serializers

def get_user_timezone(request=None, timezone_name=None):
    """
    Get the target timezone name.
    If timezone_name is provided and valid, returns it.
    If request is provided, gets the authenticated user's timezone.
    Returns 'UTC' if user is not authenticated or has an invalid timezone.
    """
    if timezone_name and timezone_name in pytz.all_timezones_set:
        return timezone_name

    if not request or not request.user or not request.user.is_authenticated:
        return 'UTC'
    tz_name = getattr(request.user, 'timezone', 'UTC')
    if not tz_name or tz_name not in pytz.all_timezones_set:
        return 'UTC'
    return tz_name

def localize_datetime(value, request=None, timezone_name=None):
    """
    Convert a UTC datetime into the target timezone (via request or timezone_name).
    Returns UTC or value itself if timezone is unavailable/invalid.
    """
    if value is None:
        return None

    if isinstance(value, str):
        from django.utils.dateparse import parse_datetime
        parsed = parse_datetime(value)
        if parsed is None:
            return value
        value = parsed

    if not isinstance(value, datetime.datetime):
        return value

    tz_name = get_user_timezone(request, timezone_name)
    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.utc

    if timezone.is_naive(value):
        value = timezone.make_aware(value, pytz.utc)

    return value.astimezone(tz)

def localize_datetime_format(value, request=None, format_str=None, timezone_name=None):
    """
    Convert a UTC datetime into the target timezone and format it as a string.
    """
    localized = localize_datetime(value, request, timezone_name)
    if localized is None:
        return None
    if isinstance(localized, datetime.datetime):
        try:
            return localized.strftime(format_str)
        except Exception:
            return localized.isoformat()
    return str(localized)

def convert_user_time_to_utc(value, request=None, timezone_name=None):
    """
    Convert a user's local datetime back to UTC.
    If the value is timezone-aware, convert it directly to UTC.
    If it is timezone-naive, assume it's in the target timezone and localize it, then convert to UTC.
    """
    if value is None:
        return None

    if isinstance(value, str):
        from django.utils.dateparse import parse_datetime
        parsed = parse_datetime(value)
        if parsed is None:
            return value
        value = parsed

    if not isinstance(value, datetime.datetime):
        return value

    if timezone.is_aware(value):
        return value.astimezone(pytz.utc)

    tz_name = get_user_timezone(request, timezone_name)
    try:
        tz = pytz.timezone(tz_name)
        localized = tz.localize(value)
        return localized.astimezone(pytz.utc)
    except Exception:
        return timezone.make_aware(value, pytz.utc)

def timezone_offset(timezone_name):
    """
    Return a formatted timezone offset string, e.g., 'UTC+0530 - Asia/Kolkata'.
    """
    try:
        tz = pytz.timezone(timezone_name)
        now = datetime.datetime.now(tz)
        offset = now.utcoffset()
        total_seconds = int(offset.total_seconds())
        sign = "+" if total_seconds >= 0 else "-"
        total_seconds = abs(total_seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        offset_str = f"UTC{sign}{hours:02d}{minutes:02d}"
        return f"{offset_str} - {timezone_name}"
    except Exception:
        return f"UTC+0000 - {timezone_name}"

class LocalizedDateTimeField(serializers.DateTimeField):
    """
    Serializer field that outputs datetimes localized to the user's timezone,
    and parses incoming datetimes to store them in UTC.
    """
    def to_representation(self, value):
        if value is None:
            return None

        request = self.context.get('request')
        try:
            localized = localize_datetime(value, request)
        except Exception:
            localized = value

        if not isinstance(localized, datetime.datetime):
            return super().to_representation(value)

        if self.format is None:
            return localized.isoformat()

        try:
            return localized.strftime(self.format)
        except Exception:
            return localized.isoformat()

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if value is not None:
            request = self.context.get('request')
            value = convert_user_time_to_utc(value, request)
        return value

class LocalizedDateField(serializers.DateField):
    """
    Serializer field that output dates converted/formatted according to the user's timezone.
    """
    def to_representation(self, value):
        if value is None:
            return None

        request = self.context.get('request')
        if isinstance(value, datetime.datetime):
            try:
                localized = localize_datetime(value, request)
                value = localized.date()
            except Exception:
                pass
        elif isinstance(value, datetime.date):
            # A pure date does not have time or timezone context.
            pass

        return super().to_representation(value)
