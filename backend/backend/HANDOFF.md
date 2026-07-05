# Insights Forge Backend — Handoff / Setup Guide

FastAPI backend for the Insights Forge platform. Implements all 23 frozen-contract
endpoints (`contract_reference.json.json`) plus email verification & password reset.

## 1. Prerequisites

- Python **3.13**
- A PostgreSQL database (Neon works out of the box)
- A Brevo account + API key (for verification / reset emails) with a **verified sender**

## 2. Setup

```bash
cd backend

python3.13 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                # then fill in the values (see section 3)

alembic upgrade head                # creates all tables in your DB
uvicorn app.main:app --reload       # http://127.0.0.1:8000
```

- Interactive API docs: **http://127.0.0.1:8000/docs**
- Health check: **GET /api/v1/health**

## 3. Required `.env` values

You must set these yourself (they are NOT in the repo — ask the sender for the
shared values, or use your own):

| Variable | What it is |
|---|---|
| `DATABASE_URL` | Postgres URL, **must** use the `postgresql+psycopg://` prefix |
| `SECRET_KEY` | Long random string — `python -c "import secrets; print(secrets.token_urlsafe(64))"` |
| `BREVO_API_KEY` | Brevo transactional API key |
| `EMAIL_FROM` | A sender address **verified in your Brevo account** |
| `FRONTEND_URL` | Where the frontend runs (used in email links), e.g. `http://localhost:5173` |
| `BACKEND_CORS_ORIGINS` | Comma-separated frontend origins allowed by CORS |

## 4. Frontend integration

- Base URL: `http://<host>:8000` — all endpoints live under `/api/v1/`.
- The API exactly matches `contract_reference.json.json` (23 endpoints), so the
  existing frontend needs **no changes**.
- Auth: `POST /api/v1/auth/signup` / `login` return `{access_token, refresh_token}`.
  Send `Authorization: Bearer <access_token>` on all protected calls. Access token
  lasts 15 min; use `POST /api/v1/auth/refresh` with the refresh token to renew.
- New auth flow (beyond the contract): after signup the user is **unverified** and
  login returns **403** until they hit `POST /api/v1/auth/verify-email` with the
  token from the email. Also `forgot-password` / `reset-password`.
- If the frontend origin isn't in `BACKEND_CORS_ORIGINS`, add it (comma-separated).

## 5. Quick smoke test

```bash
curl http://127.0.0.1:8000/api/v1/health
# -> {"status":"ok"}
```

Then in Swagger (`/docs`): signup → verify-email (grab token from the email) →
login → call any `/sectors/{sector}/...` endpoint with the Bearer token.

## 6. Notes

- Migrations are the source of truth for the schema; run `alembic upgrade head`
  after pulling changes.
- `reports/compile` currently returns a ready report with a placeholder
  `download_url` (no real file generation yet).
- Redis/Celery are listed as deps but async workers are not implemented.
- See `CLAUDE.md` for architecture details and conventions.
