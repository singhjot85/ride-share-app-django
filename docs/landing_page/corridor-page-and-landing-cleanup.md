# Phase 1 Analysis: Dedicated Corridor Page Implementation, Landing Page Modularization & Label Border Normalization

> **Feature Slug:** `corridor-page-and-landing-cleanup`
> **Target Release:** POC Pilot (Delhi ⇄ Jaipur NH48 Corridor)

---

## 1. Executive Summary & Goals

This feature accomplishes three specific objectives:
1. **Dedicated Corridor Detail & Truck Booking Page:**
   - Implements a dedicated corridor view (`CorridorPageView`) at `/corridor/` matching the visual design, interactive wizard, live truck results, and state switches from `local_data/design/user-facing/corridor_page.html`.
   - Replaces the crude ("trash") embedded corridor mockup from the landing page with a streamlined corridor preview card pointing to the dedicated corridor page.
2. **Landing Page Modularization (`views/landing/`):**
   - Breaks down the monolithic 835-line `landing_page.jinja` template into focused, single-responsibility sub-views inside `backend/templates/views/landing/`:
     - `landing_page.jinja`: Main layout orchestrator.
     - `notice_bar.jinja`: Clean borderless pilot announcement.
     - `hero.jinja`: Hero banner and schematic waybill manifest.
     - `how_it_works.jinja`: 3-step point-to-point dispatch flow.
     - `corridor_preview.jinja`: NH48 Delhi ⇄ Jaipur linehaul overview card linking to `/corridor/`.
     - `pricing.jinja`: 3-tier freight pricing matrix.
     - `trust_compliance.jinja`: Trust pillars, KYC drivers, dual OTP handshakes.
     - `booking_gateway.jinja`: Quick OTP booking dispatch container.
     - `faq.jinja`: Operational & regulatory accordion.
     - `compliance_drawer.jinja`: FASTag and Motor Vehicles transit disclosures.
     - `mobile_nav.jinja`: Docked bottom navigation bar.
3. **Label & Notice Bar Border Normalization:**
   - Eliminates visible harsh borders on notice banners (such as `"PILOT PHASE: Commercial Senders Only on Delhi ⇄ Jaipur Corridor"`), badge pills, and inline status tags.
   - Aligns borders and shadows with the reference design tokens (`theme_override.css`), using subtle fills and zero 1px high-contrast borders on pill indicators.

---

## 2. Architecture & File Structure

```
backend/
├── config/
│   └── urls.py                               # Registers /corridor/ (name="ui-corridor")
├── overrides/
│   └── api/
│       └── views.py                          # Adds CorridorPageView & CORRIDOR_PAGE_LABELS
├── static/
│   ├── css/
│   │   └── theme_override.css                # Normalized borderless notice bars and badge styles
│   └── js/
│       ├── corridor_interactive.js           # Carousel wizard, state switcher, and truck selection
│       └── landing_interactive.js            # Landing page interactive behavior
├── templates/
│   ├── views/
│   │   ├── corridor_page.jinja               # Dedicated Corridor detail template
│   │   ├── otp_login_template.jinja          # Border-normalized notice banner
│   │   └── landing/
│   │       ├── landing_page.jinja            # Master landing layout orchestrator
│   │       ├── notice_bar.jinja              # Borderless pilot notice banner
│   │       ├── hero.jinja                    # Hero & waybill manifest
│   │       ├── how_it_works.jinja            # 3-step dispatch cards
│   │       ├── corridor_preview.jinja        # Delhi ⇄ Jaipur corridor preview & deep-dive link
│   │       ├── pricing.jinja                 # 3 wholesale freight tiers
│   │       ├── trust_compliance.jinja        # Trust cards & helpline
│   │       ├── booking_gateway.jinja         # OTP booking gateway
│   │       ├── faq.jinja                     # Operational FAQ
│   │       ├── compliance_drawer.jinja       # Pre-flight compliance audit drawer
│   │       └── mobile_nav.jinja              # Docked bottom mobile navigation
│   ├── corridor_page.jinja                   # Backward-compatible include/alias
│   └── landing_page.jinja                    # Backward-compatible include/alias
└── tests/
    ├── test_urls.py                          # Added tests for corridor URL reverse/resolve
    └── test_views.py                         # Added tests for CorridorPageView and modular landing
```

---

## 3. Verification Plan

1. Run filtered tests with `make tf TEST_FILTER=TestLandingPageView`.
2. Run new corridor tests with `make tf TEST_FILTER=TestCorridorPageView`.
3. Run full test suite with `make t`.
4. Validate pre-commit hooks via `poetry run pre-commit run --all-files`.
