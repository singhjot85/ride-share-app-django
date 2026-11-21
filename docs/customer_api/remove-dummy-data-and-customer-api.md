# Analysis & Implementation Plan: Remove Dummy Data & Customer API Integration

## 1. Executive Summary & Goals
The goal of this task is to eliminate mock/dummy data across the LoadShare UI and integrate file-based label configuration with the existing CRM Customer API:
1. **File-Based Labels Configuration**:
   - Avoid keeping labels in the database altogether.
   - Maintain all bilingual UI copy and text labels (209 total keys including 32 core auth keys and 183 landing page labels) in dedicated JSON files under `backend/labels/`:
     - `backend/labels/en.json`: English translations.
     - `backend/labels/hi.json`: Hindi translations.
     - `backend/labels/users_template_label.json`: Multi-language mapping dictionary.
   - Update `BaseLanguageTemplateView` in `backend/overrides/api/views.py` to resolve labels directly from these JSON files, avoiding database lookups and cache overhead.
2. **CRM Customer API Integration**:
   - Utilize the core CRM customer endpoints at `/api/customers/v1/customers/<id>/` (`CustomerViewSet`) rather than a custom `customer-me` endpoint.
   - In `LandingPageView`, ensure the customer instance is provisioned and passed in context (`customer`), attaching `data-customer-id` in templates and a `customer_id` cookie.
   - Create `backend/static/js/customerService.js` to manage customer API requests via `GET /api/customers/v1/customers/<id>/`, data extraction (phone, email, name), profile DOM updates, and language preference resolution.
   - Clean up `profile_view.jinja` and `profile_state.js`: remove dummy mock consignments (RTW-7814-DEL, RTW-7902-JPR, RTW-6420-DEL), mock count badge (`3` -> `0`), mock simulation switcher ("Simulate empty"), and fake default fallbacks ("Sharma Logistics", "+91 98101 23456"). Add email display and input.
   - Wire the successful login flow to trigger `customerService.js` to fetch customer data, populate profile elements, and derive + apply language preference to the site.

---

## 2. Technical Specifications

### Input Source
- **Template Labels**: `backend/labels/en.json` and `backend/labels/hi.json` loaded directly from the filesystem.
- **Customer Data**: Authenticated `request.user` linking to `Customer` via `Customer.objects.get_or_create_for_user(request.user)`.
- **Customer Preferences**: Nested `CustomerPreference` records linked to `CustomerPreferenceType` (e.g. `code="language"`).

### Output Contract
- **Customer Endpoint**: `GET /api/customers/v1/customers/<customer_id>/`
  ```json
  {
    "id": "uuid",
    "first_name": "Rajesh",
    "last_name": "Kumar",
    "business_name": "Kumar Freight",
    "full_name": "Rajesh Kumar",
    "customer_type": "individual",
    "status": "onboarding",
    "phones": [
      {"id": "uuid", "phone": "+919876543210", "is_primary": true, "is_verified": true}
    ],
    "emails": [
      {"id": "uuid", "email": "rajesh@example.com", "is_primary": true, "is_verified": true}
    ],
    "preferences": [
      {"id": "uuid", "preference_code": "language", "value": "hi"}
    ]
  }
  ```
- **Language Preference Application**:
  If derived preference value is `"hi"` or `"en"`, calls `window.setLanguage(lang)`, which updates DOM text nodes immediately, sets `loadshare_lang` and `django_language` cookies, and syncs `/set-language/`.

### Caching Needs
- In-memory `lru_cache` for label JSON file reads. No database cache key management needed for labels.

### Async Needs
- Standard async HTTP requests via central `customerService.js`. No background Celery worker jobs needed for direct profile retrieval.

### DB Changes
- None. Labels do not touch database tables or seeders.

### Cron Needs
- None.

---

## 3. Booking Card Component Architecture
To preserve all card states while defaulting to a clean empty state in the profile view:
- Created `backend/templates/components/booking_card.jinja`:
  - `booking_card(...)`: Macro supporting multiple card states:
    - `in_transit` / `active`: Live pulse dot, `badge-status-transit`, truck icon, departure schedule.
    - `requested` / `pending`: `badge-status-requested`, calendar icon.
    - `delivered` / `completed`: `badge-status-delivered`, check_circle icon, delivery date.
    - `cancelled`: Cancel status badge.
  - `booking_empty_state(...)`: Macro rendering the empty consignment state container.
  - `booking_cards_container(...)`: Multi-state container macro supporting:
    - `active_state="empty"` (Default): Displays the empty state panel while keeping the cards list available.
    - `active_state="populated"`: Displays the cards list with active filter chips.
- In `backend/templates/views/landing/profile_view.jinja`:
  - Uses `{{ booking_cards_container(active_state="empty") }}` by default with count `0`.
  - Supports toggling between the empty state and populated state via `#toggle-empty-state-btn`.
- In `backend/static/js/states/profile_state.js`:
  - Updated `toggleEmptyState()` and `setBookingFilter(filter)` to work seamlessly with the multi-state container.
