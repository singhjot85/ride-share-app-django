# Users Application (`apps.users`)

The host-level `users` application extends the core framework authentication system with rideshare-specific identity attributes, role flags, and permission guards.

---

## 1. Architecture & Model Hierarchy

This app swaps the default `AUTH_USER_MODEL` (`core.apps.users.models.User`) while inheriting core's underlying domain logic directly:

```
apps.users.models.User
 └── core.apps.users.models_abstract.AbstractUser
      ├── django.contrib.auth.models.AbstractUser
      └── core.utils.models.BaseUserModel (UUID PK, timestamps, soft-delete, phone attributes)
```

### Models

| Model | Inherits From | Key Attributes & Responsibilities |
|---|---|---|
| `User` | `core_abstract.AbstractUser` | Swappable `AUTH_USER_MODEL`. Adds `is_driver` and `is_booker` role flags. |
| `SocialAccount` | `core_abstract.AbstractSocialAccount` | Swappable `USERS_SOCIAL_ACCOUNT_MODEL`. Links OAuth2 identity providers. |
| `OTPLog` | `core_abstract.AbstractOTPLog` | Swappable `USERS_OTP_LOG_MODEL`. Delivery lifecycle audit trail for SMS/email OTPs. |

---

## 2. Dynamic Model Getters

Always use the model getter functions exported from `apps.users` (or `core.apps.users`):

```python
from apps.users import get_user_model, get_social_account_model, get_otp_log_model

User = get_user_model()
SocialAccount = get_social_account_model()
OTPLog = get_otp_log_model()
```

---

## 3. Role Flags & Permissions

### Model Flags

- `is_driver` (`bool`, default: `False`): Designates whether the user is a registered vehicle driver.
- `is_booker` (`bool`, default: `False`): Designates whether the user is a parcel booker/sender.

### DRF Permissions (`apps.users.permissions`)

- **`IsAuthenticatedDriver`**:
  Enforces `request.user.is_authenticated and request.user.is_active and request.user.is_driver`.
- **`IsAuthenticatedBooker`**:
  Enforces `request.user.is_authenticated and request.user.is_active and request.user.is_booker`.

Usage in DRF viewsets:

```python
from rest_framework.viewsets import ModelViewSet
from apps.users.permissions import IsAuthenticatedDriver, IsAuthenticatedBooker

class DriverRouteViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedDriver]
    ...

class ParcelBookingViewSet(ModelViewSet):
    permission_classes = [IsAuthenticatedBooker]
    ...
```
