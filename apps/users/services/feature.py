"""Write/business logic ("services") for the users app.

Services encapsulate write operations and side effects (creating records,
sending emails, orchestrating multiple models) so that views and serializers
stay thin. Read/query logic belongs in ``selectors.py``.
"""
from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


@transaction.atomic
def create_user(*, email: str, password: str, **extra_fields) -> "User":
    """Create and return a new (inactive) user."""
    user = User(email=email, is_active=False, **extra_fields)
    user.set_new_username()
    user.set_password(password)
    user.save()
    return user
