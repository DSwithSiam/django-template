"""URL configuration for the project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from config import env as env_module

# ---------------------------------------------------------------------------
# Swagger / OpenAPI schema
# ---------------------------------------------------------------------------
swagger_info = openapi.Info(
    title=env_module.PROJECT_NAME,
    default_version=env_module.PROJECT_VERSION,
    description=env_module.PROJECT_DESCRIPTION,
    terms_of_service="https://www.google.com/policies/terms/",
    license=openapi.License(name="BSD License"),
)

schema_view = get_schema_view(
    swagger_info,
    public=True,
    permission_classes=(permissions.AllowAny,),
)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
def health_check(request):
    """Simple health check endpoint for load balancers and monitoring."""
    return JsonResponse({"status": "ok"})


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("api/v1/", include("apps.user.urls")),
    path("api/v1/", include("apps.contact.urls")),
]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Swagger — conditional
if not env_module.DISABLE_SWAGGER:
    urlpatterns += [
        path(
            "swagger/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        path(
            "redoc/",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
    ]

# Admin — conditional
if not env_module.DISABLE_ADMIN:
    urlpatterns += [
        path("admin/", admin.site.urls),
    ]
