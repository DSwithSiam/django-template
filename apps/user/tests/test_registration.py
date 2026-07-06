"""Tests for user registration."""

from django.test import override_settings
from rest_framework import status

from apps.core.test_utils import BaseAPITestCase


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class RegistrationTests(BaseAPITestCase):
    """Test user registration flow."""

    url = "/api/v1/auth/register/"

    def test_register_success(self):
        """Successful registration returns 201."""
        response = self.client.post(
            self.url,
            {
                "email": "new@example.com",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
            },
        )
        self.assert_success(response, status.HTTP_201_CREATED)

    def test_register_duplicate_email(self):
        """Duplicate email returns 400."""
        self.create_user(email="existing@example.com")
        response = self.client.post(
            self.url,
            {
                "email": "existing@example.com",
                "password": "StrongPass123!",
                "confirm_password": "StrongPass123!",
            },
        )
        self.assert_error(response, status.HTTP_400_BAD_REQUEST)

    def test_register_password_mismatch(self):
        """Mismatched passwords return 400."""
        response = self.client.post(
            self.url,
            {
                "email": "new@example.com",
                "password": "StrongPass123!",
                "confirm_password": "DifferentPass456!",
            },
        )
        self.assert_error(response, status.HTTP_400_BAD_REQUEST)

    def test_register_weak_password(self):
        """Weak password returns 400."""
        response = self.client.post(
            self.url,
            {
                "email": "new@example.com",
                "password": "123",
                "confirm_password": "123",
            },
        )
        self.assert_error(response, status.HTTP_400_BAD_REQUEST)
