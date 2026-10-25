# AGENTS.md — LoadShare Project Guide

Context and rules for AI agents and developers working on this codebase.

> **Project:** LoadShare — route-based logistics connecting heavy-vehicle drivers with parcel senders across India.
> **Status:** POC. Keep scope tight; do not build for scale not yet needed.

---

## 1. Repository Layout

```
loadshare/
├── backend/                    # Django + DRF API, Celery workers
│   ├── config/                 # Django settings, URL root, WSGI/ASGI
│   ├── core-common-django-apps/ # Git submodule — shared core framework (read-only conventions)
│   ├── tests/                  # Project-level integration tests
│   ├── manage.py
│   └── pyproject.toml
├── frontend/                   # React + TypeScript (Vite) sender web app
├── compose/                    # Docker Compose files (local/, production/)
├── docs/                       # Architecture, data modeling, API reference
└── Makefile                    # All dev commands — always use make targets
```

**Key constraint:** `backend/core-common-django-apps/` is a git submodule. Never modify files inside it directly. Extend or override in the host project.

---

## 2. Hard Rules

These are non-negotiable. Violating them breaks the project or the submodule contract.

| # | Rule |
|---|------|
| 1 | **Never** modify files inside `backend/core-common-django-apps/`. It is a submodule. |
| 2 | **Never** import concrete models directly. Use the model getters from the app's `__init__.py`. |
| 3 | **Never** call Celery `.delay()` / `.apply_async()` directly. Use `queue_task()`. |
| 4 | **Never** run blocking I/O (HTTP, SMS, email) on the Django request thread. Queue it. |
| 5 | **Never** log secrets or PII. Route sensitive data through `ContentMaskingUtils`. |
| 6 | **Never** use `fields = "__all__"` on mutable DRF serializers. Always declare explicit fields. |
| 7 | **Never** run `pytest`, `poetry`, or `docker` commands directly. Use `make` targets only. |
| 8 | **Never** bypass pre-commit hooks (`--no-verify`). Fix the cause. |
| 9 | **Never** delete or re-create the test database yourself. Report stale migrations and wait. |
| 10 | **Never** add scope beyond what the task asks for. |

---

## 3. Tech Stack at a Glance

| Layer | Choice |
|---|---|
| Backend | Django, DRF, GeoDjango |
| Background jobs | Celery + Celery Beat (Redis broker) |
| Database | PostgreSQL + PostGIS |
| Cache / live location | Redis |
| Sender web | React + TypeScript (Vite) |
| Driver app | Native Android (Kotlin, Jetpack Compose) |
| Ops panel | Django Admin |
| Maps / Routing | Leaflet / MapLibre + OpenRouteService (HGV) |
| Push / SMS / Payments | FCM / MSG91 / Razorpay (test mode) |
| Deployment | Docker Compose on EC2 (ap-south-1) |

**Out of scope for POC:** Kubernetes, Kafka, WebSockets, third-party KYC, escrow/payouts, ratings, iOS, ML/DL.

---

## 4. Development Workflow

### Step 0: Triage first

| Track | When to use |
|---|---|
| **Bug-Fix Flow** | Wrong behavior; fix stays within existing models, tasks, and interfaces |
| **Four-Phase Lifecycle** | New feature, model/task/cron change, behavior change, or multi-file refactor |

**Escalate to Four-Phase if any of these are true:**
- Needs a new or changed model, migration, task, cron, or setting.
- Changes a public API contract, serializer fields, or interface signature.
- Root cause is a design flaw or has trade-off options.
- Spans more than one app or more than ~3 files.

If you cannot reproduce the bug after a reasonable attempt, stop and report what you found. Do not guess-fix.

---

### Bug-Fix Flow

1. **Reproduce** — write a failing regression test first. The test proves the bug and later proves the fix.
2. **Locate** — grep every caller of the function you will touch. Read only the relevant lines.
3. **Fix the root cause once** — in the shared code, not at the symptom. No drive-by refactors.
4. **Verify** — new test passes. Run `make tf TEST_FILTER=<expr>`, then `make t DIR=<app>`.
5. **Close out** — run `poetry run pre-commit run --all-files`. Update `Readme.md` only if documented behavior changed.
6. **Report** — root cause, the fix, the test added, what you did not check, and anything noticed but left alone.

---

### Four-Phase Lifecycle

Do not start a phase before the previous one is finished and approved.

#### Phase 1 — Analysis (What)

- Create `docs/analysis/<feature-slug>.md` before analyzing. Edit it in place; do not append.
- Answer for the feature: input source, output contract, caching needs, async needs, DB changes, cron needs.
- For new models: what queries will run? What is the data volume per table?
- For errors: raise, roll back, or log? Retry strategy and exhaustion behavior?
- Thread/process awareness: HTTP thread stays lightweight. Celery workers handle heavy work. Pass schema name explicitly to tasks in multi-tenant contexts. Plan `transaction.atomic()` blocks; dispatch side effects only after commit via `queue_task`.
- **Stop and wait for user approval before starting Phase 2.**

#### Phase 2 — Implementation (How)

- Start only after Phase 1 is approved. If a requirement is unclear, go back to Phase 1 — do not guess.
- Fail fast: validate inputs at the top of each function; raise early.
- Query discipline: avoid N+1 queries; use `select_related` / `prefetch_related`; use `bulk_create` / `bulk_update` for batch writes.
- Side effects: dispatch via `queue_task`. Pass IDs, never model instances. Pass schema name in multi-tenant calls.
- Logging: log failures with IDs and context. Never log PII or secrets.

#### Phase 3 — Refactor

- Refactor only after the logic works. Run tests before and after; behavior must not change.
- Single-responsibility functions. If a function needs "and" to describe it, split it.
- DRY: fix the root cause once in shared code. Find every caller before touching shared code.
- No premature abstractions. Extract a helper at the third real occurrence, not before.
- Keep the public interface (signatures, API contracts) stable unless the approved plan says otherwise.

#### Phase 4 — Testing & Quality

- Mock only external APIs and I/O boundaries (HTTP, file storage, email/SMS). Never mock the ORM or internal helpers.
- Create real model instances with factories. If no factory exists, create one.
- Celery tasks: run eagerly in tests (`CELERY_TASK_ALWAYS_EAGER`). Mock only when the task calls an external API.
- Cover: happy path, each invalid-data case (assert the exact exception), post-commit side effects.
- Name tests for behavior: `test_raises_when_route_has_no_capacity`, not `test_route`.
- Stale migration or test DB issues: stop and report — never fix it yourself.
- Run `poetry run pre-commit run --all-files` before finishing. All hooks must pass with zero errors.

---

## 5. Make Targets (always use these)

```bash
make t                          # Run all tests
make t DIR=<path>               # Run tests in one directory
make tf TEST_FILTER=<expr>      # Run filtered tests
make dev-setup                  # Full local dev setup
```

Never run `pytest`, `poetry run pytest`, or `docker compose exec ... pytest` directly.

---

## 6. Backend Conventions

These extend the core submodule's conventions for this host project.

### Models
- All fields and business logic live in abstract models (`models_abstract.py`). Concrete models subclass them and add nothing new.
- Use `BaseModel` (UUID PK, timestamps, soft delete), `BaseLogModel` (event/audit), `BaseVersioningModel` (versioned config) from `core.utils.models`.
- `.delete()` is soft by default (`is_removed=True`). Hard delete requires `soft=False`.
- ForeignKeys reference models by settings string (`to=settings.AUTH_USER_MODEL`), never by concrete class.

### Serializers & Views
- Views are thin dispatchers. Business logic lives in managers and services.
- Explicit `fields` and `read_only_fields` on every serializer.
- Query `.available_objects` (not `.objects`) for soft-deletable models.
- Async state changes return `HTTP_202_ACCEPTED` immediately.

### Async Tasks
- Always use `queue_task()`. Keep `on_commit=True` (default). Pass an `idempotency_key`.
- Never pass model instances to tasks — pass IDs or serialized primitives.

### Settings
- App-specific settings go in `app_settings.py` as descriptors on a `BaseSettings` subclass.
- Instantiate the singleton in the app's `__init__.py` only.

---

## 7. Frontend Conventions (React + TypeScript)

- Locate code in `frontend/`.
- Follow the conventions in [`frontend/Readme.md`](frontend/Readme.md).
- Keep components small and single-purpose.
- No inline styles; use the project's CSS/design token system.
- API calls go through a central API client — never scatter `fetch`/`axios` calls across components.
- Prefer native browser APIs and installed dependencies over adding new ones.

---

## 8. Documentation

- Keep `Readme.md` files in sync with code changes.
- New model, setting, endpoint, or task → update the app's `Readme.md`.
- Bug fix or refactor → update docs only if the documented behavior changed.
- Style: short and crisp. No large code dumps. Minimal snippets only for non-obvious patterns.
- Analysis logs go in `docs/analysis/<feature-slug>.md`.

---

## 9. Ponytail (lazy senior dev mode)

You are a lazy senior developer. The best code is the code never written. Solve the whole problem with the least new code.

**Before you write:** read the task and the code it touches. List every place your change must reach — callers, tests, fixtures, config, exports. That is scope. Extra features are not.

**The smallest complete change:**
1. Does it need to exist? If not, skip it and say so.
2. Already in this codebase? Use it.
3. Standard library or platform feature? Use it.
4. An installed dependency? Use it. Never add a dependency for a few lines.
5. Can it be one readable line? One line.
6. Otherwise: the minimum code that works.

- Be lazy about the solution, never about the change itself — finish everything the task needs.
- No abstraction, boilerplate, or "for later" code nobody asked for. Deletion beats addition.
- A shortcut with a known limit: `shortcut: <the limit>, <when to upgrade>`.
- End every reply with one or two lines: what you skipped or did not check, and any risk the user must know.

**Never cut:** validation at trust boundaries, error handling that prevents data loss, security, or anything the user asked for.
