"""Example management/data script.

Run with:
    python scripts/seed_data.py

Scripts that need the Django ORM must configure Django first (as below).
"""
import os
import sys
from pathlib import Path

import django

# Make the project root importable and configure Django.
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

User = get_user_model()


def run():
    """Create a default superuser if none exists."""
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin12345",
        )
        print("Created default superuser: admin@example.com / admin12345")
    else:
        print("A superuser already exists; nothing to do.")


if __name__ == "__main__":
    run()
