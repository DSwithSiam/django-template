"""Read/query logic for the users app.

Selectors contain functions that fetch and shape data. Keep all read queries
here so they are reusable and easy to test in isolation.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model

User = get_user_model()


def get_user_by_email(email: str):
    """Return the user matching ``email`` or ``None``."""
    return User.objects.filter(email=email).first()


def active_users():
    """Return a queryset of active users."""
    return User.objects.filter(is_active=True)
