"""Read/query logic for the contact app."""
from __future__ import annotations

from apps.contact.models import FAQ, ContactUs


def list_faqs():
    """Return FAQs in display order."""
    return FAQ.objects.all()


def unreplied_messages():
    """Return contact messages that still need a reply."""
    return ContactUs.objects.filter(is_replied=False)
