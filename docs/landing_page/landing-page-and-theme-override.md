# Phase 1 Analysis: LoadShare Landing Page, Design System Theme Override & Bilingual (EN/HI) UI Architecture

> **Feature Slug:** `landing-page-and-theme-override`
> **Status:** Pending User Approval (Phase 1)
> **Target Release:** POC Pilot (Delhi ⇄ Jaipur NH48 Corridor)

---

## 1. Executive Summary & Goals

This feature adapts the visual design, interactive states, and theme tokens from `local_data/design/user-facing/landing_page.html` to establish the production landing page for LoadShare.

### Key Deliverables:
1. **Design System & Theme Token Override:**
   - Override the core framework theme variables (defaulting to sky blue `#0284c7`) with the industrial logistics palette from the reference mockup:
     - **Primary:** Deep Industrial Navy (`#001428`, container `#0f2942`)
     - **Secondary / Accent:** High-Visibility Commercial Amber/Rust (`#ab3600`, container `#ff6e38`, fixed `#ffdbcf`)
     - **Background & Surfaces:** Clean Highway Off-White (`#f8f9ff`, sunken `#eff4ff`, container `#dce9ff`)
     - **Text & Foreground:** Contrast Charcoal (`#0b1c30`, muted variant `#43474d`)
   - Preserve existing component token contracts (`.btn-primary`, `.badge`, `.card`, `.stat-card`) while enabling custom design utilities (highway tracks, barcode waybill strip, sticky top bar, mobile bottom bar).
2. **Project-Aligned Component Hierarchy:**
   - **Header & Notice Strip:** Pilot corridor banner (commercial senders only on Delhi ⇄ Jaipur NH48).
   - **Hero & Schematic Manifest Card:** Visual corridor linehaul track, waybill metadata, and instant dispatch CTA.
   - **Direct Flow (How it Works):** 3-step operational breakdown (Pickup Request, Route Matching, OTP Handshake).
   - **Pilot Corridor Telemetry Section:** Origin, intermediate highway drop nodes (Manesar, Kotputli), and destination hub (Jaipur VKI Area), with live tracking line and 2G offline fallback simulator.
   - **Wholesale Pricing Tiers:** 3 weight slabs (10–50 kg @ ₹12/kg, 51–250 kg @ ₹8.50/kg, 250+ kg @ ₹6.00/kg) with locked-fare guarantee.
   - **Trust & Compliance Pillars:** OTP at pickup, OTP at delivery, KYC-screened commercial fleet drivers, live milestone SMS/WhatsApp pings, operations concierge helpline.
   - **Integrated OTP Booking Gateway:** Seamlessly connects the reference mockup's interactive flow with the project's real OTP authentication / dispatch API.
   - **Operational FAQ Accordion:** Prohibited items, payment timing (cash/UPI on delivery), linehaul consolidation advantage, consignee absence rules, carrier liability disclosure.
   - **Pre-Flight Audit Drawer & Compliant Footer:** MV logistics regulatory notices, driver APK redirect, helpline links.
   - **Mobile Docked Navigation Bar:** Quick navigation (Corridor, Pricing, Main, Support, Profile).
3. **Bilingual UI Architecture (English & Hindi):**
   - Translate all branding, headlines, labels, form instructions, error states, and FAQ entries to English (`en`) and Hindi (`hi`).
   - Implement a zero-latency hybrid strategy combining client-side instant swapping with server-side cookie persistence.

---

## 2. Technical Architecture & Component Structure

```
backend/
├── static/
│   └── css/
│       └── theme_override.css           # Project-specific CSS variables & design tokens overriding core
├── templates/
│   ├── views/
│   │   ├── authenticated_view.jinja     # Base authenticated shell (injects theme_override.css)
│   │   └── otp_login_template.jinja     # OTP gateway modal/template
│   ├── landing_page.jinja               # Full landing page extending views/authenticated_view.jinja
│   └── components/
│       ├── landing_hero.jinja           # Hero & schematic manifest route card
│       ├── landing_corridor.jinja       # NH48 linehaul hubs & simulated telemetry
│       ├── landing_pricing.jinja        # 3-tier wholesale corridor freight rates
│       ├── landing_trust_faq.jinja      # Trust pillars & regulatory FAQ accordion
│       └── landing_mobile_nav.jinja     # Docked mobile navigation bar
└── config/
    └── views.py                         # LandingPageView with multilingual labels context
```

### Constraint Compliance:
- **Rule #1:** Zero modifications to `backend/core-common-django-apps/`. All overrides are placed in `backend/templates/` and `backend/static/`.
- **Rule #6:** No unconstrained serializers or models.
- **Rule #10:** Strict POC scope — no WebSockets, Kafka, or complex third-party map APIs. The highway telemetry track uses CSS and SVG styling as in the approved reference mockup.

---

## 3. Theme Override Strategy

### A. Token Mapping

| Token Property | Core Default | LoadShare / Routeway Override | Purpose |
|---|---|---|---|
| `--color-primary` | `#0284c7` (Sky Blue) | `#001428` (Deep Navy) | Main brand elements, headings, primary buttons |
| `--color-primary-hover` | `#0369a1` | `#0f2942` | Primary hover states |
| `--color-primary-container` | `#e0f2fe` | `#0f2942` | Hero badges, card accents |
| `--color-secondary` | `#475569` (Slate) | `#ab3600` (Safety Amber) | High-contrast commercial action buttons, live indicators |
| `--color-secondary-hover` | `#334155` | `#822700` | Secondary hover states |
| `--color-secondary-container` | `#f1f5f9` | `#ff6e38` | Prominent highlights, notification pills |
| `--color-bg` | `#f8fafc` | `#f8f9ff` | Application canvas background |
| `--color-surface` | `#ffffff` | `#ffffff` | Card surfaces |
| `--color-surface-sunken` | `#f1f5f9` | `#eff4ff` | Secondary containers, inputs, waybill backgrounds |
| `--color-text` | `#0f172a` | `#0b1c30` | High-contrast typography |
| `--color-text-muted` | `#64748b` | `#43474d` | Subheads, secondary metadata |

### B. Injection Mechanism
1. Define `backend/static/css/theme_override.css`.
2. Add `PROJECT_DIR / "static"` to `STATICFILES_DIRS` in `backend/config/settings/base.py`.
3. In `backend/templates/views/authenticated_view.jinja`, mount the stylesheet inside `{% block extra_head %}`:
   ```jinja
   {% block extra_head %}
       <link rel="stylesheet" href="{{ static('css/theme_override.css') }}">
   {% endblock extra_head %}
   ```
4. This cascades over core design tokens without affecting the core framework submodule.

---

## 4. Multilingual (Bilingual EN / HI) Implementation Plan

### A. Requirements & Analysis
- Target user base: Senders, small business owners, and logistics dispatchers in North India corridors (Delhi, Haryana, Rajasthan).
- Languages: English (`en`) and Hindi (`hi`).
- User expectation: Instant toggling via header/footer button without losing form inputs or forcing a jarring page refresh.

### B. Proposed Dual-Layer Architecture

```
                    ┌────────────────────────────────────────────────────────┐
                    │               User clicks [EN / हिंदी]                 │
                    └──────────────────────────┬─────────────────────────────┘
                                               │
                       ┌───────────────────────┴───────────────────────┐
                       ▼                                               ▼
          [Layer 1: Client-Side Instant]                [Layer 2: State Persistence]
         - Reads `data-en` / `data-hi` attributes       - Sets cookie: `loadshare_lang=hi`
         - Swaps `.lang-text` innerText immediately     - Next HTTP GET passes cookie
         - Toggles active pill styling in header        - Django SSR renders target language
```

### C. Server-Side Context & Database Label Resolution
1. **Label Resolution Pipeline:**
   - Leverage `core.utils.labels.resolve_labels`:
     `context["labels"] = resolve_labels(interface_type="landing_page_label", language=active_lang)`
   - Supply comprehensive bilingual label dictionary in `LandingPageView.get_context_data`:
     - Both `en` and `hi` variants available in the template.
2. **Template Markup Pattern:**
   ```jinja
   <span class="lang-text"
         data-en="{{ labels.hero_headline_en }}"
         data-hi="{{ labels.hero_headline_hi }}">
       {{ labels.hero_headline }}
   </span>
   ```
3. **Session & Cookie Handler:**
   - Small lightweight client script in `theme_override.js` / inline script manages cookie `loadshare_lang` and executes the text node swap.
   - On initial request, `LandingPageView` checks `request.COOKIES.get("loadshare_lang", "en")` and initializes `language`.

---

## 5. Input Source, Contracts & Error Handling

- **Inputs:**
  - Route booking parameters: Origin hub, Destination hub, estimated weight slab, dispatch date, 10-digit sender mobile number.
  - Language toggle state: `en` / `hi`.
- **Outputs:**
  - Fast server-rendered HTML payload (`GET /`).
  - OTP verification payload dispatched via existing endpoint `/api/users/v1/auth/otp/send/`.
- **Failure Modes & Fallbacks:**
  - Unauthenticated visitor &rarr; Landing page renders hero, route overview, rates, and embedded OTP entry form.
  - Authenticated visitor &rarr; Landing page renders personalized sender dashboard and instant booking panel.
  - Session timeout &rarr; Full-screen dialog overlay prompts re-login.
  - Network offline/telemetry drop &rarr; Interactive map toggle provides physical depot contact and 2G SMS dispatch instructions.

---

## 6. Verification & Testing Plan (Phase 4 Preview)

1. **Routing & View Tests:**
   - Test `LandingPageView` returns HTTP 200 with both `en` and `hi` cookie preferences.
   - Test language preference persistence via cookie.
2. **Template Structure & Token Verification:**
   - Verify `theme_override.css` is included in `<head>`.
   - Verify all 12 key sections (Hero, Schematic Manifest, How it Works, Corridor Telemetry, Rates, Trust Pillars, OTP Booking, FAQ, Pre-flight Drawer, Footer, Mobile Nav, Session Overlay) are present in the rendered HTML.
   - Verify no username/password login method switcher is leaked.
3. **Bilingual Attribute Assertion:**
   - Assert `.lang-text` nodes contain valid `data-en` and `data-hi` values without missing translations.
4. **Code Quality:**
   - Run `make t` (unit & integration tests).
   - Run `pre-commit` (`ruff`, `ruff-format`, `djlint`, `detect-secrets`).

---

## 7. Approval Checkpoint

> [!IMPORTANT]
> This analysis concludes **Phase 1 (Analysis)**.
> Awaiting user review and approval before proceeding to **Phase 2 (Implementation)**.
