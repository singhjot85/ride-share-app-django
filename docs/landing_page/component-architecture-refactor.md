# Phase 1 Analysis: Modular UI Component Architecture Refactor

> **Feature Slug:** `component-architecture-refactor`
> **Target Release:** POC Modular Design System
> **Status:** Phase 1 Analysis (Pending User Approval)

---

## 1. Problem Statement & Motivation

Currently, the landing views (`home_view.jinja`, `book_corridor_view.jinja`, `profile_view.jinja`) mix UI layout with repetitive component logic:
- **Duplicated HTML:** Elements like accordions, multi-state cards, back-link context bars, and filter chips are written in full across multiple files. The 3-step corridor search wizard ("Find Instant Truck Space") alone spans ~310 lines of inline markup in `book_corridor_view.jinja`.
- **Monolithic CSS:** `backend/static/css/landing_layout.css` has grown to over 1,050 lines, intermixing generic component styles with page-specific overrides.
- **Scattered State JS:** State controllers (`corridor_state.js`, `profile_state.js`, `navigation_state.js`) manually manipulate DOM selectors, lacking standardized lifecycle hooks or component events.

### Target Architecture
A clean **Atomic Component Architecture**:
1. **Views as Layout Shells:** Views (`views/landing/*.jinja`) become clean layout orchestrators containing only structural positioning `<div>`s that invoke high-level components with 2–3 lines of code.
2. **Configurable Macros with Sensible Defaults:** Components reside in `backend/templates/components/<component_name>/<component_name>.jinja` (or `backend/templates/components/`) and provide declarative Jinja macros with robust default parameters.
3. **Encapsulated CSS & JS:** Each component has its own dedicated stylesheet (`<name>.css`) strictly using theme tokens from `variables.css`, and a dedicated client controller (`<name>.js`) handling internal state transitions.

---

## 2. Component Inventory & Extraction Candidates

| Component | Current Locations in Views | Purpose & Variants | Dedicated Assets |
|-----------|----------------------------|---------------------|------------------|
| **Carousel / Step Wizard** (`carousel`) | `book_corridor_view.jinja` (L107-418 "Find Instant Truck Space") | Multi-step progressive form or card carousel. Variants: `wizard` (step dots, validation, prev/next) and `card_slider`. | `components/carousel.jinja`<br>`css/components/carousel.css`<br>`js/components/carousel.js` |
| **Multi-State Card** (`state_card`) | `home_view.jinja` (Tracker canvas)<br>`book_corridor_view.jinja` (Truck results)<br>`profile_view.jinja` (Bookings list) | Container managing 5 standard states: `default`, `loading`/skeleton, `empty`, `error`, `capacity`. | `components/state_card.jinja`<br>`css/components/state_card.css`<br>`js/components/state_card.js` |
| **Accordion** (`accordion`) | `home_view.jinja` (FAQ list)<br>`book_corridor_view.jinja` (Route disclosures) | Collapsible content sections. Variants: single-open, multi-open, with custom icons. | `components/accordion.jinja`<br>`css/components/accordion.css`<br>`js/components/accordion.js` |
| **Filter Chips / Tab Group** (`filter_chips`) | `profile_view.jinja` (All/Active/Completed)<br>`book_corridor_view.jinja` (Reviewer switcher & Goods categories) | Interactive horizontal pill toggle group emitting selection change events. | `components/filter_chips.jinja`<br>`css/components/filter_chips.css`<br>`js/components/filter_chips.js` |
| **Context Header Bar** (`context_bar`) | `book_corridor_view.jinja` (L7-39)<br>`profile_view.jinja` (L10-33) | Subview header with back navigation link, status metadata badges, and quick action CTA. | `components/context_bar.jinja`<br>`css/components/context_bar.css` |
| **Sticky Action Bar** (`sticky_bar`) | `book_corridor_view.jinja` (L822-858) | Viewport-pinned bottom dock that reveals upon item selection. | `components/sticky_bar.jinja`<br>`css/components/sticky_bar.css`<br>`js/components/sticky_bar.js` |
| **Modal Dialog** (`modal`) | `profile_view.jinja` (Sign out dialog)<br>`landing_page.jinja` (Session timeout) | Accessible popover modal with backdrop blur, keyboard trap, and confirm/cancel actions. | `components/modal.jinja`<br>`css/components/modal.css`<br>`js/components/modal.js` |

---

## 3. Directory & Asset Structure

```
backend/
├── templates/
│   ├── components/
│   │   ├── carousel/
│   │   │   └── carousel.jinja             # Reusable carousel/wizard macro
│   │   ├── state_card/
│   │   │   └── state_card.jinja           # Multi-state card switcher macro
│   │   ├── accordion/
│   │   │   └── accordion.jinja            # Collapsible accordion macro
│   │   ├── filter_chips/
│   │   │   └── filter_chips.jinja         # Pill switcher macro
│   │   ├── context_bar/
│   │   │   └── context_bar.jinja          # Back-bar header macro
│   │   ├── modal/
│   │   │   └── modal.jinja                # Dialog modal macro
│   │   ├── floating_chip.jinja            # (Existing) Desktop nav chip
│   │   └── bottom_navbar.jinja            # (Existing) Mobile nav bar
│   └── views/landing/
│       ├── home_view.jinja                # Simplified layout shell
│       ├── book_corridor_view.jinja       # Simplified layout shell
│       └── profile_view.jinja             # Simplified layout shell
└── static/
    ├── css/
    │   ├── variables.css                  # Theme tokens (Single source of truth)
    │   ├── components/
    │   │   ├── carousel.css
    │   │   ├── state_card.css
    │   │   ├── accordion.css
    │   │   ├── filter_chips.css
    │   │   ├── context_bar.css
    │   │   └── modal.css
    │   └── landing_layout.css             # View-level grid & container placement ONLY
    └── js/
        └── components/
            ├── carousel.js
            ├── state_card.js
            ├── accordion.js
            ├── filter_chips.js
            └── modal.js
```

---

## 4. Phased Implementation Roadmap

### Phase 1: Planning & Specification (Current Step)
- Establish component inventory, directory conventions, and macro signatures.
- Obtain user approval on approach and component boundaries.

### Phase 2: Carousel / Wizard & State Cards
- Implement `components/carousel/` (`carousel.jinja`, `carousel.css`, `carousel.js`).
- Refactor the "Find Instant Truck Space" 3-step wizard in `book_corridor_view.jinja` from ~310 lines into a concise macro call (`{{ wizard(...) }}`).
- Implement `components/state_card/` (`state_card.jinja`, `state_card.css`, `state_card.js`) and wire into Tracker Preview and Truck Results.

### Phase 3: Accordion, Filter Chips & Context Bar
- Implement `components/accordion/` (`accordion.jinja`, `accordion.css`, `accordion.js`) and refactor FAQ in `home_view.jinja` and route info in `book_corridor_view.jinja`.
- Implement `components/filter_chips/` and replace manual chip loops in Profile and Corridor views.
- Implement `components/context_bar/` for consistent back navigation.

### Phase 4: Modal, Sticky Bar & Verification
- Implement `components/modal/` and `components/sticky_bar/`.
- Clean out orphaned CSS rules from `landing_layout.css`.
- Run comprehensive test suite (`make t`) and pre-commit checks (`poetry run pre-commit run --all-files`).
