"""File/object storage helpers.

Today this defers to Django's configured ``default_storage`` (local media in
dev). Swap the implementation here to move to S3/GCS without touching apps.
"""
from __future__ import annotations

from django.core.files.storage import default_storage


def build_media_url(name: str) -> str:
    """Return the public URL for a stored file ``name``."""
    return default_storage.url(name)


def save_file(name: str, content) -> str:
    """Persist ``content`` under ``name`` and return the stored path."""
    return default_storage.save(name, content)
