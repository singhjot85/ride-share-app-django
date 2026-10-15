# LoadShare Backend

Django + Django REST Framework API that powers LoadShare: routes, parcel requests, matching, live tracking, notifications and payments.

## Tech Stack

- **Framework:** Django, Django REST Framework, GeoDjango
- **API schema:** drf-spectacular (OpenAPI)
- **Database:** PostgreSQL + PostGIS
- **Cache / latest driver location:** Redis
- **Async jobs:** Celery + Celery beat (Redis broker) - request expiry, notifications, receipts
- **Ops panel:** Django admin
- **Integrations:** OpenRouteService (HGV routing), MSG91 (SMS/OTP), FCM (push), Razorpay (test mode)

## Directory Structure

```
backend/
|- config/            # Project configuration
|   |- settings/      # Settings split into constants, variables, resolvers
|   |- urls.py        # All URL routing, registered at this level only
|   |- celery.py      # Celery app and beat schedule
|   |- wsgi.py
|- apps/              # Django apps (all application logic lives here)
|   |- accounts/      # Users, auth, OTP login
|   |- routes/        # Driver routes and capacity
|   |- parcels/       # Parcel requests and matching
|   |- tracking/      # Driver location updates
|   |- payments/      # Razorpay integration
|   |- notifications/ # SMS and push
|   |- services/      # External service clients (routing, SMS, push, payments)
|   |- utils/         # Shared helpers
|- requirements/
|- manage.py
```

> App names are indicative and may change as the POC evolves.

## Getting Started

```bash
cp .env.example .env
docker compose up --build          # API, Postgres/PostGIS, Redis, Celery, Celery beat
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

- API: `http://localhost:8000/api/`
- Django admin: `http://localhost:8000/admin/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

Run tests:

```bash
docker compose exec backend python manage.py test
```

## Coding Conventions

These are guidelines, not hard rules. Deviating is fine when the reason is clear.

**Plan new code in four phases:** analyse (inputs, outputs, thread and transaction context), write simple logic first, refactor into small reusable pieces (DRY, OOP), then test.

**General**
- Add type hints; use `typing.TYPE_CHECKING` for type-only imports.
- Validate missing and unexpected input at the start of a function, and raise early.
- Handle the common case first, complex cases last.
- Mock external API and I/O calls in tests; add end-to-end tests for each feature.

**Views**
- Use DRF viewsets; plain Django views only in rare cases.
- Views only handle the request and response. Business logic goes in a separate manager or service.
- Always return serialized data and enforce permissions on every endpoint.
- Never expose raw error messages; use custom errors.
- Paginate any list endpoint, and do not expose list endpoints that are not needed.

**URLs**
- Define all URLs at the project level, not per app.
- Register viewsets with a router; use raw URLs only for pre-resolved URLs (such as `admin.urls`) or function-based views.
- Use `DefaultRouter` only in non-production, so the API root view is not exposed in deployed environments.

**Settings**
- Keep all settings in `config/`; keep `settings.py` to definitions only.
- Constants go in `constants.py`, runtime-varying values in `variables.py`, resolution logic in `resolvers.py`.

## Async Tasks

Long-running or I/O-bound work (notifications, request expiry, receipts) runs in Celery workers, not in the request thread. Be clear about which thread your code runs in, and about transactions, before writing it.

## Documentation

- Data modeling: `docs/architecture/data-models.md`
- Asynchronous task system: `docs/architecture/async-system.md`