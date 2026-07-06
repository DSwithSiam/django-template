# Authentication

## Overview

This template uses **JWT (JSON Web Token)** authentication via `djangorestframework-simplejwt`.

- **Access Token**: Valid for 1 day
- **Refresh Token**: Valid for 7 days
- **Login**: Via email + password

## Auth Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register/` | Register new user | No |
| GET/POST | `/api/v1/auth/verify-email/` | Verify email | No |
| POST | `/api/v1/auth/login/` | Login (email) | No |
| POST | `/api/v1/auth/token/refresh/` | Refresh JWT token | No |
| GET | `/api/v1/auth/profile/` | Get profile | Yes |
| PATCH | `/api/v1/auth/profile/update/` | Update profile | Yes |
| POST | `/api/v1/auth/password/change/` | Change password | Yes |
| POST | `/api/v1/auth/password/forgot/` | Request OTP | No |
| POST | `/api/v1/auth/password/verify-otp/` | Verify OTP | No |
| POST | `/api/v1/auth/password/reset/` | Reset with OTP | No |

## Registration Flow

1. User submits email + password → `POST /api/v1/auth/register/`
2. Account created as **inactive** (`is_active=False`)
3. Verification email sent (via Celery if available)
4. User clicks link → `GET /api/v1/auth/verify-email/?uid=...&token=...`
5. Account activated → JWT tokens returned

## Using JWT in Requests

Include the access token in the `Authorization` header:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGci...
```

## Token Refresh

When the access token expires, use the refresh token to get a new one:

```bash
POST /api/v1/auth/token/refresh/
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

## Password Reset Flow

1. `POST /api/v1/auth/password/forgot/` with `{"email": "user@example.com"}`
2. OTP sent to email (6-digit code, valid for 5 minutes)
3. `POST /api/v1/auth/password/verify-otp/` with `{"email": "...", "otp": "123456"}`
4. `POST /api/v1/auth/password/reset/` with `{"email": "...", "otp": "123456", "new_password": "...", "confirm_password": "..."}`

## User Roles

| Role | Value | Description |
|------|-------|-------------|
| `USER` | Default | Regular user |
| `ADMIN` | Staff | Can manage content |
| `SUPER_ADMIN` | Superuser | Full access |

## Permission Classes

```python
from apps.core.permissions import IsActiveUser, IsAdmin, IsSuperAdmin, IsAdminOrReadOnly, IsOwner

class MyView(APIView):
    permission_classes = [IsAdmin]  # Only admins
```
