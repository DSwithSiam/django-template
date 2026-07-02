import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_username_is_generated_from_email():
    user = User(email='jane.doe@example.com')
    user.set_new_username()
    assert user.username == 'jane.doe'


@pytest.mark.django_db
def test_superuser_gets_super_admin_role():
    user = User.objects.create_superuser(
        username='root', email='root@example.com', password='pass1234'
    )
    assert user.is_staff is True
    assert user.role == 'SUPER_ADMIN'
