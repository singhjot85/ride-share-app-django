# Phase 1 Analysis: Users App Host-Repo Model Swap & Permissions

## 1. Overview & Objectives

The goal is to provide a host-specific Users app (`apps.users`) in `ride-share-app-django` that:
1. Swaps the current concrete user model (`core.apps.users.models.User`).
2. Subclasses `core.apps.users.models_abstract.AbstractUser` as the base abstract model.
3. Adds two role flags: `is_driver` (boolean, default=False) and `is_booker` (boolean, default=False).
4. Creates two DRF permissions derived from those flags (`IsDriver`, `IsBooker`) that enforce authentication and role membership.
5. Preserves compatibility with existing database tables (`users_user`), migration history (`users 0001_initial`), dynamic model getters (`get_user_model()`), foreign key swappable references, and core auth/OTP flows.

---

## 2. Technical Analysis

### A. Input Source
- **Model Fields**:
  - `is_driver`: `models.BooleanField(_("Is Driver"), default=False, help_text=_("Designates whether the user is a registered vehicle driver."))`
  - `is_booker`: `models.BooleanField(_("Is Booker"), default=False, help_text=_("Designates whether the user is a parcel booker/sender."))`
- **Inherited from Core `AbstractUser`**:
  - Django's `AbstractUser` fields: `username`, `email`, `password`, `first_name`, `last_name`, `is_active`, `is_staff`, `is_superuser`, `date_joined`, `groups`, `user_permissions`.
  - Core's `BaseUserModel` fields: UUID primary key `id`, `created`, `modified`, `is_removed`, `removed_by`, `phone_number`, `is_phone_verified`, `is_email_verified`.
- **Permission Inputs**:
  - `request.user`: Must be authenticated (`is_authenticated=True`) and active (`is_active=True`).
  - Flag evaluation: `getattr(user, "is_driver", False)` and `getattr(user, "is_booker", False)`.

### B. Output Contract
- **Model Class**:
  - `apps.users.models.User` (inheriting from `apps.users.models_abstract.AbstractUser`).
  - `get_user_model()` dynamically returns `apps.users.models.User`.
  - `AUTH_USER_MODEL = "users.User"`.
- **Permissions**:
  - `apps.users.permissions.IsDriver(BasePermission)`:
    - `has_permission(self, request, view) -> bool`: Returns `True` iff `request.user.is_authenticated and request.user.is_driver`.
  - `apps.users.permissions.IsBooker(BasePermission)`:
    - `has_permission(self, request, view) -> bool`: Returns `True` iff `request.user.is_authenticated and request.user.is_booker`.
  - Aliases provided: `IsAuthenticatedDriver = IsDriver`, `IsAuthenticatedBooker = IsBooker`.

### C. Caching Needs
- No dedicated cache layer needed for the boolean flags on `User`.
- Django auth session / SimpleJWT access tokens store user ID; permissions check user attributes directly from the database query or cached user instance attached to `request.user`.

### D. Async / Celery Needs
- None for model definition and permission checks.
- Any background task interacting with users will continue to pass user IDs (`uuid.UUID`), resolving with `get_user_model().objects.get(id=user_id)`.

### E. Database Schema & Migration Strategy
- **Existing State**:
  - `db_migrations/users/0001_initial.py` is applied on the database.
  - Table `users_user` exists with all baseline core columns.
  - Foreign keys in `crm`, `tenants`, `invoices`, `integrations`, and `token_blacklist` have `swappable_dependency(settings.AUTH_USER_MODEL)` targeting `users.0001_initial`.
- **App Classification & Labeling**:
  - App module: `apps.users` located at `backend/apps/users`.
  - AppConfig: `name = "apps.users"`, `label = "users"`.
  - Setting `USERS_APP = "apps.users"` replaces `"core.apps.users"` in `PROJECT_APPS`, `INSTALLED_APPS`, `DJANGO_TENANT_PUBLIC_APPS`, and `DJANGO_TENANT_PRIVATE_APPS`.
  - App label remains `"users"` so `AUTH_USER_MODEL = "users.User"` and `MIGRATION_MODULES["users"] = "db_migrations.users"` are 100% continuous without renaming tables or breaking migration graphs.
- **Migration Plan**:
  - Run `make mm APP_LABEL=users` to generate `db_migrations/users/0002_user_is_booker_user_is_driver.py`.
  - The migration adds `is_driver` and `is_booker` (both with `default=False`) to the existing `users_user` table.
  - Run `make m` to apply.

### F. Query Performance
- `is_driver` and `is_booker` are standard boolean fields stored directly on the `users_user` table.
- Reading `user.is_driver` or `user.is_booker` requires zero additional joins or queries beyond loading the authenticated user.
- If frequently filtered together with `is_active` in driver discovery queries (e.g., finding active drivers), an index can be considered in the future (`shortcut: no index on boolean flags yet; add composite index when driver route queries are introduced`).

### G. Error Handling & Edge Cases
- Anonymous user checking permissions: `request.user.is_authenticated` is False -> permission denied (HTTP 401 Unauthorized for unauthenticated, HTTP 403 Forbidden for authenticated non-matching role).
- Inactive user (`is_active=False`): Handled by Django auth; permissions also check `is_active`.
- Soft-deleted user (`is_removed=True`): Filtered out by `UserManager.available_objects`.
- System user: `is_driver=False`, `is_booker=False`.

---

## 3. Architecture & File Layout

```
backend/
├── apps/
│   └── users/
│       ├── __init__.py          # Exports get_user_model, get_social_account_model, get_otp_log_model, etc.
│       ├── apps.py              # UsersConfig (name="apps.users", label="users")
│       ├── models_abstract.py   # AbstractUser with is_driver, is_booker
│       ├── models.py            # User, SocialAccount, OTPLog concrete swappable shells
│       ├── permissions.py       # IsDriver, IsBooker permission classes
│       ├── admin.py             # UserAdmin extending UserAdmin with is_driver, is_booker fieldsets
│       └── Readme.md            # App-level human documentation
├── config/
│   └── settings/
│       └── base.py              # Update USERS_APP = "apps.users"
├── db_migrations/
│   └── users/
│       └── 0002_user_is_booker_user_is_driver.py # Generated migration
└── tests/
    └── test_users.py            # Unit & integration tests for model & permissions
```

---

## 4. Open Questions & Recommendations

1. **App Placement & Label**:
   - *Option A (Recommended)*: Locate at `backend/apps/users/` with `name = "apps.users"` and `label = "users"`. Replace `"core.apps.users"` with `"apps.users"` in `USERS_APP`.
     - *Why*: Keeps the app label `"users"`, preserving seamless compatibility with `AUTH_USER_MODEL = "users.User"`, existing `db_migrations/users/0001_initial.py`, and all 5 foreign-key dependencies (`crm`, `tenants`, `invoices`, etc.).
   - *Option B*: Locate at `backend/apps/users/` with a different label like `label = "rideshare_users"`.
     - *Why not*: Would break existing applied migration history in PostgreSQL and require complex migration dependency repairs.

2. **Model Getter & Companion Models**:
   - *Recommendation*: The host `apps/users/models.py` will subclass `AbstractUser` from core for `User`, and thin-subclass `AbstractSocialAccount` and `AbstractOTPLog` for `SocialAccount` and `OTPLog` so that all three swappable models remain unified under the host app without losing core's social and OTP login functionality.

3. **Permission Behavior**:
   - *Recommendation*: `IsDriver` and `IsBooker` derive from `rest_framework.permissions.BasePermission`, checking:
     `bool(request.user and request.user.is_authenticated and getattr(request.user, "is_driver", False))`
     and
     `bool(request.user and request.user.is_authenticated and getattr(request.user, "is_booker", False))`.
   - Also check `request.user.is_active`.
