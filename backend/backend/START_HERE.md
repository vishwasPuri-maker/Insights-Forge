# 👋 START HERE — Insights Forge Backend

Read this first. It takes ~10 minutes to get running.

---

## ✅ What YOU must provide (fill these into a `.env` file)

The code is complete. You only need to supply these values. Copy `.env.example`
to a new file named `.env` and fill in:

| Value | Where to get it | Required? |
|---|---|---|
| `DATABASE_URL` | Your PostgreSQL/Neon connection string. **Must start with `postgresql+psycopg://`** (Neon gives `postgresql://` — change the prefix). | ✅ Yes |
| `SECRET_KEY` | Any long random string. Generate: `python -c "import secrets; print(secrets.token_urlsafe(64))"` | ✅ Yes |
| `BREVO_API_KEY` | Your Brevo account → SMTP & API → API Keys. (Only needed for signup/verify/reset **emails**.) | ⚠️ For email |
| `EMAIL_FROM` | An email **verified as a sender in YOUR Brevo account**. | ⚠️ For email |
| `EMAIL_FROM_NAME` | Any display name, e.g. `Insights Forge`. | optional |
| `FRONTEND_URL` | Where your frontend runs, e.g. `http://localhost:5173`. Used in email links. | recommended |
| `BACKEND_CORS_ORIGINS` | Your frontend origin(s), comma-separated. If missing, the browser blocks API calls. | ✅ for frontend |

> If `BREVO_API_KEY`/`EMAIL_FROM` are left blank, the app still runs — only the
> emails won't send (signup/login still work; verification just can't be emailed).

---

## 🚀 Steps (in order)

```bash
# 1. Go into the folder
cd backend

# 2. Make sure you have Python 3.13
python3 --version        # must be 3.13.x

# 3. Create a virtual environment + install
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4. Create your .env
cp .env.example .env
#    ...now open .env and fill in the values from the table above

# 5. Create the database tables
alembic upgrade head

# 6. Run the server
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** — you should see all the API endpoints.
Test: `GET /api/v1/health` should return `{"status":"ok"}`.

---

## ⚠️ Common mistakes (if something fails, check these first)

1. **App won't start** → `DATABASE_URL` or `SECRET_KEY` missing/empty in `.env`.
2. **Database driver error** → `DATABASE_URL` must use `postgresql+psycopg://`, not `postgresql://`.
3. **`pip install` fails** → you're not on Python 3.13.
4. **Frontend gets a CORS error** → add the frontend's URL to `BACKEND_CORS_ORIGINS`.
5. **Emails don't arrive** → `EMAIL_FROM` must be a *verified sender* in the same Brevo account as `BREVO_API_KEY`.

---

## 🔌 Connecting the frontend

- Backend base URL: `http://127.0.0.1:8000`, all endpoints under `/api/v1/`.
- The API matches the frozen contract (`contract_reference.json.json`) exactly, so
  the existing frontend needs **no code changes** — just point it at this backend URL.
- Auth: `signup`/`login` return `{access_token, refresh_token}`. Send
  `Authorization: Bearer <access_token>` on protected calls. Renew with
  `POST /api/v1/auth/refresh`.
- After signup a user is **unverified**; login returns **403** until they verify via
  the emailed link (`POST /api/v1/auth/verify-email`).

For full details see `HANDOFF.md` and `CLAUDE.md`.
