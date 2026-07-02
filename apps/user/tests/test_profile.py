"""Tests for user profile."""

from rest_framework import status

from apps.core.test_utils import BaseAPITestCase


class ProfileTests(BaseAPITestCase):
    """Test user profile endpoints."""

    def test_get_profile_authenticated(self):
        """Authenticated user can retrieve profile."""
        user = self.authenticate()
        response = self.client.get("/api/v1/auth/profile/")
        data = self.assert_success(response)
        self.assertEqual(data["data"]["email"], user.email)

    def test_get_profile_unauthenticated(self):
        """Unauthenticated request returns 401."""
        response = self.client.get("/api/v1/auth/profile/")
        self.assert_error(response, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        """Authenticated user can update profile."""
        self.authenticate()
        response = self.client.patch(
            "/api/v1/auth/profile/update/",
            {"first_name": "Updated"},
        )
        data = self.assert_success(response)
        self.assertEqual(data["data"]["first_name"], "Updated")
