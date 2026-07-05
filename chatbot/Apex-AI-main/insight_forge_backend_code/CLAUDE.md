# CLAUDE.md

Context for Claude Code. Read this before doing any work in this repo.

## Project

DecisIQ — an AI Decision Intelligence Platform. A multi-tenant, multi-sector platform that ingests a company's raw data, cleans it, and turns it into dashboards, forecasts, alerts, and AI-recommended actions. Version 1 supports four sectors: **Retail, Service, Education, Agriculture**.

**This repository is the backend / API service only.**

## My role — and what is NOT my job

I am the **Security & API Engineering Specialist**. This repo covers:
- Authentication (JWT + refresh tokens, Argon2 password hashing, role-based access)
- REST + WebSocket API endpoints
- Multi-tenant data isolation (PostgreSQL Row-Level Security)
- The file-upload (ingestion) endpoint that receives raw data and hands it off

**Explicitly NOT my job — do NOT build these in this repo:**
- **Data cleaning / ML logic** (missing-value imputation, outlier detection, forecasting, KNN, Isolation Forest). That belongs to the Data Analyst. This backend only *receives* the raw file, *stores* it, and *triggers* the cleaning job — it never processes the data itself. Do not add pandas/scikit-learn cleaning code here.
- **Frontend** (React / Vite / any UI). A separate developer owns that in a separate repo. This backend only serves JSON over HTTP; it renders nothing.

If a task drifts into cleaning logic or frontend, stop and flag it instead of building it.

## Tech stack

- **Language:** Python 3.13
- **Framework:** FastAPI + Uvicorn
- **Auth:** PyJWT (15-min access token + refresh token), passlib[argon2] for password hashing, RBAC roles: `admin` / `manager` / `user`
- **Database:** PostgreSQL 16 (Neon) via SQLAlchemy, multi-tenant with Row-Level Security keyed on `organization_id`
- **DB driver:** psycopg 3
- **File storage:** S3 / MinIO via boto3
- **Config:** pydantic-settings (reads from `.env`)
- **Chatbot endpoint:** OpenAI (or Anthropic) API, called server-side
- **Testing:** pytest + httpx

**Out of scope for this MVP — do NOT add these.** The official specs mention them, but they are over-engineered for this build and are deferred: Celery, Redis, Kubernetes, Nginx ingress, TLS termination, self-hosted LLMs (vLLM/Llama). For background work, use FastAPI `BackgroundTasks`, not Celery. Also: `requirements.txt` should not include pandas / openpyxl / scikit-learn — those belong to the Data Analyst, not this repo.

## Commands

```bash
source venv/bin/activate          # run in every new terminal; prompt should show (venv), not (base)
pip install -r requirements.txt   # install dependencies
uvicorn app.main:app --reload     # run dev server at http://localhost:8000
pytest                            # run tests
```

Auto-generated interactive API docs: open `http://localhost:8000/docs` after the server starts. This doubles as the live API contract to share with the frontend developer.

Note: this machine has Anaconda installed. Always confirm `(venv)` is active (not `(base)`) so packages stay isolated to this project.

## Project structure

```
backend/
├── app/
│   ├── main.py            # FastAPI app entry point; mounts routers
│   ├── config.py          # settings loaded from .env
│   ├── database.py        # DB engine/session + org context (set_config app.current_organization_id)
│   ├── auth/
│   │   ├── jwt_handler.py  # create/verify JWTs; extract organization + role + sector (FastAPI dependency)
│   │   └── security.py     # Argon2 password hashing/verification
│   ├── routes/
│   │   ├── auth.py         # /auth/signup, /login, /refresh, /logout
│   │   ├── ingestion.py    # /ingestion/stream — streaming upload to S3, triggers cleaning
│   │   ├── datasets.py     # /datasets, /datasets/{id}
│   │   ├── sectors.py      # /sectors/{sector}/scorecard, /timeseries, /records, /records/{id}
│   │   ├── decisions.py    # /decision-cards, approve, reject
│   │   └── chat.py         # /chat/stream (WebSocket)
│   ├── models.py          # SQLAlchemy table models
│   └── schemas.py         # Pydantic request/response models
├── database/
│   └── rls_policies.sql   # RLS policies on data tables, keyed on organization_id (written; apply manually)
├── tests/
│   └── test_smoke.py      # full-surface smoke test (runs against DATABASE_URL)
├── seed_demo.py           # insert TEMPORARY demo rows (is_demo=true) across all 4 sectors
├── clear_demo.py          # delete ONLY is_demo=true rows (never real data)
├── .env                   # secrets — NEVER commit
├── .gitignore             # must include .env and venv/
└── requirements.txt
```

## Demo / seed data

There is no real cleaned data during development, so `seed_demo.py` inserts sample
rows for the `/sectors/{sector}/*` endpoints. Rules:

- Every table that can hold demo rows (`organizations`, `users`, `datasets`,
  `records`, `decision_cards`) has an **`is_demo BOOLEAN NOT NULL DEFAULT false`**
  column. Real rows are always `is_demo = false`.
- `python seed_demo.py` creates one demo org + one demo user per sector (+ datasets,
  records, decision cards), all `is_demo = true`. Demo user login:
  `demo-<sector>@demo-decisiq.com` / `demo-pass-123`.
- `python clear_demo.py` deletes **only** `is_demo = true` rows (and demo users'
  sessions) — never a full-table delete. It self-verifies 0 demo rows remain.
- **Never leave demo data in the DB.** Seed → verify → `clear_demo.py` immediately.

## Conventions & rules

- **Versioned routes:** every endpoint lives under `/api/v1/...`.
- **Auth on every data route:** protected routes require a valid JWT. Extract `organization_id`, `user_id`, `role`, and `sector` from the token via a shared FastAPI dependency in `jwt_handler`.
- **Organization isolation is mandatory:** before any org-scoped query, set the context with `SELECT set_config('app.current_organization_id', '<org-uuid>', true)` (via `set_organization_context`). Do **not** use `SET LOCAL <name> = :param` — Postgres' SET does not accept bound parameters. PostgreSQL RLS enforces that an organization only sees its own rows. Never rely on application-side filtering alone.
- **Sector is a path parameter, not separate endpoints.** One `/sectors/{sector}/scorecard` serves all four sectors; the handler switches logic (not tables — see Data model) on `{sector}`. Do not create four copies of each endpoint. A user is fixed to one sector (carried in the JWT); validate the requested sector matches the caller's.
- **Chart endpoints return frontend-ready JSON**, e.g. `{ "labels": [...], "series": [{ "name": "...", "values": [...] }] }`. Do not return raw DB rows for charts.
- **Standard error shape** on every endpoint: `{ "error": { "code": "...", "message": "..." } }` with a correct HTTP status. The frontend depends on this for its error states.
- **Secrets live in `.env`** (DB URL, JWT secret, S3 keys, LLM key), read via `config.py`. Never hardcode secrets. `.env` is git-ignored.
- **Passwords** are hashed with Argon2 — never stored in plain text.

## RBAC (roles)

- `user` — read-only: dashboards, records, chatbot.
- `manager` — user + approve/reject decision cards, threshold config, reports.
- `admin` — manager + manage users, datasets, and org settings.

## Endpoints to build (v1), in priority order

Build the vertical slice top-to-bottom first:

1. `POST /api/v1/auth/login`, `/refresh`, `/logout` (and `/signup`)
2. `POST /api/v1/ingestion/stream` — multipart streaming upload to the S3 landing bucket, trigger the cleaning job, return a `dataset_id`
3. `GET /api/v1/datasets`, `GET /api/v1/datasets/{id}` (status + health score)
4. `GET /api/v1/sectors/{sector}/scorecard`, `/timeseries`, `/records`, `/records/{id}`
5. `GET /api/v1/decision-cards`, `POST /api/v1/decision-cards/{id}/approve`, `/reject`
6. `WS /api/v1/chat/stream`

Deferred until the above works: geo, what-if simulator, reports, KPI thresholds, user management.

## Data flow (how a request travels)

1. User logs in → receives a JWT holding `organization_id`, `user_id`, `role`, and `sector` (a user is fixed to one sector).
2. Frontend sends the JWT on every request; the sector rides inside the token, so no re-lookup is needed.
3. This API verifies the JWT, sets the organization context, and runs the query under RLS.
4. For uploads: the file streams in ~1 MB chunks to S3. This API does **not** parse or clean it — it stores the file and triggers the separate cleaning worker, which writes clean rows into the generic `datasets` structure tagged with the `sector`.
5. Dashboard endpoints read the cleaned rows (filtered by `sector`) and return frontend-ready JSON.

## Data model (decided — the ER diagram is the source of truth, but ONLY Module 1 + `datasets`)

- **Generic model, NOT sector-specific tables.** Do not create `retail_transactions`, `service_tickets`, etc. All sector data lives in the generic `datasets` structure, distinguished by a `sector` field. Ignore all other ER modules (workspaces, dashboards, forecasting, reports, notifications, …) — do not build them.
- **Table names align to the ER diagram:** `organizations` (was `tenants`), `users`, `user_sessions` (was `refresh_tokens` — same jti/refresh-token mechanism, just renamed), `datasets`. `organization_id` replaces `tenant_id` everywhere (models, JWT, RLS, `set_config`).
- **`sector` lives on `users`** (retail / service / education / agriculture) and on `datasets`, and is embedded in the JWT. One user = one sector for now; don't build multi-sector switching.
- **In scope right now:** only the auth tables (`organizations`, `users`, `user_sessions`) + `datasets`. Nothing else yet.

## Current status

- Dependencies installed, venv set up. `DATABASE_URL` points at Neon (postgres, `+psycopg` driver).
- **HTTP endpoints built and passing against Neon:** auth (signup/login/refresh/logout), ingestion (`/ingestion/stream`), datasets, sector dashboards (`/sectors/{sector}/scorecard|timeseries|records|records/{id}|geo`), decision-cards (list + status filter / approve / reject), what-if (`POST /simulate`), reports (`POST /reports/compile`, `GET /reports/{id}`), KPI thresholds (`GET /thresholds`, `PUT /thresholds/{id}`), user management (`GET/POST/DELETE /users`).
- Tables: `organizations`, `users`, `user_sessions`, `datasets`, `records` (generic JSONB — cleaned rows), `decision_cards`, `reports`, `kpi_thresholds`.
  - `POST /simulate` is in-memory only (no DB writes) — deterministic arithmetic projection, not ML.
  - `POST /reports/compile` runs async via `BackgroundTasks` (no Celery): returns a `pending` report id, background job sets `ready` + `download_url`.
  - `/sectors/{sector}/geo` returns a GeoJSON FeatureCollection built from records whose `data` JSONB carries lat/lng.
  - `/thresholds` PUT and all `/users` routes are RBAC-gated (thresholds edit = manager/admin; users = admin). New users always inherit the caller's `organization_id`.
  - `decision_cards` columns: `id, organization_id, sector, title, recommendation, confidence_score, status(pending|approved|rejected), resolved_by, resolved_at, is_demo, created_at`. Approve/reject sets `status` + `resolved_by` (user id) + `resolved_at`.
- **Chat (`WS /api/v1/chat/stream`)** is mounted and works, but is owned by another developer and there is **no `LLM_API_KEY` yet** — it currently streams a stub reply. Leave the LLM wiring to that developer; do not build the chatbot here.
- `tests/test_smoke.py` covers the whole surface (auth, datasets, sectors, decisions, chat WS stub). Run: `pytest`.
- Full request/response contract for the frontend: **`API_CONTRACT.md`** (also live at `/docs`).
- `database/rls_policies.sql` written (org-isolation policies for `datasets`, `records`, `decision_cards`). **Not yet applied** — every query also filters by `organization_id` explicitly, so isolation holds; apply the file to turn on DB-enforced RLS.

## Next step / notes

- The external cleaning worker must INSERT cleaned rows into `records` (`organization_id`, `dataset_id`, `sector`, `data` JSONB) and set `datasets.status='ready'` + `health_score`. That's the contract this backend reads from.
- Apply RLS: `psql "$DATABASE_URL" -f database/rls_policies.sql` (see file header). Policies cover all data tables (`datasets`, `records`, `decision_cards`, `reports`, `kpi_thresholds`) and use `NULLIF(current_setting(...), '')::uuid` so they fail closed when no org context is set. `tests/test_rls_isolation.py` proves org A cannot read org B's rows via a direct query — but note the Neon owner role has **BYPASSRLS**, so in production RLS only bites a non-owner DB role; today's primary isolation is the explicit `organization_id` filter in every query (RLS is defense-in-depth).
- Frontend contract SSOT: **`docs/openapi.json`** (generated OpenAPI 3.1) + **`docs/API_CONTRACT.md`**. Regenerate openapi.json after API changes (command in the doc header). Root `API_CONTRACT.md` is a mirror.
- Reports currently return a stub `download_url` (`/reports/{id}/download`); the actual artifact assembly + a download route are still to be wired.
- The whole roadmap (incl. former deferrals: geo, what-if, reports, thresholds, user management) is now built. Chat LLM wiring remains (owned by another dev, pending `LLM_API_KEY`).

Keep every endpoint under `/api/v1/`. Do not build cleaning/ML or frontend code.
