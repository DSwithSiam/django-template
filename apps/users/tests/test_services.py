import pytest

from apps.users.services.feature import create_user
from apps.users.selectors import get_user_by_email


@pytest.mark.django_db
def test_create_user_persists_inactive_user():
    user = create_user(email='service@example.com', password='StrongPass123')
    assert user.pk is not None
    assert user.is_active is False
    assert get_user_by_email('service@example.com') == user
