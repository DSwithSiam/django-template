"""User serializers — data validation only, no business logic."""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.core.serializers import ContextMixin, ExtendedImageField
from apps.user.models import User


# ---------------------------------------------------------------------------
# Profile serializers
# ---------------------------------------------------------------------------
class UserProfileSerializer(serializers.ModelSerializer):
    """Read-only user profile representation."""

    image = ExtendedImageField(required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "role",
            "first_name",
            "last_name",
            "image",
            "phone",
            "address",
            "last_active_at",
            "date_joined",
        )
        read_only_fields = fields


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Update user profile fields."""

    image = ExtendedImageField(required=False)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "image",
            "phone",
            "address",
        )


# ---------------------------------------------------------------------------
# Auth serializers
# ---------------------------------------------------------------------------
class RegisterSerializer(serializers.Serializer):
    """Validate registration input. User creation is in services.py."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs


class EmailLoginSerializer(TokenObtainPairSerializer):
    """Login via email instead of username."""

    username_field = "email"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.EmailField()

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserProfileSerializer(self.user).data
        return data


class EmailVerificationSerializer(serializers.Serializer):
    """Validate email verification token."""

    uid = serializers.CharField()
    token = serializers.CharField()


# ---------------------------------------------------------------------------
# Password serializers
# ---------------------------------------------------------------------------
class PasswordChangeSerializer(serializers.Serializer, ContextMixin):
    """Validate old password change flow."""

    password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    confirm_password = serializers.CharField()

    def validate_password(self, value):
        user = self.get_context_user()
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Validate password reset request."""

    email = serializers.EmailField()


class PasswordOTPVerifySerializer(serializers.Serializer):
    """Validate OTP verification."""

    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Validate password reset with OTP."""

    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate_otp(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs
