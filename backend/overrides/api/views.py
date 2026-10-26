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

LOGGER = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ("en", "hi")
DEFAULT_LANGUAGE = "en"
LANGUAGE_COOKIE_NAME = "loadshare_lang"
DJANGO_LANGUAGE_COOKIE_NAME = "django_language"
COOKIE_MAX_AGE = 365 * 24 * 60 * 60  # 1 year

# Built-in bilingual fallback dictionary for LoadShare landing page
LANDING_PAGE_LABELS = {
    "brand_name": {"en": "LoadShare", "hi": "लोडशेयर"},
    "brand_tagline": {
        "en": "Direct Corridor Freight & Parcel Delivery",
        "hi": "डायरेक्ट कॉरिडोर फ्रेट और पार्सल डिलीवरी",
    },
    "pilot_notice": {
        "en": "PILOT PHASE: Commercial Senders Only on Delhi ⇄ Jaipur Corridor",
        "hi": "पायलट चरण: केवल दिल्ली ⇄ जयपुर कॉरिडोर हेतु पार्सल सेवा",
    },
    "hero_corridor_badge": {
        "en": "NH48 FREIGHT CORRIDOR • LIVE SLOTS",
        "hi": "NH48 फ्रेट कॉरिडोर • लाइव स्लॉट",
    },
    "hero_headline": {
        "en": "Send parcels on trucks already traveling your route",
        "hi": "उसी रूट पर जा रहे ट्रकों से किफायती पार्सल भेजें",
    },
    "hero_subtitle": {
        "en": "Direct corridor delivery at wholesale freight rates. No multiple hub handling, straight point-to-point transit for small businesses & traders.",
        "hi": "थोक भाड़े पर सीधे कॉरिडोर से पार्सल भेजें। बिना बार-बार हब बदले, सीधे एक बिंदु से दूसरे बिंदु तक त्वरित पार्सल डिस्पेच।",
    },
    "hero_cta_book": {
        "en": "Book Pilot Corridor Delivery",
        "hi": "पायलट कॉरिडोर पार्सल बुक करें",
    },
    "hero_cta_hubs": {
        "en": "View NH48 Transit Hubs",
        "hi": "NH48 ट्रांजिट हब देखें",
    },
    "trust_badge_otp": {
        "en": "OTP-verified pickup & delivery • Direct intercity route • No middlemen markups",
        "hi": "OTP-सत्यापित पिकअप व डिलीवरी • सीधा अंतर-शहर रूट • कोई बिचौलिया शुल्क नहीं",
    },
    "how_it_works_title": {
        "en": "How Corridor Dispatch Works",
        "hi": "पार्सल भेजने की 3 सरल प्रक्रियाएँ",
    },
    "how_it_works_subtitle": {
        "en": "Direct freight integration without repetitive sorting centers.",
        "hi": "बिना बार-बार छंटाई केंद्रों के सीधा फ्रेट ट्रांसपोर्ट एकीकरण।",
    },
    "how_it_works_step1_title": {
        "en": "Request Pickup & Route",
        "hi": "पिकअप व रूट चुनें",
    },
    "how_it_works_step1_desc": {
        "en": "Specify parcel weight, dimensions, and drop hub. Get immediate locked pricing with zero weight discrepancies.",
        "hi": "पार्सल वजन, आयाम और ड्रॉप हब चुनें। बिना किसी अतिरिक्त शुल्क के तुरंत निश्चित दर प्राप्त करें।",
    },
    "how_it_works_step2_title": {
        "en": "Match with On-Route Truck",
        "hi": "रूट पर चल रहे ट्रक से मिलान",
    },
    "how_it_works_step2_desc": {
        "en": "Assigned directly to a verified commercial carrier already scheduled and fueled on NH48 corridor.",
        "hi": "NH48 कॉरिडोर पर पहले से निर्धारित और सत्यापित कमर्शियल ट्रक से तुरंत सीधा जुड़ाव।",
    },
    "how_it_works_step3_title": {
        "en": "Track & OTP Handover",
        "hi": "ट्रैक व OTP से सुरक्षित डिलीवरी",
    },
    "how_it_works_step3_desc": {
        "en": "Live automated milestone pings. Handover happens only upon physical numeric OTP verification by recipient.",
        "hi": "लाइव ऑटोमेटेड माइलस्टोन अपडेट्स। डिलीवरी केवल प्राप्तकर्ता द्वारा भौतिक संख्यात्मक OTP सत्यापन पर ही संपन्न।",
    },
    "rates_title": {
        "en": "Wholesale Corridor Rates",
        "hi": "थोक कॉरिडोर दरें",
    },
    "rates_subtitle": {
        "en": "Direct freight space pricing. No volume surcharge or dark fuel multipliers.",
        "hi": "सीधा फ्रेट स्पेस मूल्य निर्धारण। कोई अप्रत्यक्ष शुल्क या अतिरिक्त ईंधन अधिभार नहीं।",
    },
    "tier1_name": {"en": "TIER 1 • PARCELS", "hi": "श्रेणी 1 • पार्सल"},
    "tier1_weight": {"en": "10 kg – 50 kg", "hi": "10 किग्रा – 50 किग्रा"},
    "tier1_rate": {"en": "₹12", "hi": "₹12"},
    "tier1_unit": {"en": "/ kg", "hi": "/ किग्रा"},
    "tier1_subtext": {
        "en": "Minimum docket fee: ₹350",
        "hi": "न्यूनतम डॉकेट शुल्क: ₹350",
    },
    "tier2_name": {"en": "TIER 2 • COMMERCIAL", "hi": "श्रेणी 2 • कमर्शियल"},
    "tier2_weight": {"en": "51 kg – 250 kg", "hi": "51 किग्रा – 250 किग्रा"},
    "tier2_rate": {"en": "₹8.50", "hi": "₹8.50"},
    "tier2_unit": {"en": "/ kg", "hi": "/ किग्रा"},
    "tier2_badge": {
        "en": "Most Popular for Traders",
        "hi": "व्यापारियों की पहली पसंद",
    },
    "tier2_subtext": {
        "en": "No separate handling surcharge",
        "hi": "कोई अलग हैंडलिंग चार्ज नहीं",
    },
    "tier3_name": {"en": "TIER 3 • PART-LOAD (LTL)", "hi": "श्रेणी 3 • पार्ट-लोड"},
    "tier3_weight": {"en": "250 kg+", "hi": "250 किग्रा+"},
    "tier3_rate": {"en": "₹6.00", "hi": "₹6.00"},
    "tier3_unit": {"en": "/ kg", "hi": "/ किग्रा"},
    "tier3_subtext": {
        "en": "Priority bay loading included",
        "hi": "प्राथमिकता बे-लोडिंग शामिल",
    },
    "faq_title": {
        "en": "Frequently Asked Questions",
        "hi": "अक्सर पूछे जाने वाले प्रश्न",
    },
    "faq_subtitle": {
        "en": "Clear ground operational rules for commercial consignors.",
        "hi": "कमर्शियल कंसाइनर्स हेतु स्पष्ट ऑन-ग्राउंड परिचालन नियम।",
    },
    "booking_title": {
        "en": "Sender Express Booking",
        "hi": "एक्सप्रेस पार्सल बुकिंग",
    },
    "booking_subtitle": {
        "en": "No password needed. Verified via 4-digit SMS OTP.",
        "hi": "पासवर्ड की आवश्यकता नहीं। 4-अंकीय SMS OTP से त्वरित सत्यापन।",
    },
    "label_phone": {
        "en": "10-DIGIT MOBILE NUMBER",
        "hi": "10-अंकीय मोबाइल नंबर",
    },
    "label_name": {
        "en": "FULL NAME / BUSINESS NAME",
        "hi": "पूरा नाम / व्यापार का नाम",
    },
    "label_route": {
        "en": "ACTIVE CORRIDOR ROUTE",
        "hi": "सक्रिय कॉरिडोर रूट",
    },
    "btn_request_otp": {
        "en": "Request Corridor OTP & Rates",
        "hi": "कॉरिडोर OTP व दरें प्राप्त करें",
    },
    "footer_copyright": {
        "en": "© 2025 LoadShare Logistics India Ltd. All rights reserved. Registered inter-city parcel carrier under Motor Vehicles (MV) Carrier Framework.",
        "hi": "© 2025 लोडशेयर लॉजिस्टिक्स इंडिया लिमिटेड। सर्वाधिकार सुरक्षित। मोटर वाहन (MV) फ्रेमवर्क के तहत पंजीकृत इंटर-सिटी पार्सल कैरियर।",
    },
}


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
