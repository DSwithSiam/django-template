"""Tests for contact endpoints."""

from rest_framework import status

from apps.core.test_utils import BaseAPITestCase


class ContactTests(BaseAPITestCase):
    """Test contact form submission."""

    def test_submit_contact_form(self):
        """Public users can submit contact form."""
        response = self.client.post(
            "/api/v1/contact/",
            {
                "full_name": "John Doe",
                "email": "john@example.com",
                "message": "Hello, I have a question.",
            },
        )
        self.assert_success(response, status.HTTP_201_CREATED)

    def test_list_contacts_requires_admin(self):
        """Non-admin users cannot list contact messages."""
        self.authenticate()
        response = self.client.get("/api/v1/contact/list/")
        self.assert_error(response, status.HTTP_403_FORBIDDEN)


class FAQTests(BaseAPITestCase):
    """Test FAQ endpoints."""

    def test_list_faqs_public(self):
        """Anyone can list FAQs."""
        response = self.client.get("/api/v1/faqs/")
        self.assert_success(response)

    def test_create_faq_requires_admin(self):
        """Only admins can create FAQs."""
        self.authenticate()  # Regular user
        response = self.client.post(
            "/api/v1/faqs/",
            {
                "question": "Test?",
                "answer": "Yes.",
            },
        )
        self.assert_error(response, status.HTTP_403_FORBIDDEN)
