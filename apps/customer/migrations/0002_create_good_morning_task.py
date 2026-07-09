from django.db import migrations


def create_good_morning_periodic_task(apps, schema_editor):
    CrontabSchedule = apps.get_model("django_celery_beat", "CrontabSchedule")
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    ContentType = apps.get_model("contenttypes", "ContentType")

    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute="30",
        hour="10",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
        timezone="UTC",
    )

    PeriodicTask.objects.get_or_create(
        name="send-good-morning-emails",
        defaults={
            "task": "apps.customer.tasks.send_good_morning_emails",
            "crontab": schedule,
            "enabled": True,
            "description": "Sends Good Morning email to all active customers daily at 10:30 AM",
        },
    )


def remove_good_morning_periodic_task(apps, schema_editor):
    PeriodicTask = apps.get_model("django_celery_beat", "PeriodicTask")
    PeriodicTask.objects.filter(name="send-good-morning-emails").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("customer", "0001_initial"),
        ("django_celery_beat", "0019_alter_periodictasks_options"),
    ]

    operations = [
        migrations.RunPython(
            create_good_morning_periodic_task,
            remove_good_morning_periodic_task,
        ),
    ]
