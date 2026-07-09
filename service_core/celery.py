import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "service_core.settings")

app = Celery("service_core")

app.config_from_object(
    "django.conf:settings",
    namespace="CELERY",
)

app.autodiscover_tasks()

CELERY_BEAT_SCHEDULE = {
    "send-good-morning-emails": {
        "task": "apps.customer.tasks.send_good_morning_emails",
        "schedule": crontab(minute="*"),
    },
}   