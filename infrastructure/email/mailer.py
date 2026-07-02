"""Thin wrapper around Django's email backend.

Keeping email delivery here (instead of inside apps) makes it easy to swap the
provider (SMTP, SendGrid, SES, ...) without touching business logic.
"""
from __future__ import annotations

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_html_email(
    *,
    subject: str,
    to: list[str],
    template: str,
    context: dict | None = None,
    from_email: str | None = None,
    fail_silently: bool = False,
) -> int:
    """Render ``template`` with ``context`` and send it as an HTML email."""
    html_message = render_to_string(template, context or {})
    plain_message = strip_tags(html_message)
    return send_mail(
        subject=subject,
        message=plain_message,
        from_email=from_email or settings.EMAIL_HOST_USER,
        recipient_list=to,
        html_message=html_message,
        fail_silently=fail_silently,
    )
