"""
Unit tests for URL routing and login/landing paths.
"""

from django.urls import resolve, reverse

from overrides.api.views import LandingPageView, LoginView, SetLanguageView, SignupView


class TestURLRouting:
    """
    Test URL routing configurations for root landing page and auth endpoints.
    """

    def test_landing_page_url_resolves(self):
        """Verify the root path resolves to LandingPageView."""
        match = resolve("/")
        assert match.url_name == "ui-root"
        assert match.func.view_class is LandingPageView

    def test_login_url_resolves(self):
        """Verify the login path resolves to LoginView without hash fragments."""
        match = resolve("/login/")
        assert match.url_name == "ui-login"
        assert match.func.view_class is LoginView

    def test_signup_url_resolves(self):
        """Verify the signup path resolves to SignupView."""
        match = resolve("/signup/")
        assert match.url_name == "ui-signup"
        assert match.func.view_class is SignupView

    def test_register_url_resolves(self):
        """Verify the register path resolves to SignupView."""
        match = resolve("/register/")
        assert match.url_name == "ui-register"
        assert match.func.view_class is SignupView

    def test_set_language_url_resolves(self):
        """Verify the set-language path resolves to SetLanguageView."""
        match = resolve("/set-language/")
        assert match.url_name == "set-language"
        assert match.func.view_class is SetLanguageView

    def test_login_url_reverse(self):
        """Verify reverse('ui-login') returns '/login/'."""
        url = reverse("ui-login")
        assert url == "/login/"

    def test_landing_page_reverse(self):
        """Verify reverse('ui-root') returns '/'."""
        url = reverse("ui-root")
        assert url == "/"

    def test_set_language_reverse(self):
        """Verify reverse('set-language') returns '/set-language/'."""
        url = reverse("set-language")
        assert url == "/set-language/"
