# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Insights Forge is a multi-tenant, AI-powered business intelligence platform. This repo is the FastAPI backend. All commands below run from the `backend/` directory.

## Commands

```bash
# Environment
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Create .env from .env.example — DATABASE_URL and SECRET_KEY are required (no defaults).

# Run
uvicorn app.main:app --reload        # Swagger at http://127.0.0.1:8000/docs

# Migrations (Alembic autogenerates from app/db/base.py metadata)
alembic revision --autogenerate -m "message"
alembic upgrade head

# Tests
pytest                               # config in pyproject.toml (pythonpath=".", testpaths=["tests"])
pytest tests/unit/test_x.py::test_name   # single test

# Quality
black .          # line-length 88, py313
ruff check .     # line-length 88
mypy app         # untyped defs allowed; ignore_missing_imports
```

Requires Python 3.13.

## Architecture

Layered: **Service → API** (`app/api/v1/<resource>.py` routers, `app/services/*` logic, `app/schemas/*` Pydantic I/O). The full API + auth layer is implemented on top of the official Phase 0 schema.

### Frozen frontend contract (do not break)

`contract_reference.json.json` is the OpenAPI spec the React frontend is integrated against — **23 endpoints / 24 operations under `/api/v1/`**. Every path and request/response shape must match it exactly. After changing any endpoint, regenerate `openapi.json` (`app.openapi()`) and diff operation sets against the contract; the diff must show zero missing. Three **additional** auth endpoints exist beyond the contract (verify-email, forgot-password, reset-password) — additive only.

### Auth, RBAC & tenancy

- **JWT** ([app/core/security.py](app/core/security.py)): 15-min access token carrying `sub, org_id, role, workspace_id, sector`; refresh token (7d) persisted in `user_sessions` and rotated on refresh. Passwords hashed with the `bcrypt` library directly (not passlib — it breaks with bcrypt ≥4).
- **Current user / RBAC** ([app/api/deps.py](app/api/deps.py)): `get_current_user`, `require_roles("admin", ...)`, and `ensure_sector(current, sector)` which enforces that a path `{sector}` matches the caller's workspace.
- **Workspace == sector**: `workspaces.sector` (enum `Sector`: retail/service/education/agriculture) is the tenant's sector. Signup provisions org + admin/manager/user roles + default workspace + admin user. Sector endpoints resolve `{sector}` to the caller's workspace and filter by `workspace_id`.
- **Email verification** (Brevo, [app/services/email_service.py](app/services/email_service.py)): signup creates the user `is_verified=False` and emails a token; login is blocked (403) until verified. Password reset uses the same `email_tokens` table. Brevo key + sender in `.env`.
- **Error shape**: raised `HTTPException`/`AppError` → `{"error": {"code", "message"}}` ([app/core/errors.py](app/core/errors.py)); request-validation 422s intentionally keep FastAPI's `{"detail": [...]}` because the contract's `HTTPValidationError` is integrated against it.

### Contract-mapping notes

- `decision-cards` → `ai_recommendations` (extended with `title`, `decision_status`, `resolved_by/at`, `workspace_id`; source FKs relaxed to nullable).
- `records` (raw ingested rows, JSONB `data`) and `thresholds` are new tables. Ingestion parses CSV/JSON rows as-is (no cleaning/ML).
- `reports`: contract `report_type`/`status`/`download_url` live in `report_config` (the model's `report_type` is a fixed enum).

### Performance gotcha (important)

Every relationship in the official models is `lazy="selectin"`, so a naive entity load fires ~11 extra round-trips (seconds over Neon). All serialization reads only scalar columns, so read/lookup queries use `.options(lazyload("*"))` (or `db.get(..., options=[lazyload("*")])`) and write paths avoid `db.refresh()` (the session is `expire_on_commit=False`). Follow this pattern in new query code.

### Database layer (complete — treat as the source of truth)

- **`app/db/database.py`** — declarative `Base` with a global naming convention (`ix_`, `uq_`, `fk_`, `pk_`, `ck_`) for deterministic constraint names, and the SQLAlchemy engine.
- **`app/db/session.py`** — `SessionLocal` + `get_db()` FastAPI dependency (`autoflush=False`, `expire_on_commit=False`).
- **`app/db/base.py`** — imports every model so Alembic sees full metadata. **Any new model must be imported here or migrations will miss it.**
- **`app/models/`** — one file per table (~30 models across identity, workspace, dataset, analytics, dashboard, AI, forecast, report, notification, system, plus `record`, `threshold`, `email_token`).

> Note: the official models' cross-entity relationships had to be repaired (misindented / missing reverse sides) before the ORM would configure. When adding a relationship, verify `configure_mappers()` succeeds.

### Model conventions (follow these when adding models)

- Inherit `BaseModel` (`app/models/base.py`): UUID `id` (`uuid4` default), timezone-aware `created_at`/`updated_at`, and `is_deleted` flag.
- Business entities also mix in `AuditMixin` (`app/models/audit.py`): `created_by`, `updated_by` (FK → users), and `deleted_at`. Pattern: `class Foo(BaseModel, AuditMixin)`.
- UUID primary keys everywhere; PostgreSQL `Enum` (defined in `app/models/enums.py`) instead of VARCHAR; JSONB for flexible/config columns.
- Foreign keys are declared with explicit `index=True` on tenant/lookup columns.

### Multi-tenancy

Tenant-scoped tables carry `organization_id` (and often `workspace_id`) FKs. Preserve this scoping in all repository/query code as those layers are built.

## Working notes

- `backend/brain/` holds project-memory docs maintained across sessions. Check these for current intent before large changes.
- Config is centralized in `app/core/config.py` via pydantic-settings; access through the `settings` singleton, never `os.environ` directly.
- Redis + Celery are dependencies for async workers (`app/workers`), not yet implemented.
- `DEBUG=True` turns on SQL echo (very noisy); set `DEBUG=False` for test runs.
- The `venv/` was relocated, so console-script shebangs (`black`, `alembic`) may be stale — invoke tools via `./venv/bin/python -m <tool>`.

## Status

Phases 1–5 complete: env + official schema on Neon; workspace-as-sector; all 23 contract endpoints; email verification + password reset (Brevo); verified end-to-end on the live DB. `openapi.json` matches the contract (zero missing operations).
