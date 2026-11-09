"""
Template views for the LoadShare host overrides application.

Provides server-rendered UI views for the root landing page, OTP authentication
flows, Layer 2 state persistence for bilingual (English & Hindi) support, and
direct file-based label resolution from the labels directory.
"""

import json
import logging
import os
from functools import lru_cache
from typing import Any

from core.apps.crm import get_customer_model
from core.utils.labels import LabelDict
from core.utils.views import BaseTemplateView
from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.views.generic.base import View

LOGGER = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ("en", "hi")
DEFAULT_LANGUAGE = "en"
LANGUAGE_COOKIE_NAME = "loadshare_lang"
DJANGO_LANGUAGE_COOKIE_NAME = "django_language"
COOKIE_MAX_AGE = 365 * 24 * 60 * 60  # 1 year

Customer = get_customer_model()


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


@lru_cache(maxsize=16)
def load_labels_file(filename: str) -> dict[str, Any]:
    """
    Load a JSON label dictionary from the backend/labels directory.

    Args:
        filename (str): Name of the JSON file (e.g., 'en.json', 'hi.json').

    Returns:
        dict[str, Any]: Loaded dictionary or empty dict if not found.
    """
    file_path = os.path.join(settings.BASE_DIR, "labels", filename)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as exc:
            LOGGER.warning("Could not read labels file %s: %s", filename, exc)
    return {}


def get_language_labels(lang: str = "en") -> dict[str, str]:
    """
    Retrieve localized label dictionary for the specified language from json files.

    Args:
        lang (str): Target language code ('en' or 'hi').

    Returns:
        dict[str, str]: Dictionary mapping label keys to translated strings.
    """
    labels = load_labels_file(f"{lang}.json")
    if labels and isinstance(labels, dict):
        return labels

    multi_labels = load_labels_file("users_template_label.json")
    if multi_labels and isinstance(multi_labels, dict):
        return {
            k: (v.get(lang) or v.get("en") or "") if isinstance(v, dict) else str(v)
            for k, v in multi_labels.items()
        }

    return {}


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
            request.GET.get("next") or request.META.get("HTTP_REFERER") or "/"
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
    Base TemplateView providing bilingual context, file-based labels,
    and Layer 2 cookie persistence.
    """

    def add_labels_context(self, context: dict) -> None:
        """
        Inject template labels directly from file-based dictionaries without database calls.

        Args:
            context (dict): The template context dictionary.
        """
        if "labels" not in context or not isinstance(context["labels"], LabelDict):
            current_lang = context.get("current_lang") or get_request_language(
                self.request
            )
            active_labels = get_language_labels(current_lang)
            context["labels"] = LabelDict(backend_labels=active_labels)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """
        Assemble template context with active language and localized labels
        retrieved directly from JSON files in the labels directory.

        Args:
            **kwargs: Keyword arguments passed to get_context_data.

        Returns:
            dict[str, Any]: Context dictionary with bilingual label maps and current language.
        """
        context = super().get_context_data(**kwargs)
        current_lang = get_request_language(self.request)
        context["current_lang"] = current_lang
        context["supported_languages"] = SUPPORTED_LANGUAGES

        # Load language-specific label dictionaries from backend/labels/
        labels_en = get_language_labels("en")
        labels_hi = get_language_labels("hi")
        active_labels = labels_hi if current_lang == "hi" else labels_en

        context["labels_en"] = labels_en
        context["labels_hi"] = labels_hi
        context["labels"] = LabelDict(backend_labels=active_labels)
        context["user"] = getattr(self.request, "user", None)
        context["phone"] = getattr(
            getattr(self.request, "user", None), "phone_number", None
        )
        return context

    def render_to_response(
        self, context: dict[str, Any], **response_kwargs: Any
    ) -> HttpResponse:
        """
        Render response and persist active language and customer ID in cookies.

        Args:
            context (dict[str, Any]): Template context dictionary.
            **response_kwargs: Extra keyword arguments passed to response class.

        Returns:
            HttpResponse: Rendered response with cookies attached.
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
        if customer := context.get("customer"):
            response.set_cookie(
                "customer_id",
                str(customer.id),
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

        # Inject customer model if authenticated
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            customer, _ = Customer.objects.get_or_create_for_user(user)
            customer = (
                Customer.objects.filter(pk=customer.pk)
                .prefetch_related(
                    "phones",
                    "emails",
                    "preferences__preference_type",
                )
                .first()
            )
            context["customer"] = customer

        return context
