"""
User views — thin controllers that delegate to services.

No business logic here. Views handle:
    1. Parse request
    2. Validate via serializer
    3. Call service
    4. Return response
"""

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # noqa: F401

from apps.core.responses import success_response
from apps.core.throttles import AuthLoginThrottle
from apps.user import serializers as user_serializers
from apps.user import services as user_services


# ---------------------------------------------------------------------------
# Registration & verification
# ---------------------------------------------------------------------------
class RegisterAPIView(generics.GenericAPIView):
    """Register a new user account."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthLoginThrottle]
    serializer_class = user_serializers.RegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_services.register_user(serializer.validated_data, request=request)
        return success_response(
            details="Registration successful. Verification email sent.",
            code="REGISTER_SUCCESS",
            status_code=status.HTTP_201_CREATED,
        )


class EmailVerificationAPIView(generics.GenericAPIView):
    """Verify user email via token link."""

    permission_classes = [AllowAny]
    serializer_class = user_serializers.EmailVerificationSerializer

    def _verify(self, data):
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        tokens = user_services.verify_email(
            uid=serializer.validated_data["uid"],
            token=serializer.validated_data["token"],
        )
        return success_response(
            details="Email verified successfully.",
            code="EMAIL_VERIFIED",
            data=tokens,
        )

    def get(self, request):
        return self._verify(
            {
                "uid": request.query_params.get("uid"),
                "token": request.query_params.get("token"),
            }
        )

    def post(self, request):
        return self._verify(request.data)


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------
class EmailLoginAPIView(TokenObtainPairView):
    """Login via email and password. Returns JWT tokens + user profile."""

    throttle_classes = [AuthLoginThrottle]
    serializer_class = user_serializers.EmailLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return success_response(
            details="Login successful.",
            code="LOGIN_SUCCESS",
            data={
                "refresh": serializer.validated_data["refresh"],
                "access": serializer.validated_data["access"],
                "user": serializer.validated_data["user"],
            },
        )


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------
class ProfileAPIView(generics.RetrieveAPIView):
    """Get the authenticated user's profile."""

    permission_classes = [IsAuthenticated]
    serializer_class = user_serializers.UserProfileSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response(
            details="Profile retrieved.",
            code="PROFILE_SUCCESS",
            data=serializer.data,
        )


class ProfileUpdateAPIView(generics.UpdateAPIView):
    """Update the authenticated user's profile."""

    permission_classes = [IsAuthenticated]
    serializer_class = user_serializers.ProfileUpdateSerializer
    http_method_names = ["patch"]

    def get_object(self):
        return self.request.user

    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(
            details="Profile updated.",
            code="PROFILE_UPDATED",
            data=serializer.data,
        )


# ---------------------------------------------------------------------------
# Password management
# ---------------------------------------------------------------------------
class PasswordChangeAPIView(generics.GenericAPIView):
    """Change password using current password."""

    permission_classes = [IsAuthenticated]
    serializer_class = user_serializers.PasswordChangeSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_services.change_password(request.user, serializer.validated_data["new_password"])
        return success_response(details="Password changed.", code="PASSWORD_CHANGED")


class PasswordResetRequestAPIView(generics.GenericAPIView):
    """Request a password reset OTP via email."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthLoginThrottle]
    serializer_class = user_serializers.PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_services.request_password_reset(serializer.validated_data["email"])
        return success_response(
            details="If an account exists, an OTP has been sent.",
            code="OTP_SENT",
        )


class PasswordOTPVerifyAPIView(generics.GenericAPIView):
    """Verify a password reset OTP."""

    permission_classes = [AllowAny]
    serializer_class = user_serializers.PasswordOTPVerifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_services.verify_otp(
            email=serializer.validated_data["email"],
            otp=serializer.validated_data["otp"],
        )
        return success_response(details="OTP is valid.", code="OTP_VALID")


class PasswordResetConfirmAPIView(generics.GenericAPIView):
    """Reset password using OTP."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthLoginThrottle]
    serializer_class = user_serializers.PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_services.reset_password(
            email=serializer.validated_data["email"],
            otp=serializer.validated_data["otp"],
            new_password=serializer.validated_data["new_password"],
        )
        return success_response(details="Password reset successfully.", code="PASSWORD_RESET")
