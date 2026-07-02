"""Stripe integration boundary.

Wraps the Stripe SDK so the rest of the codebase never imports ``stripe``
directly. Install the SDK (``pip install stripe``) before using in production.
"""
from __future__ import annotations

from django.conf import settings


class StripeClient:
    def __init__(self, api_key: str | None = None, webhook_secret: str | None = None):
        self.api_key = api_key or settings.STRIPE_SECRET_KEY
        self.webhook_secret = webhook_secret or settings.STRIPE_WEBHOOK_SECRET

    def _sdk(self):
        try:
            import stripe  # noqa: WPS433 (import at call site is intentional)
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "The 'stripe' package is not installed. Run: pip install stripe"
            ) from exc
        stripe.api_key = self.api_key
        return stripe

    def create_checkout_session(self, **kwargs):
        return self._sdk().checkout.Session.create(**kwargs)

    def construct_event(self, payload: bytes, sig_header: str):
        return self._sdk().Webhook.construct_event(
            payload, sig_header, self.webhook_secret
        )


def get_stripe_client() -> StripeClient:
    return StripeClient()
