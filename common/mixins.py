"""Reusable view/serializer mixins."""
from __future__ import annotations

from helpers.response import response


class StandardResponseMixin:
    """Mixin for DRF views that return the project's standard envelope.

    Usage:
        class MyView(StandardResponseMixin, generics.ListAPIView):
            success_detail = 'Items retrieved successfully'
    """

    success_detail = 'Request successful'
    success_code = 'SUCCESS'

    def ok(self, data=None, *, details: str | None = None, status_code: int = 200):
        return response(
            details=details or self.success_detail,
            code=self.success_code,
            status_code=status_code,
            data=data,
        )


class TimeStampedSerializerMixin:
    """Adds read-only ``created_at``/``updated_at`` to a ModelSerializer's fields."""

    class Meta:
        read_only_fields = ('created_at', 'updated_at')
