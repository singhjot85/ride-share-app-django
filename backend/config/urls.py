"""
Tenant-schema URL configuration for the rideshare app.

Routes:
    - Root / Landing Page: `/` (LandingPageView)
    - Authentication UI: `/login/`, `/signup/`, `/register/` (OTP-only flows)
    - Language Selector: `/set-language/` (Layer 2 state persistence)
    - Django Admin: `/admin/` (private_admin_site)
    - Backend API: `/api/<app>/<version>/...`
"""

from core.config.api_protected import core_tenant_url_mapping, resolve_and_build_paths
from core.utils.admin import private_admin_site
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

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
    # Django Admin
    path("admin/", private_admin_site.urls),
    # Backend API Endpoints
    *resolve_and_build_paths(core_tenant_url_mapping),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
