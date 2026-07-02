"""Write/business logic ("services") for the contact app."""
from __future__ import annotations

from apps.contact.models import ContactUs


def create_contact_message(*, full_name: str, email: str, message: str, phone_number: str = "") -> ContactUs:
    """Persist a new contact-us message."""
    return ContactUs.objects.create(
        full_name=full_name,
        email=email,
        phone_number=phone_number,
        message=message,
    )
