"""User URL configuration."""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.user import views

urlpatterns = [
    # Auth
    path("auth/register/", views.RegisterAPIView.as_view(), name="register"),
    path("auth/verify-email/", views.EmailVerificationAPIView.as_view(), name="email-verify"),
    path("auth/login/", views.EmailLoginAPIView.as_view(), name="login"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # Profile
    path("auth/profile/", views.ProfileAPIView.as_view(), name="profile"),
    path("auth/profile/update/", views.ProfileUpdateAPIView.as_view(), name="profile-update"),
    # Password
    path("auth/password/change/", views.PasswordChangeAPIView.as_view(), name="password-change"),
    path("auth/password/forgot/", views.PasswordResetRequestAPIView.as_view(), name="password-forgot"),
    path("auth/password/verify-otp/", views.PasswordOTPVerifyAPIView.as_view(), name="password-verify-otp"),
    path("auth/password/reset/", views.PasswordResetConfirmAPIView.as_view(), name="password-reset"),
]
