"""
Unit and integration tests for LoadShare template views, authenticated template flow,
and Layer 2 State Persistence for bilingual UI support.
"""

from datetime import timedelta

import pytest
from core.apps.users.services.otp.factory import OTPServiceFactory
from core.utils.middleware import JWTCookieAuthenticationMiddleware
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import Client, RequestFactory
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from overrides.api.views import (
    DJANGO_LANGUAGE_COOKIE_NAME,
    LANGUAGE_COOKIE_NAME,
    LandingPageView,
    LoginView,
    SignupView,
)


@pytest.fixture
def user(db):
    """Create a standard active user for authenticated view tests."""
    user_model = get_user_model()
    return user_model.objects.create_user(
        username="driver_rajesh",
        phone_number="+919876543210",
        password=None,
    )


class TestLandingPageView:
    """
    Test LandingPageView behavior, design reference components, and bilingual state persistence.
    """

    def test_unauthenticated_landing_page_renders_otp_login(self, rf: RequestFactory):
        """Verify unauthenticated landing page presents the OTP login interface."""
        request = rf.get("/")
        request.user = AnonymousUser()

        view = LandingPageView.as_view()
        response = view(request)

        assert response.status_code == 200
        content = response.render().content.decode("utf-8")

        # OTP Login form structure is present
        assert "otp_login_identifier" in content
        assert "form_otp_login" in content
        assert "data-otp-tab" in content

        # No password or username login method switcher
        assert "auth-method-switcher" not in content
        assert "form_username_login" not in content

        # Session timeout overlay dialog is present in DOM
        assert "session_timeout_overlay" in content
        assert "btn_session_timeout_login" in content
        assert "Session Expired" in content

    def test_authenticated_landing_page_renders_dashboard(
        self, rf: RequestFactory, user
    ):
        """Verify authenticated landing page renders the modular shell layout."""
        request = rf.get("/")
        request.user = user

        view = LandingPageView.as_view()
        response = view(request)

        assert response.status_code == 200
        content = response.render().content.decode("utf-8")

        # Landing shell container is rendered
        assert "landing-page-shell" in content
        assert "landing-top-bar" in content

        # Both Language and Theme toggles are present in top bar
        assert "lang-toggle-btn" in content
        assert "theme-toggle-btn" in content

        # OTP Login form is NOT shown for active session
        assert "form_otp_login" not in content

        # Session timeout overlay dialog is present in DOM for session expiry watching
        assert "session_timeout_overlay" in content
        assert "btn_session_timeout_login" in content

    def test_design_reference_components_present(self, rf: RequestFactory, user):
        """Verify placements and navigation components from reference design exist in rendered HTML."""
        request = rf.get("/")
        request.user = user

        view = LandingPageView.as_view()
        response = view(request)
        content = response.render().content.decode("utf-8")

        # Theme variables, override and layout CSS linked
        for css_asset in [
            "variables.css",
            "theme_override.css",
            "landing_layout.css",
            "floating_chip.css",
            "bottom_navbar.css",
        ]:
            assert css_asset in content

        # Floating chip, navbar, top-bar-title and tabs
        assert "desktop-floating-chip" in content
        assert "mobile-bottom-navbar" in content
        assert 'id="top-bar-title"' in content

        for tab in ["book-corridor", "rates", "home", "support", "profile"]:
            assert f'data-tab="{tab}"' in content
            assert f'id="view-{tab}"' in content

        for js_asset in [
            "theme_toggle.js",
            "navigation_state.js",
            "corridor_state.js",
            "profile_state.js",
            "language_toggle.js",
        ]:
            assert js_asset in content

    def test_corridor_view_components_present(self, rf: RequestFactory, user):
        """Verify corridor booking subview and wizard components are present."""
        request = rf.get("/")
        request.user = user

        response = LandingPageView.as_view()(request)
        content = response.render().content.decode("utf-8")

        expected_ids = [
            "search-engine",
            "wizardStep1",
            "wizardStep2",
            "wizardStep3",
            "results-container",
            "stateCardsDefault",
            "stateCardsSkeleton",
            "stateCardsEmpty",
            "stateCardsCapacity",
            "stateCardsError",
            "stickyBottomBar",
        ]
        for element_id in expected_ids:
            assert f'id="{element_id}"' in content

    def test_profile_view_components_present(self, rf: RequestFactory, user):
        """Verify profile subview and booking management components are present."""
        request = rf.get("/")
        request.user = user

        response = LandingPageView.as_view()(request)
        content = response.render().content.decode("utf-8")

        expected_ids = [
            "account-card",
            "account-view-mode",
            "account-edit-mode",
            "bookings-section",
            "booking-cards-list",
            "booking-empty-state",
            "filter-all",
            "filter-active",
            "filter-completed",
        ]
        for element_id in expected_ids:
            assert f'id="{element_id}"' in content

    def test_session_timeout_dialog_attributes(self, rf: RequestFactory, user):
        """Verify session timeout modal dialog has the expected button and links."""
        request = rf.get("/")
        request.user = user

        view = LandingPageView.as_view()
        response = view(request)
        content = response.render().content.decode("utf-8")

        assert 'id="session_timeout_overlay"' in content
        assert 'class="session-timeout-overlay"' in content
        assert 'role="alertdialog"' in content
        assert 'id="session_timeout_title"' in content
        assert 'id="session_timeout_desc"' in content
        assert 'id="btn_session_timeout_login"' in content
        assert 'href="/login/?next=/"' in content

    def test_layer2_bilingual_cookie_persistence(self, rf: RequestFactory, user):
        """Verify Layer 2 State Persistence: loadshare_lang cookie renders Hindi on SSR."""
        request = rf.get("/")
        request.user = user
        request.COOKIES[LANGUAGE_COOKIE_NAME] = "hi"

        view = LandingPageView.as_view()
        response = view(request)
        content = response.render().content.decode("utf-8")

        # Hindi translations appear in SSR output
        assert "लोडशेयर" in content
        assert "पायलट चरण: केवल दिल्ली ⇄ जयपुर कॉरिडोर हेतु पार्सल सेवा" in content
        assert "उसी रूट पर जा रहे ट्रकों से किफायती पार्सल भेजें" in content
        assert "थोक कॉरिडोर दरें" in content

    def test_layer2_bilingual_query_param_sets_cookie(self, rf: RequestFactory, user):
        """Verify ?lang=hi query parameter sets persistent language cookies on response."""
        request = rf.get("/?lang=hi")
        request.user = user

        view = LandingPageView.as_view()
        response = view(request)

        assert response.status_code == 200
        assert LANGUAGE_COOKIE_NAME in response.cookies
        assert response.cookies[LANGUAGE_COOKIE_NAME].value == "hi"
        assert DJANGO_LANGUAGE_COOKIE_NAME in response.cookies
        assert response.cookies[DJANGO_LANGUAGE_COOKIE_NAME].value == "hi"


class TestLoginView:
    """
    Test LoginView behavior enforcing OTP-only authentication.
    """

    def test_login_view_renders_otp_only(self, rf: RequestFactory):
        """Verify LoginView displays OTP flow and excludes username/password switcher."""
        request = rf.get("/login/")
        request.user = AnonymousUser()

        view = LoginView.as_view()
        response = view(request)

        assert response.status_code == 200
        content = response.render().content.decode("utf-8")

        # Enforces OTP
        assert "otp_login_identifier" in content
        assert "form_otp_login" in content
        assert "btn_send_login_otp" in content

        # No username/password switcher
        assert "auth-method-switcher" not in content
        assert "form_username_login" not in content

        # Session timeout overlay is present
        assert "session_timeout_overlay" in content
        assert "btn_session_timeout_login" in content

        # LoadShare Highway Corridor theme & design reference components
        assert "theme_override.css" in content
        assert "LoadShare" in content
        assert "barcode-strip" in content
        assert "auth-lang-toggle" in content
        assert "1800-419-7688" in content

    def test_signup_view_renders_signup_tab(self, rf: RequestFactory):
        """Verify SignupView configures initial_tab to signup."""
        request = rf.get("/signup/")
        request.user = AnonymousUser()

        view = SignupView.as_view()
        response = view(request)

        assert response.status_code == 200
        content = response.render().content.decode("utf-8")

        assert "otp_login_identifier" in content
        assert "data-initial-tab" in content
        assert "signup" in content
        assert "otp_signup.js" in content

    def test_client_get_landing_page_and_login(self, client: Client):
        """Verify full HTTP request-response cycle for root and login URLs."""
        resp_root = client.get("/")
        assert resp_root.status_code == 200
        assert "session_timeout_overlay" in resp_root.content.decode("utf-8")

        resp_login = client.get("/login/")
        assert resp_login.status_code == 200
        assert "otp_login_identifier" in resp_login.content.decode("utf-8")

    def test_default_redirect_settings_routes_to_root(self):
        """Verify settings.DEFAULT_REDIRECT routes to root i.e. '/' instead of '/accounts/profile/'."""
        assert getattr(settings, "LOGIN_REDIRECT_URL", None) == "/"
        assert getattr(settings, "DEFAULT_REDIRECT", "") in ("", "/")

    def test_login_view_respects_next_query_param(self, rf: RequestFactory):
        """Verify LoginView respects next parameter in query string."""
        request = rf.get("/login/?next=/dashboard/orders/")
        request.user = AnonymousUser()

        view = LoginView.as_view()
        response = view(request)
        assert response.status_code == 200
        content = response.render().content.decode("utf-8")
        assert 'data-redirect-url="/dashboard/orders/"' in content

    def test_login_view_redirects_authenticated_user(self, rf: RequestFactory, user):
        """Verify already authenticated users navigating to /login/ are redirected to root."""
        request = rf.get("/login/")
        request.user = user

        view = LoginView.as_view()
        response = view(request)
        assert response.status_code == 302
        assert response.url == "/"

    def test_jwt_cookie_authentication_middleware(self, rf: RequestFactory, user):
        """Verify JWTCookieAuthenticationMiddleware populates request.user from access_token cookie."""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        request = rf.get("/")
        request.user = AnonymousUser()
        request.COOKIES["access_token"] = access_token

        def get_response(req):
            return req.user

        middleware = JWTCookieAuthenticationMiddleware(get_response)
        authenticated_user = middleware(request)

        assert authenticated_user.is_authenticated
        assert authenticated_user.id == user.id

    def test_jwt_cookie_middleware_expired_token_returns_404_on_protected_path(
        self, rf: RequestFactory, user
    ):
        """Verify JWTCookieAuthenticationMiddleware rejects expired JWT cookie with 404."""
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        access.set_exp(lifetime=-timedelta(seconds=10))
        expired_token = str(access)

        request = rf.get("/")
        request.user = AnonymousUser()
        request.COOKIES["access_token"] = expired_token

        def get_response(req):
            return HttpResponse("ok")

        middleware = JWTCookieAuthenticationMiddleware(get_response)
        response = middleware(request)

        assert response.status_code == 404
        assert "access_token" in response.cookies
        # Verify cookie is marked for deletion
        assert response.cookies["access_token"]["max-age"] == 0

    def test_jwt_cookie_middleware_expired_token_allowed_on_exempt_path(
        self, rf: RequestFactory, user
    ):
        """Verify JWTCookieAuthenticationMiddleware allows expired JWT cookie on exempt auth path."""
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        access.set_exp(lifetime=-timedelta(seconds=10))
        expired_token = str(access)

        request = rf.get("/login/")
        request.user = AnonymousUser()
        request.COOKIES["access_token"] = expired_token

        def get_response(req):
            return HttpResponse("login page ok")

        middleware = JWTCookieAuthenticationMiddleware(get_response)
        response = middleware(request)

        assert response.status_code == 200

    def test_jwt_cookie_middleware_delegates_setting_auth_cookies_on_response(
        self, rf: RequestFactory
    ):
        """Verify JWTCookieAuthenticationMiddleware attaches auth cookies when response contains tokens."""
        request = rf.post("/api/users/v1/auth/login/")

        def get_response(req):
            return Response(
                {
                    "access": "test_access_jwt",
                    "refresh": "test_refresh_jwt",
                    "access_expires_in": 1800,
                }
            )

        middleware = JWTCookieAuthenticationMiddleware(get_response)
        response = middleware(request)

        assert "access_token" in response.cookies
        assert response.cookies["access_token"].value == "test_access_jwt"
        assert response.cookies["refresh_token"].value == "test_refresh_jwt"
        assert response.cookies["refresh_token"]["httponly"] is True

    def test_landing_page_with_jwt_cookie_renders_authenticated_dashboard(
        self, rf: RequestFactory, user
    ):
        """Verify request with JWT cookie renders full authenticated dashboard instead of login screen."""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        request = rf.get("/")
        request.user = AnonymousUser()
        request.COOKIES["access_token"] = access_token

        # Process through middleware
        def get_response(req):
            view = LandingPageView.as_view()
            return view(req)

        middleware = JWTCookieAuthenticationMiddleware(get_response)
        response = middleware(request)

        assert response.status_code == 200
        content = response.render().content.decode("utf-8")

        # Renders dashboard content
        assert "PILOT PHASE: Commercial Senders Only" in content
        assert "landing-page-shell" in content
        assert "desktop-floating-chip" in content
        assert "mobile-bottom-navbar" in content
        # Login form is hidden
        assert "form_otp_login" not in content

    def test_otp_verify_view_attaches_cookies_and_redirects(self, client: Client, user):
        """Verify core OTP verify flow attaches auth cookies via middleware and redirects to root."""
        code = "654321"
        OTPServiceFactory.get_service("phone").set_otp_cache(
            user.phone_number, code, timeout=300
        )

        response = client.post(
            "/api/users/v1/auth/otp/verify/",
            data={"identifier": user.phone_number, "code": code, "channel": "phone"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["redirect_url"] == "/"
        assert "access_token" in response.cookies
        assert response.cookies["access_token"].value == data["access"]
        assert response.cookies["access_token"]["samesite"] == "Lax"
        assert response.cookies["access_token"]["path"] == "/"

    def test_otp_signup_new_user_creates_account_with_name_and_cookies(
        self, client: Client, db
    ):
        """Verify OTP signup with purpose='signup' creates new user with profile fields and sets cookies."""
        new_phone = "+919999988888"
        code = "123456"

        # 1. Request OTP with purpose="signup"
        send_res = client.post(
            "/api/users/v1/auth/otp/send/",
            data={"identifier": new_phone, "channel": "phone", "purpose": "signup"},
            content_type="application/json",
        )
        assert send_res.status_code == 202

        # Manually cache code for verification (since Celery is mocked/eager)
        OTPServiceFactory.get_service("phone").set_otp_cache(
            new_phone, code, timeout=300
        )

        # 2. Verify OTP with profile fields
        verify_res = client.post(
            "/api/users/v1/auth/otp/verify/",
            data={
                "identifier": new_phone,
                "code": code,
                "channel": "phone",
                "first_name": "Rajesh",
                "last_name": "Kumar",
                "email": "rajesh@example.com",
            },
            content_type="application/json",
        )
        assert verify_res.status_code == 201
        data = verify_res.json()
        assert data["created"] is True
        assert "access_token" in verify_res.cookies

        # 3. Verify user created with correct profile data
        User = get_user_model()
        created_user = User.objects.get(phone_number=new_phone)
        assert created_user.is_phone_verified is True


class TestSetLanguageView:
    """
    Test SetLanguageView endpoint for Layer 2 State Persistence.
    """

    def test_set_language_get_sets_cookies_and_redirects(self, client: Client):
        """Verify GET /set-language/?lang=hi redirects and sets language cookies."""
        response = client.get("/set-language/?lang=hi&next=/")
        assert response.status_code == 302
        assert response.url == "/"
        assert LANGUAGE_COOKIE_NAME in response.cookies
        assert response.cookies[LANGUAGE_COOKIE_NAME].value == "hi"
        assert DJANGO_LANGUAGE_COOKIE_NAME in response.cookies
        assert response.cookies[DJANGO_LANGUAGE_COOKIE_NAME].value == "hi"

    def test_set_language_post_sets_cookies(self, client: Client):
        """Verify POST /set-language/ with lang=hi sets language cookies."""
        response = client.post("/set-language/", data={"lang": "hi", "next": "/"})
        assert response.status_code == 302
        assert response.url == "/"
        assert response.cookies[LANGUAGE_COOKIE_NAME].value == "hi"

    def test_set_language_invalid_falls_back_to_default(self, client: Client):
        """Verify invalid language falls back to English ('en')."""
        response = client.get("/set-language/?lang=invalid_lang&next=/")
        assert response.status_code == 302
        assert response.cookies[LANGUAGE_COOKIE_NAME].value == "en"
