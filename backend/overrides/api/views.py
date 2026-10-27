"""
Template views and API endpoints for the LoadShare host overrides application.

Provides server-rendered UI views for the root landing page, OTP authentication
flows, and Layer 2 state persistence for bilingual (English & Hindi) support.
"""

import logging
from typing import Any

from core.utils.labels import resolve_labels
from core.utils.views import BaseTemplateView
from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic.base import View

from overrides.labels import LANDING_PAGE_LABELS

LOGGER = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ("en", "hi")
DEFAULT_LANGUAGE = "en"
LANGUAGE_COOKIE_NAME = "loadshare_lang"
DJANGO_LANGUAGE_COOKIE_NAME = "django_language"
COOKIE_MAX_AGE = 365 * 24 * 60 * 60  # 1 year


def get_request_language(request: HttpRequest) -> str:
    """
    Determine the active UI language from query parameters, cookies, or default.

    Checks in order:
    1. ``?lang=`` query parameter.
    2. ``loadshare_lang`` cookie.
    3. ``django_language`` cookie.
    4. Django settings ``LANGUAGE_CODE``.

    Args:
        request (HttpRequest): Django request object.

    Returns:
        str: Validated language code ('en' or 'hi').
    """
    lang = request.GET.get("lang")
    if not lang:
        lang = request.COOKIES.get(LANGUAGE_COOKIE_NAME)
    if not lang:
        lang = request.COOKIES.get(DJANGO_LANGUAGE_COOKIE_NAME)
    if not lang:
        lang = getattr(settings, "LANGUAGE_CODE", DEFAULT_LANGUAGE)

    return lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


class SetLanguageView(View):
    """
    View to persist user language selection in cookies (Layer 2 State Persistence).

    Accepts GET or POST requests with a ``lang`` parameter ('en' or 'hi')
    and sets persistent cookies on the redirect response.
    """

    def get(self, request: HttpRequest) -> HttpResponse:
        """
        Set language preference via GET query parameters and redirect.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            HttpResponse: Redirect response with language cookies attached.
        """
        lang = request.GET.get("lang", DEFAULT_LANGUAGE)
        redirect_url = (
            request.GET.get("next") or request.META.get("HTTP_REFERER") or "/"
        )
        return self._build_response(redirect_url, lang)

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Set language preference via POST body and redirect.

        Args:
            request (HttpRequest): The incoming HTTP request.

        Returns:
            HttpResponse: Redirect response with language cookies attached.
        """
        lang = request.POST.get("lang", DEFAULT_LANGUAGE)
        redirect_url = (
            request.POST.get("next") or request.META.get("HTTP_REFERER") or "/"
        )
        return self._build_response(redirect_url, lang)

    def _build_response(self, redirect_url: str, lang: str) -> HttpResponse:
        """
        Construct redirect response with persistent language cookies.

        Args:
            redirect_url (str): Destination URL to redirect to.
            lang (str): Target language code ('en' or 'hi').

        Returns:
            HttpResponseRedirect: Configured redirect response.
        """
        target_lang = lang if lang in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
        response = HttpResponseRedirect(redirect_url)
        response.set_cookie(
            LANGUAGE_COOKIE_NAME,
            target_lang,
            max_age=COOKIE_MAX_AGE,
            samesite="Lax",
        )
        response.set_cookie(
            DJANGO_LANGUAGE_COOKIE_NAME,
            target_lang,
            max_age=COOKIE_MAX_AGE,
            samesite="Lax",
        )
        return response


class BaseLanguageTemplateView(BaseTemplateView):
    """
    Base TemplateView providing bilingual context and Layer 2 cookie persistence.
    """

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Assemble template context with active language and localized labels.

        Args:
            **kwargs: Keyword arguments passed to get_context_data.

        Returns:
            dict[str, Any]: Context dictionary with bilingual label maps and current language.
        """
        context = super().get_context_data(**kwargs)
        current_lang = get_request_language(self.request)
        context["current_lang"] = current_lang
        context["supported_languages"] = SUPPORTED_LANGUAGES

        # Build language-specific label dictionaries for client-side data-en and data-hi attributes
        labels_en = {k: v.get("en", "") for k, v in LANDING_PAGE_LABELS.items()}
        labels_hi = {k: v.get("hi", "") for k, v in LANDING_PAGE_LABELS.items()}
        active_labels = labels_hi if current_lang == "hi" else labels_en

        context["labels_en"] = labels_en
        context["labels_hi"] = labels_hi

        # Merge with database-resolved labels using core label infrastructure
        db_labels = resolve_labels(
            interface_type=self.template_label_interface_type,
            language=current_lang,
        )
        # Active labels provide direct fallbacks to database labels
        for key, val in active_labels.items():
            db_labels.setdefault(key, val)

        context["labels"] = db_labels
        context["user"] = getattr(self.request, "user", None)
        context["phone"] = getattr(
            getattr(self.request, "user", None), "phone_number", None
        )
        return context

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        """
        Render response and persist active language in cookies if passed via GET parameter.

        Args:
            context (dict[str, Any]): Template context dictionary.
            **response_kwargs: Extra keyword arguments passed to response class.

        Returns:
            HttpResponse: Rendered response with language cookie if requested.
        """
        response = super().render_to_response(context, **response_kwargs)
        requested_lang = self.request.GET.get("lang")
        if requested_lang and requested_lang in SUPPORTED_LANGUAGES:
            response.set_cookie(
                LANGUAGE_COOKIE_NAME,
                requested_lang,
                max_age=COOKIE_MAX_AGE,
                samesite="Lax",
            )
            response.set_cookie(
                DJANGO_LANGUAGE_COOKIE_NAME,
                requested_lang,
                max_age=COOKIE_MAX_AGE,
                samesite="Lax",
            )
        return response


class LoginView(BaseLanguageTemplateView):
    """
    Template view serving the project's OTP-only sign-in flow.

    Renders the project-specific authenticated template configured to display
    the phone/email OTP verification card without username/password fallback.
    """

    template_name = "views/authenticated_view.jinja"
    initial_tab: str = "signin"
    initial_method: str = "otp"

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Redirect already authenticated users to default destination.

        Args:
            request: The incoming HTTP request.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            HttpResponse: Redirect if authenticated, else dispatches request.
        """
        if getattr(request, "user", None) and request.user.is_authenticated:
            default_redirect = getattr(settings, "DEFAULT_REDIRECT", "") or "/"
            redirect_url = request.GET.get("next") or default_redirect
            return HttpResponseRedirect(redirect_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Assemble template context for the OTP authentication gateway.

        Args:
            **kwargs: Keyword arguments passed to get_context_data.

        Returns:
            dict[str, Any]: Template context dictionary configured for OTP login.
        """
        context = super().get_context_data(social_urls=False, **kwargs)
        default_redirect = getattr(settings, "DEFAULT_REDIRECT", "") or "/"
        next_url = self.request.GET.get("next") or default_redirect
        context.setdefault("initial_tab", self.initial_tab)
        context.setdefault("initial_method", "otp")
        context.setdefault("is_login_view", True)
        context.setdefault("landing_page_url", default_redirect)
        context.setdefault("redirect_url", next_url)
        context.setdefault("page_title", "LoadShare - Sign In")
        return context


class SignupView(LoginView):
    """
    Template view serving the project's OTP-based account creation flow.

    Inherits from LoginView but configures the initial tab to 'signup'.
    """

    initial_tab = "signup"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Assemble template context for account signup.

        Args:
            **kwargs: Keyword arguments passed to get_context_data.

        Returns:
            dict[str, Any]: Template context dictionary configured for OTP signup.
        """
        context = super().get_context_data(**kwargs)
        context["initial_tab"] = "signup"
        context["page_title"] = "LoadShare - Create Account"
        return context


class LandingPageView(BaseLanguageTemplateView):
    """
    Template view serving the LoadShare root landing page on ``""``.

    Inherits the project-specific authenticated view shell:
    - If unauthenticated, displays the OTP-only sign-in gateway.
    - If authenticated, renders the full LoadShare logistics dashboard.
    - If user session expires, displays the session timeout overlay dialog.
    - Provides bilingual support with Layer 2 state persistence.
    """

    template_name = "user_landing_page.jinja"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Assemble template context for the landing page.

        Args:
            **kwargs: Keyword arguments passed to get_context_data.

        Returns:
            dict[str, Any]: Template context dictionary for the landing page.
        """
        context = super().get_context_data(social_urls=False, **kwargs)
        default_redirect = getattr(settings, "DEFAULT_REDIRECT", "") or "/"
        context.setdefault("landing_page_url", default_redirect)
        context.setdefault("redirect_url", default_redirect)
        context.setdefault("page_title", "LoadShare - Route-Based Logistics")
        context.setdefault("page_label", "Logistics Overview")
        return context
