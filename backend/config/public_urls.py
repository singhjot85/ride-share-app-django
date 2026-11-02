from core.config.api_protected import core_public_url_mapping, resolve_and_build_paths
from core.utils.admin.sites import public_admin_site
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from overrides.api.views import LandingPageView

urlpatterns = [
    # UI / Template Endpoints
    path("", LandingPageView.as_view(), name="ui-root"),
    # Django Admin APIs
    path("admin/", public_admin_site.urls),
    # Swagger APIs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    # Backend API Endpoints
    *resolve_and_build_paths(core_public_url_mapping),
]
