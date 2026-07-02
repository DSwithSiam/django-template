import pytest

from apps.contact.services.feature import create_contact_message
from apps.contact.selectors import unreplied_messages


@pytest.mark.django_db
def test_create_contact_message_is_unreplied():
    msg = create_contact_message(
        full_name='Jane Doe', email='jane@example.com', message='Hello there'
    )
    assert msg.is_replied is False
    assert msg in unreplied_messages()
