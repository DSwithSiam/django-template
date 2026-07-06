"""User models."""

import re
import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from apps.common.enums import Status
from apps.common.models import BaseModel
from apps.user.enums import UserRole
from apps.user.managers import UserManager


class User(AbstractUser):
    """
    Custom user model with UUID primary key and email-based auth.

    Extends Django's AbstractUser. Uses email as the primary identifier
    while keeping username for display/URL purposes.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    status = models.SmallIntegerField(choices=Status.choices, default=Status.ACTIVE)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER,
        db_index=True,
    )
    image = models.ImageField(upload_to="profile/", null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, default="")
    address = models.CharField(max_length=500, blank=True, default="")
    last_active_at = models.DateTimeField(default=timezone.now, null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return self.email

    def update_last_active(self) -> None:
        """Update last_active_at without triggering full save."""
        self.last_active_at = timezone.now()
        User.objects.filter(pk=self.pk).update(last_active_at=self.last_active_at)

    def set_unique_username(self) -> None:
        """Generate a unique username from email."""
        email = self.email or ""
        base_name = email.split("@")[0] if "@" in email else email
        base_name = re.sub(r"\d+$", "", base_name) or "user"

        existing = set(
            User.objects.filter(username__regex=rf"^{re.escape(base_name)}\d*$").values_list("username", flat=True)
        )

        if base_name not in existing:
            self.username = base_name
            return

        suffix = 1
        while f"{base_name}{suffix}" in existing:
            suffix += 1
        self.username = f"{base_name}{suffix}"


class PasswordResetOTP(BaseModel):
    """OTP for password reset flow."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_otps")
    otp = models.CharField(max_length=6)
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"OTP for {self.user.email}"

    def is_expired(self) -> bool:
        """Check if OTP has expired (5 minutes)."""
        return timezone.now() > self.created_at + timedelta(minutes=5)
