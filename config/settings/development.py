"""
Development settings.

Usage:
    DJANGO_SETTINGS_MODULE=config.settings.development
"""

from config import env as env_module
from config.settings.base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["*"]

# ---------------------------------------------------------------------------
# Database — SQLite by default for easy local dev
# ---------------------------------------------------------------------------
DATABASES = {
    "default": env_module.env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR}/db.sqlite3"),  # noqa: F405
}

# ---------------------------------------------------------------------------
# Email — print to console in development
# ---------------------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# CORS — allow all origins in development
# ---------------------------------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True

# ---------------------------------------------------------------------------
# Django Debug Toolbar (if installed)
# ---------------------------------------------------------------------------
try:
    import debug_toolbar  # noqa: F401

    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
    INTERNAL_IPS = ["127.0.0.1"]
except ImportError:
    pass

# ---------------------------------------------------------------------------
# DRF — add browsable API renderer in development
# ---------------------------------------------------------------------------
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (  # noqa: F405
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
)

# ---------------------------------------------------------------------------
# Logging — more verbose in development
# ---------------------------------------------------------------------------
LOGGING["root"]["level"] = "DEBUG"  # noqa: F405
