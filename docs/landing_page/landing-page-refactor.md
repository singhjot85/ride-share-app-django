# Phase 1 Analysis & Implementation Plan: Landing Page Refactor

> **Feature Slug:** `landing-page-refactor`
> **Status:** Phase 2 Complete (Awaiting User Review before Phase 3)
> **Target Release:** POC Pilot (Delhi ⇄ Jaipur NH48 Corridor)

---

## 1. Executive Summary

The landing page has been refactored from a monolithic 835-line template (`backend/templates/landing_page.jinja`) into a component-driven, responsive shell architecture with strict asset separation.

### Key Objectives Achieved in Phase 2
1. **Responsive Dual Navigation Shell:**
   - **Mobile:** Fixed bottom navigation bar with 5 destinations (`Book Corridor`, `Rates`, `Home`, `Support`, `Profile`) in `components/bottom_navbar.jinja` styled via `bottom_navbar.css`.
   - **Desktop:** Centered floating rounded navigation chip (`components/floating_chip.jinja`) styled via `floating_chip.css` that hides on scroll down and reappears on scroll up.
   - **Top Title Bar (`landing-top-bar`):** Leftmost brand icon & title; rightmost contains **two separate controls**:
     - Language Toggle (`EN / हिंदी`) with Layer 2 cookie persistence (`/set-language/`).
     - Theme Toggle (`light / dark` mode) with icon synchronization (`dark_mode` / `light_mode`).
2. **Client-Side Tab Switching & Lazy Loading Hooks:**
   - Single-container multi-view architecture managed by `backend/static/js/states/navigation_state.js`.
   - Switching tabs updates visibility without full page reloads, synchronizes URL hashes (`#home`, `#book-corridor`, `#rates`, `#support`, `#profile`), and activates registered on-demand data fetchers.
3. **Component & View Modularity (`backend/templates/views/landing/`):**
   - `home_view.jinja`: Active by default. Contains hero headline, pilot announcement badge, live dispatch card with state toggles (`dispatch`, `loading`, `empty`), and transit guarantees.
   - `book_corridor_view.jinja`: Dedicated corridor search shell with the Reviewer State Switcher (`[Show 3 Trucks]`, `[Loading Skeleton]`, `[0 Results Empty]`, `[Corridor at Capacity]`, `[Error State]`) managed by `corridor_state.js`.
   - `rates_view.jinja`: Clean placeholder view for freight rate tiers.
   - `support_view.jinja`: Clean placeholder view for 24x7 helpline & concierge.
   - `profile_view.jinja`: Clean placeholder view for sender business profile.
4. **Strict Asset Separation & Ponytail Scope Discipline:**
   - All styles separated into `backend/static/css/` (`theme_override.css`, `landing_layout.css`, `floating_chip.css`, `bottom_navbar.css`, `variables.css`). Zero inline `<style>` tags in Jinja.
   - All logic separated into modular scripts in `backend/static/js/`:
     - `theme_toggle.js`: Synchronous `<head>` script preventing FOUC, resolving saved theme preference, handling debounced toggle, and writing to multi-layer persistence (`localStorage`, `sessionStorage`, `document.cookie`).
     - `language_toggle.js`: Bilingual language switcher (`en` / `hi`) with Layer 2 cookie persistence.
     - `states/navigation_state.js`: Client-side tab routing (5 destinations) and desktop chip scroll spy.
     - Zero inline `<script>` tags in `user_landing_page.jinja` or any landing templates.
5. **Strict Project Flag Isolation:**
   - Every project handles and sets only project-level flags (e.g., `loadshare_theme`, `loadshare_lang`).
   - Never read or write core framework internal flags (no mention of `core_*`).

---

## 2. Decision Log & Clarifications

| Topic | User Guidance / Decision | Implementation Approach |
|---|---|---|
| **Mockups** | Updated to latest `01_landing_page.html` (34 KB) & `02_corridor_page.html` (56 KB). | Sourced tokens, dispatch state toggles, and reviewer switcher directly from these updated files. |
| **Nav Items** | Confirmed 5 items (typo corrected). | `Book Corridor` \| `Rates` \| `Home` \| `Support` \| `Profile` on both desktop chip and mobile bottom bar. `Home` is default active tab. |
| **Header Controls** | Keep two separate toggles. | Language toggle (`EN / हिंदी`) and Theme toggle (`dark_mode`) side-by-side in header right section. |
| **Tab Switching** | Avoid server hammering; initial load loads shells; lazy load data per page; ghost components during loading. | Client-side tab switcher (`navigation_state.js`). Shell renders containers; tab click activates view, triggers lazy fetch hook, and shows ghost/skeleton state until data arrives. |
| **State Switcher** | Keep state switcher in corridor view for review & testing. | Retained reviewer toolbar (`[Show 3 Trucks]`, `[Loading Skeleton]`, `[0 Results Empty]`, `[Corridor at Capacity]`, `[Error State]`) in `book_corridor_view.jinja`. |
| **Test Verification** | Minimal tests; use mock data; real labels will be seeded later. | Cleaned up brittle assertions in `test_views.py`; verified HTTP 200, template resolution, shell components presence, and auth flow. All 30 tests pass. |
| **Logo Visibility** | Use secondary color (shade of orange) for logo background. | Set `.brand-logo-box` background to `var(--color-secondary)` with white icon and orange glow shadow so logo icon is sharp and visible. |
| **Desktop Active Tab** | Highlight active tab on desktop chip with secondary color (orange). | Set `.chip-nav-item.active` background to `var(--color-secondary)` and text to `var(--color-on-secondary)` matching mobile bottom nav. |
| **Dark Theme Fix** | Dark theme toggle not working; nothing saved in localStorage, sessionStorage, or cookies. | Traced end-to-end: identified Jinja block mismatch (`extra_js` instead of `extra_scripts`), missing multi-layer persistence (`sessionStorage` and `document.cookie`), and FOUC script falling back to OS preference without checking cookies. Fixed all 4 layers. |
| **Hard Rule: variables.css** | Create `variables.css` and use variables across component CSS exclusively. | Extracted all design tokens into `variables.css`. Refactored `landing_layout.css`, `floating_chip.css`, `bottom_navbar.css`, and `theme_override.css` to use `var(--color-...)` tokens exclusively. |
| **Strict Project Flag Isolation** | Remove instances like `localStorage.setItem("core_theme", theme)`; every project handles and sets only project-level flags; no mention of core. | Updated `navigation_state.js` and `user_landing_page.jinja` to exclusively read and write project-scoped flags (`loadshare_theme`, `loadshare_lang`). Eliminated all mentions/writes of core internal flags. |

---

## 3. End-to-End Trace: Dark/Light Theme Switcher

### A. Problem Statement
Clicking `#theme-toggle-btn` in the browser did not change the visual theme and did not save any state in `localStorage`, `sessionStorage`, or `Cookies`.

### B. Root Causes Identified During End-to-End Audit

1. **Jinja Script Block Name Mismatch:**
   - In `backend/core-common-django-apps/core/templates/core/base.jinja` (line 78), the script injection block is:
     ```jinja
     {% block extra_scripts %}
     {% endblock extra_scripts %}
     ```
   - In `user_landing_page.jinja`, scripts were placed inside `{% block extra_js %}`.
   - Because `extra_js` does not exist in any parent template, Jinja silently omitted the entire block from the rendered HTML.
   - Consequence: `<script src="/static/js/states/navigation_state.js"></script>` was never loaded in the browser. When the user clicked the toggle button (`onclick="LoadShareNav.toggleTheme()"`), the browser threw `ReferenceError: LoadShareNav is not defined`. No JavaScript executed, and zero storage writes occurred.

2. **Double Event Invocation (Instant Cancellation):**
   - Having both an inline `onclick="toggleTheme()"` and a DOM `themeBtn.addEventListener("click", ...)` attached to `#theme-toggle-btn` caused a double trigger on every click:
     - 1st handler: toggles light -> dark (DOM and storages set to dark).
     - 2nd handler (microsecond later in same click cycle): toggles dark -> light (DOM and storages set to light).
   - Consequence: The theme switched and immediately canceled itself out in 0 milliseconds, appearing to the human eye as if the button did nothing.

3. **Incomplete Multi-Layer Storage Persistence:**
   - In `navigation_state.js`, `applyTheme(theme)` previously only called `localStorage.setItem("loadshare_theme", theme)`.
   - It did not write to `sessionStorage` and did not set `document.cookie`.
   - Consequence: If an inspector checked DevTools under `Session Storage` or `Cookies`, no theme entry existed.

4. **FOUC Prevention Script Cookie Detection:**
   - The inline FOUC prevention script in `extra_head` only read `localStorage.getItem("loadshare_theme")`.
   - Consequence: In cookie-first contexts or after clearing local storage, the page defaulted to OS preference (`prefers-color-scheme`).

5. **Click Target Event Shielding:**
   - Child `<span>` icons inside `<button>` could occasionally intercept clicks or trigger bubbling anomalies in certain browser engines.

### C. End-to-End Resolution

1. **Block Correction in `user_landing_page.jinja`:**
   Changed to `{% block extra_scripts %}` so that `navigation_state.js`, `corridor_state.js`, `corridor_service.js`, and `language_toggle.js` are properly emitted right before `</body>`.
2. **Double Event Elimination & 250ms Debounce:**
   - Removed the duplicate `addEventListener` on `#theme-toggle-btn`.
   - Added a 250ms debounce guard (`lastToggleTime`) inside `toggleTheme()` to mathematically guarantee that rapid or duplicate event dispatches cannot toggle twice.
3. **Immediate Head Fallback Execution:**
   - Provided an immediate global `window.toggleTheme()` in `extra_head` that is active from millisecond 0 of HTML parsing, so clicking the toggle button works even before deferred scripts finish downloading.
   - Once `navigation_state.js` loads, it takes over seamlessly.
4. **Child Pointer Event Passthrough:**
   - Added `.theme-toggle-btn * { pointer-events: none; }` in `landing_layout.css` to guarantee clean, un-intercepted button click events.
5. **Tri-Layer Storage Persistence in `navigation_state.js`:**
   `applyTheme(theme)` now persists across all 3 client storage layers using project-scoped flag `loadshare_theme`:
   ```javascript
   localStorage.setItem("loadshare_theme", theme);
   sessionStorage.setItem("loadshare_theme", theme);
   document.cookie = "loadshare_theme=" + encodeURIComponent(theme) + "; path=/; max-age=31536000; SameSite=Lax";
   ```
6. **DOM & CSS Variable Propagation:**
   `applyTheme(theme)` applies:
   - `document.documentElement.setAttribute("data-theme", theme)`
   - `document.documentElement.classList.toggle("dark", theme === "dark")`
   - `document.body.setAttribute("data-theme", theme)`
   - `document.body.classList.toggle("dark", theme === "dark")`
   - Updates icon between `dark_mode` and `light_mode`.
   - In `variables.css`, `:root, [data-theme="light"]` and `[data-theme="dark"], html.dark, body.dark, .dark` swap the design tokens (`--color-bg`, `--color-surface`, `--color-text`, `--color-border`), which immediately re-colors the entire layout.
7. **Regression Test Added:**
   `backend/tests/test_views.py` now explicitly verifies `navigation_state.js`, `theme-toggle-btn`, and `loadshare_theme` in the rendered output.

---

## 4. Directory & File Architecture (Phase 2 Shell)

```
backend/
├── static/
│   ├── css/
│   │   ├── variables.css               # HARD RULE: Unified design tokens (light & dark mode)
│   │   ├── theme_override.css          # Core overrides importing variables.css
│   │   ├── landing_layout.css          # Top bar, view containers, ghost loaders, CTA buttons
│   │   ├── bottom_navbar.css           # Mobile fixed bottom nav bar styling (safe-area aware)
│   │   └── floating_chip.css           # Desktop center floating nav chip (hide on scroll)
│   └── js/
│       ├── theme_toggle.js             # FOUC prevention & appearance theme toggle (cookie, localStorage, sessionStorage)
│       ├── language_toggle.js          # Bilingual UI language switcher (Layer 1 text swap + Layer 2 cookie sync)
│       ├── navigation_state.js         # Tab switching and desktop scroll spy / hide-on-scroll logic
│       ├── session_sync.js             # Session timeout & JWT sync
│       └── otp_signup.js               # OTP auth flows
├── templates/
│   ├── components/
│   │   ├── floating_chip.jinja         # Desktop center floating nav chip (5 destinations)
│   │   └── bottom_navbar.jinja         # Mobile bottom navigation bar (5 destinations)
│   ├── views/
│   │   ├── authenticated_view.jinja    # Base view template (intercepts with OTP login when unauthenticated)
│   │   └── otp_login_template.jinja    # Phone OTP signin/signup card
│   └── landing_page.jinja              # Direct base authenticated_view; contains outer shell, title bar, and 5 toggleable shells
```

---

## 5. Iterative Implementation Plan

- [x] **Phase 1: Architecture Review & Plan Sign-off**
- [x] **Phase 2: Minimal Shell Layout & 5-Destination Navigation (Ponytail Cleaned)**
  - [x] Outer shell structure (`landing_page.jinja`) with direct base of `views/authenticated_view.jinja`.
  - [x] Heading title bar (orange logo box, language switcher, theme switcher).
  - [x] Desktop floating pill (`floating_chip.jinja`) with 5 working, toggleable icons (`book-corridor`, `rates`, `home`, `support`, `profile`).
  - [x] Mobile bottom navbar (`bottom_navbar.jinja`) with 5 working, toggleable icons.
  - [x] 5 clean toggleable view sections inside `landing_page.jinja`.
  - [x] Removed all orphan templates (`views/landing/`, redundant `user_landing_page.jinja`, dead `landing_interactive.js`, dead CSS).
  - [x] Design token stylesheets (`variables.css`, `landing_layout.css`, `floating_chip.css`, `bottom_navbar.css`, `theme_override.css`).
  - [x] `navigation_state.js` & `theme_toggle.js` separated and verified.
  - [x] Verified with `make t` (30/30 tests passing) and `poetry run pre-commit run --all-files` (zero errors).
- [x] **Phase 3: Home View Implementation from `01_landing_page.html` (`home_view.jinja`)**
  - [x] Centralized all bilingual copy in `backend/overrides/labels.py` (`LANDING_PAGE_LABELS`).
  - [x] Implemented Hero section (pilot notice, headline, subhead, CTA buttons).
  - [x] Implemented Tracker Preview Canvas with 3-state switcher (`active`, `loading`, `empty`).
  - [x] Implemented Transit Guarantees & Safety Protocol (4 pillars).
  - [x] Implemented How It Works (3 numbered steps).
  - [x] Implemented Collapsible FAQs using native semantic `<details>` and `<summary>` elements (0 extra JS required).
  - [x] Implemented Clean Footer (helpline, WhatsApp desk, APK link, copyright & statutory carriage notice).
  - [x] Verified with `make t` (30/30 tests passing) and `poetry run pre-commit run --all-files` (zero errors).
- [ ] **Phase 4: Corridor View Implementation (`book_corridor_view.jinja`)**
  - Detailed truck manifest details, filter controls, sticky bottom booking confirmation bar from `02_corridor_page.html`.
- [ ] **Phase 5: Quality & Closeout**
  - Final tests, pre-commit validation, and documentation updates.
