"""
Unit and integration tests for LoadShare template views, authenticated template flow,
and Layer 2 State Persistence for bilingual UI support.
"""

import os
from datetime import timedelta

import pytest
from core.apps.crm import get_customer_model
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
    get_language_labels,
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
    Test LandingPageView behavior and bilingual state persistence.
    """

    def test_unauthenticated_landing_page_renders_otp_login(self, rf: RequestFactory):
        """Verify unauthenticated landing page presents the OTP login interface."""
        request = rf.get("/")
        request.user = AnonymousUser()

        view = LandingPageView.as_view()
        response = view(request)

        assert response.status_code == 200
        content = response.render().content.decode("utf-8")

        assert "form_otp_login" in content
        assert "form_username_login" not in content

    def test_authenticated_landing_page_renders_dashboard(
        self, rf: RequestFactory, user
    ):
        """Verify authenticated landing page renders dashboard and hides login form."""
        request = rf.get("/")
        request.user = user

        view = LandingPageView.as_view()
        response = view(request)

        assert response.status_code == 200
        content = response.render().content.decode("utf-8")

        # OTP Login form is NOT shown for active session
        assert "form_otp_login" not in content

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


@pytest.mark.django_db
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

        # Enforces OTP without password/username switcher
        assert "form_otp_login" in content
        assert "form_username_login" not in content

    def test_signup_view_renders_signup_tab(self, rf: RequestFactory):
        """Verify SignupView configures initial_tab to signup."""
        request = rf.get("/signup/")
        request.user = AnonymousUser()

        view = SignupView.as_view()
        response = view(request)

        assert response.status_code == 200
        assert response.context_data["initial_tab"] == "signup"

    def test_client_get_landing_page_and_login(self, client: Client):
        """Verify full HTTP request-response cycle for root and login URLs."""
        resp_root = client.get("/")
        assert resp_root.status_code == 200

        resp_login = client.get("/login/")
        assert resp_login.status_code == 200

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

        # Login form is hidden for authenticated user
        assert "form_otp_login" not in content

    def test_otp_verify_view_attaches_cookies_and_redirects(self, client: Client, user):
        """Verify core OTP verify flow attaches auth cookies via middleware and redirects to root."""
        code = "654321"
        phone_number = str(user.phone_number)
        OTPServiceFactory.get_service("phone").set_otp_cache(
            phone_number, code, timeout=300
        )

        response = client.post(
            "/api/users/v1/auth/otp/sms/login/",
            data={"phone_number": phone_number, "otp_code": code},
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
            "/api/users/v1/auth/otp/sms/send/",
            data={"phone_number": new_phone, "purpose": "signup"},
            content_type="application/json",
        )
        assert send_res.status_code == 202

        # Manually cache code for verification (since Celery is mocked/eager)
        OTPServiceFactory.get_service("phone").set_otp_cache(
            new_phone, code, timeout=300
        )

        # 2. Verify OTP with profile fields
        verify_res = client.post(
            "/api/users/v1/auth/otp/sms/signup/",
            data={
                "phone_number": new_phone,
                "otp_code": code,
                "first_name": "Rajesh",
                "last_name": "Kumar",
                "email": "rajesh@example.com",
            },
            content_type="application/json",
        )
        assert verify_res.status_code == 201
        assert "access" in verify_res.json()
        assert "access_token" in verify_res.cookies

        # 3. Verify user created with correct profile data
        User = get_user_model()
        created_user = User.objects.get(phone_number=new_phone)
        assert created_user.is_phone_verified is True


@pytest.mark.django_db
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


@pytest.mark.django_db
class TestCRMCustomerAPI:
    """
    Test suite for CRM Customer endpoints (/api/customers/v1/customers/{id}/).
    """

    def test_unauthenticated_crm_customer_returns_401(self, client: Client, user):
        """Verify unauthenticated requests to CRM customer detail return 401."""
        Customer = get_customer_model()
        customer, _ = Customer.objects.get_or_create_for_user(user)

        response = client.get(f"/api/customers/v1/customers/{customer.id}/")
        assert response.status_code == 401

    def test_authenticated_crm_customer_returns_details_and_relations(
        self, client: Client, user
    ):
        """Verify authenticated GET /api/customers/v1/customers/{id}/ returns serialized customer data."""
        Customer = get_customer_model()
        customer, _ = Customer.objects.get_or_create_for_user(user)

        refresh = RefreshToken.for_user(user)
        client.cookies["access_token"] = str(refresh.access_token)

        response = client.get(f"/api/customers/v1/customers/{customer.id}/")
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == str(customer.id)
        assert "phones" in data
        assert "emails" in data
        assert "preferences" in data
        # Check primary phone matching user phone number
        assert len(data["phones"]) >= 1
        assert data["phones"][0]["phone"] == str(user.phone_number)

    def test_authenticated_crm_customer_updates_profile(self, client: Client, user):
        """Verify PUT /api/customers/v1/customers/{id}/ updates customer attributes."""
        Customer = get_customer_model()
        customer, _ = Customer.objects.get_or_create_for_user(user)

        refresh = RefreshToken.for_user(user)
        client.cookies["access_token"] = str(refresh.access_token)

        payload = {
            "business_name": "Sharma Logistics Express",
            "customer_type": "individual",
        }
        response = client.put(
            f"/api/customers/v1/customers/{customer.id}/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["business_name"] == "Sharma Logistics Express"


@pytest.mark.django_db
class TestFileBasedLabelResolution:
    """
    Test suite for file-based label resolution directly from backend/labels directory.
    """

    def test_json_label_files_exist_and_contain_keys(self):
        """Verify JSON label files exist in backend/labels/ with full translation keys."""
        labels_dir = os.path.join(settings.BASE_DIR, "labels")
        assert os.path.exists(os.path.join(labels_dir, "en.json"))
        assert os.path.exists(os.path.join(labels_dir, "hi.json"))
        assert os.path.exists(os.path.join(labels_dir, "users_template_label.json"))

        en_labels = get_language_labels("en")
        hi_labels = get_language_labels("hi")
        assert len(en_labels) >= 200
        assert len(hi_labels) >= 200
        assert en_labels["brand_name"] == "ROUTEWAY"
        assert hi_labels["brand_name"] == "लोडशेयर"

    def test_landing_page_renders_labels_directly_from_json_files(
        self, rf: RequestFactory, user
    ):
        """Verify LandingPageView renders Hindi labels directly from JSON files without DB lookup."""
        request = rf.get("/?lang=hi")
        request.user = user

        view = LandingPageView.as_view()
        response = view(request)
        content = response.render().content.decode("utf-8")

        assert "लोडशेयर" in content
        assert "उसी रूट पर जा रहे ट्रकों से किफायती पार्सल भेजें" in content
