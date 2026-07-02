import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_faq_list_is_public():
    client = APIClient()
    response = client.get('/api/v1/faqs/')
    assert response.status_code == 200
