"""Project-wide exceptions and a custom DRF exception handler.

Wire it up in settings if desired:
    REST_FRAMEWORK['EXCEPTION_HANDLER'] = 'common.exceptions.api_exception_handler'
"""
from __future__ import annotations

from rest_framework.views import exception_handler


class ApplicationError(Exception):
    """Base class for domain/business-rule errors raised by services."""

    default_message = 'An application error occurred.'
    default_code = 'APPLICATION_ERROR'

    def __init__(self, message: str | None = None, code: str | None = None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        super().__init__(self.message)


class NotFoundError(ApplicationError):
    default_message = 'Resource not found.'
    default_code = 'NOT_FOUND'


class PermissionDeniedError(ApplicationError):
    default_message = 'You do not have permission to perform this action.'
    default_code = 'PERMISSION_DENIED'


def api_exception_handler(exc, context):
    """Return DRF responses in the project's ``{success, details, code}`` shape."""
    response = exception_handler(exc, context)
    if response is not None:
        detail = response.data.get('detail') if isinstance(response.data, dict) else response.data
        response.data = {
            'success': False,
            'details': detail or response.data,
            'code': getattr(exc, 'default_code', 'ERROR'),
            'status_code': response.status_code,
        }
    return response
