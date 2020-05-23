
import pytz
from django.utils import timezone
from datetime import datetime, timedelta


class TIMEZONE_CODES():
    INDIA = 'Asia/Kolkata'
    MALAYSIA = 'Asia/Kuala_Lumpur'


def local_current_datetime_from_active_tz():
    return timezone.localtime(timezone.now())


def fifteen_minutes_later():
    return local_current_datetime_from_active_tz() + timezone.timedelta(minutes=15)

