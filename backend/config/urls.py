"""
Tenant-schema URL configuration for the rideshare app.

Routes:
    - Root / Landing Page: `/` (LandingPageView)
    - Authentication UI: `/login/`, `/signup/`, `/register/` (OTP-only flows)
    - Language Selector: `/set-language/` (Layer 2 state persistence)
    - Django Admin: `/admin/` (private_admin_site)
    - Backend API: `/api/<app>/<version>/...`
"""

from core.utils.admin import private_admin_site
from core.utils.urls import build_app_urlpatterns
from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from overrides.api.views import (
    LandingPageView,
    LoginView,
    SetLanguageView,
    SignupView,
)

urlpatterns = [
    # UI / Template Endpoints
    path("", LandingPageView.as_view(), name="ui-root"),
    path("login/", LoginView.as_view(), name="ui-login"),
    path("signup/", SignupView.as_view(), name="ui-signup"),
    path("register/", SignupView.as_view(), name="ui-register"),
    path("set-language/", SetLanguageView.as_view(), name="set-language"),
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
    # Django Admin
    path("admin/", private_admin_site.urls),
    # Backend API Endpoints
    *build_app_urlpatterns(),
]
