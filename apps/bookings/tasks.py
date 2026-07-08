from celery import shared_task


@shared_task
def booking_notification(customer_name, provider_name, service_name):
    print("=" * 50)
    print("NEW BOOKING RECEIVED")
    print(f"Customer : {customer_name}")
    print(f"Provider : {provider_name}")
    print(f"Service  : {service_name}")
    print("=" * 50)

    return "Booking Notification Sent"