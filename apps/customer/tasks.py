import logging
import datetime
import pytz

from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_celery_beat.models import PeriodicTask

from apps.customer.models import Customer, EmailLog
from service_core.mail_functions import SendEmails

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def send_good_morning_emails():
    """
    Minutely Celery Beat task.
    1. Reads the 'send-good-morning-emails' task configuration to check if it's enabled and get the scheduled send_time (crontab).
    2. Identifies which customer timezones currently match that configured time.
    3. Fetches active customers in those timezones.
    4. Performs bulk lookup of already sent emails today to prevent duplicates.
    5. Sends a "Good Morning" email to customers who haven't received it yet.
    """
    try:
        config_task = PeriodicTask.objects.get(name="send-good-morning-emails")
    except PeriodicTask.DoesNotExist:
        logger.error("Configuration task 'send-good-morning-emails' does not exist in the database.")
        return {"error": "Configuration task not found"}

    if not config_task.enabled:
        logger.info("Good Morning email sending is disabled.")
        return {"status": "disabled"}

    crontab_schedule = config_task.crontab
    if not crontab_schedule:
        logger.error("Configuration task 'send-good-morning-emails' has no crontab schedule.")
        return {"error": "Crontab schedule not set"}

    try:
        target_hour = int(crontab_schedule.hour)
        target_minute = int(crontab_schedule.minute)
    except ValueError:
        logger.error(
            "Invalid crontab hour/minute format in config task: hour=%s, minute=%s",
            crontab_schedule.hour,
            crontab_schedule.minute
        )
        return {"error": "Invalid crontab format"}

    utc_now = timezone.now()

    # Step 1: Find active timezones in the system
    active_timezones = User.objects.filter(
        is_active=True, role=User.Role.CUSTOMER
    ).values_list("timezone", flat=True).distinct()

    # Step 2: Determine which timezones are currently at the target hour and minute
    matching_timezones = []
    for tz_name in active_timezones:
        calc_tz_name = tz_name
        if not calc_tz_name or calc_tz_name not in pytz.all_timezones_set:
            calc_tz_name = "UTC"

        try:
            tz = pytz.timezone(calc_tz_name)
            local_time = utc_now.astimezone(tz)
            if local_time.hour == target_hour and local_time.minute == target_minute:
                matching_timezones.append(tz_name)
        except Exception as e:
            logger.warning("Error checking timezone match for %s: %s", tz_name, e)

    if not matching_timezones:
        logger.info("No timezones currently match the target send time %02d:%02d.", target_hour, target_minute)
        return {
            "status": "success",
            "message": "No matching timezones at this minute",
            "sent_count": 0
        }

    # Step 3: Query customers in the matching timezones
    customers = Customer.objects.filter(
        user__is_active=True,
        user__timezone__in=matching_timezones
    ).select_related("user")

    if not customers.exists():
        logger.info("No active customers found in matching timezones: %s", matching_timezones)
        return {
            "status": "success",
            "message": "No customers in matching timezones",
            "sent_count": 0
        }

    # Step 4: Fetch existing logs in bulk to prevent duplicates
    customer_ids = [c.id for c in customers]

    # Pre-calculate possible dates (local dates could be yesterday, today, or tomorrow relative to UTC date)
    possible_dates = [
        utc_now.date() - datetime.timedelta(days=1),
        utc_now.date(),
        utc_now.date() + datetime.timedelta(days=1),
    ]

    existing_logs = EmailLog.objects.filter(
        customer_id__in=customer_ids,
        email_type="good_morning",
        sent_date__in=possible_dates
    ).values_list("customer_id", "sent_date")

    existing_log_set = set(existing_logs)  # Set of (customer_id, sent_date)

    mail_service = SendEmails()
    email_host = settings.DEFAULT_FROM_EMAIL
    template_name = "emails/good_morning.html"
    subject = "Good Morning from Service Provider"

    successful = 0
    failed = 0
    skipped = 0
    failed_emails = []

    # Step 5: Process and send emails
    for customer in customers:
        user_email = customer.user.email
        if not user_email or not user_email.strip():
            logger.warning("Skipping customer %s — email is empty", customer.id)
            continue

        # Get local date for this customer to check duplicates
        cust_tz_name = customer.user.timezone
        if not cust_tz_name or cust_tz_name not in pytz.all_timezones_set:
            cust_tz_name = "UTC"

        try:
            cust_tz = pytz.timezone(cust_tz_name)
            cust_local_time = utc_now.astimezone(cust_tz)
            cust_local_date = cust_local_time.date()
        except Exception as e:
            logger.error("Failed to compute local date for customer %s with timezone %s: %s", customer.id, cust_tz_name, e)
            cust_local_date = utc_now.date()

        # Check duplicate
        if (customer.id, cust_local_date) in existing_log_set:
            logger.info("Good Morning email already sent today to %s (%s)", user_email, cust_local_date)
            skipped += 1
            continue

        context = {
            "customer_name": customer.user.username,
            "current_date": cust_local_date.strftime("%B %d, %Y"),
        }

        try:
            result = mail_service.sendTemplateEmail(
                subject=subject,
                context=context,
                template=template_name,
                email_host=email_host,
                user_email=user_email,
            )

            if result is None:
                # Successfully sent, log it to DB
                try:
                    EmailLog.objects.create(
                        customer=customer,
                        email_type="good_morning",
                        sent_date=cust_local_date
                    )
                    successful += 1
                    logger.info("Good Morning email successfully sent to %s", user_email)
                except Exception as db_err:
                    # IntegrityError could happen if processed concurrently
                    logger.warning("Failed to save EmailLog for %s (possibly sent concurrently): %s", user_email, db_err)
                    successful += 1  # Still successful from mail delivery standpoint
            else:
                failed += 1
                failed_emails.append(user_email)
                logger.error("Failed to send email to %s: %s", user_email, result)

        except Exception as exc:
            failed += 1
            failed_emails.append(user_email)
            logger.error("Unexpected error sending to %s: %s", user_email, exc)

    logger.info(
        "Good Morning task finished — Successful: %s, Skipped: %s, Failed: %s",
        successful,
        skipped,
        failed,
    )

    return {
        "successful": successful,
        "skipped": skipped,
        "failed": failed,
        "failed_emails": failed_emails,
    }
