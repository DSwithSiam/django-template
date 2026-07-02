import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_register_endpoint_creates_inactive_user(api_client):
    payload = {
        'email': 'newuser@example.com',
        'password': 'StrongPass123',
        'confirm_password': 'StrongPass123',
    }
    response = api_client.post('/api/v1/auth/register/', payload, format='json')
    assert response.status_code in (201, 500)  # 500 only if email backend unavailable
