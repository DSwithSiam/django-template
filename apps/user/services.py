"""
User service layer — all business logic lives here.

Views call these functions; serializers only validate data.
This keeps views thin and business logic testable in isolation.
"""

import logging
import random
from urllib.parse import urlencode

from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.models import PasswordResetOTP, User
from apps.user.tokens import email_verification_token_generator
from config import env as env_module

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
def register_user(validated_data: dict, request=None) -> User:
    """
    Create a new user and trigger verification email.

    Args:
        validated_data: Validated data from RegisterSerializer
        request: The HTTP request (for building absolute URLs)

    Returns:
        The created User instance

    Raises:
        ValidationError: If username generation fails after retries
    """
    email = validated_data["email"]
    password = validated_data["password"]

    with transaction.atomic():
        user = User(email=email, is_active=False, is_staff=False)
        user.set_unique_username()
        user.set_password(password)

        for attempt in range(5):
            try:
                user.save()
                break
            except IntegrityError as exc:
                if "username" not in str(exc).lower() or attempt == 4:
                    raise ValidationError("Unable to create account. Please try again.") from exc
                user.set_unique_username()

    # Send verification email asynchronously
    _send_verification_email_async(user, request)

    return user


def _send_verification_email_async(user: User, request=None) -> None:
    """Send verification email via Celery if available, else synchronously."""
    verification_link = _build_verification_link(user, request)
    try:
        from apps.user.tasks import send_verification_email_task

        send_verification_email_task.delay(str(user.pk), verification_link)
    except Exception:
        logger.warning("Celery unavailable, sending email synchronously.")
        from apps.user.tasks import _send_verification_email

        _send_verification_email(str(user.pk), verification_link)


def _build_verification_link(user: User, request=None) -> str:
    """Build the email verification URL."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token_generator.make_token(user)
    verify_path = reverse("email-verify")
    query = urlencode({"uid": uid, "token": token})

    if request is not None:
        return request.build_absolute_uri(f"{verify_path}?{query}")

    base_url = (env_module.SWAGGER_DEFAULT_API_URL or "").rstrip("/")
    return f"{base_url}{verify_path}?{query}" if base_url else f"{verify_path}?{query}"


# ---------------------------------------------------------------------------
# Email verification
# ---------------------------------------------------------------------------
def verify_email(uid: str, token: str) -> dict:
    """
    Verify a user's email and activate their account.

    Returns:
        Dict with access/refresh tokens and user data
    """
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as exc:
        raise ValidationError("Invalid verification link.") from exc

    if user.is_active:
        raise ValidationError("Account is already verified. Please log in.")

    if not email_verification_token_generator.check_token(user, token):
        raise ValidationError("Verification link is invalid or has expired.")

    user.is_active = True
    user.save(update_fields=["is_active"])

    # Send welcome email asynchronously
    try:
        from apps.user.tasks import send_welcome_email_task

        send_welcome_email_task.delay(str(user.pk))
    except Exception:
        logger.warning("Could not queue welcome email for user %s", user.pk)

    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


# ---------------------------------------------------------------------------
# Password management
# ---------------------------------------------------------------------------
def change_password(user: User, new_password: str) -> None:
    """Change a user's password."""
    user.set_password(new_password)
    user.save(update_fields=["password"])


def request_password_reset(email: str) -> None:
    """
    Generate OTP and send password reset email.

    Silently succeeds even if email doesn't exist (security best practice).
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return  # Don't reveal whether email exists

    # Invalidate previous OTPs
    PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)

    otp = str(random.randint(100000, 999999))
    PasswordResetOTP.objects.create(user=user, otp=otp)

    # Send OTP email asynchronously
    try:
        from apps.user.tasks import send_password_reset_otp_task

        send_password_reset_otp_task.delay(str(user.pk), otp)
    except Exception:
        logger.warning("Celery unavailable, sending OTP email synchronously.")
        from apps.user.tasks import _send_password_reset_otp

        _send_password_reset_otp(str(user.pk), otp)


def verify_otp(email: str, otp: str) -> bool:
    """Verify that an OTP is valid."""
    user = _get_user_by_email(email)

    otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp, is_used=False).order_by("-created_at").first()

    if not otp_obj:
        raise ValidationError("Invalid OTP.")

    if otp_obj.is_expired():
        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])
        raise ValidationError("OTP has expired.")

    return True


def reset_password(email: str, otp: str, new_password: str) -> User:
    """Reset password using OTP."""
    user = _get_user_by_email(email)

    otp_obj = PasswordResetOTP.objects.filter(user=user, otp=otp, is_used=False).order_by("-created_at").first()

    if not otp_obj:
        raise ValidationError("Invalid or already used OTP.")

    if otp_obj.is_expired():
        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])
        raise ValidationError("OTP has expired. Please request a new one.")

    user.set_password(new_password)
    user.save(update_fields=["password"])
    otp_obj.is_used = True
    otp_obj.save(update_fields=["is_used"])

    return user


def _get_user_by_email(email: str) -> User:
    """Get user by email or raise NotFound."""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist as exc:
        raise NotFound("User not found.") from exc
