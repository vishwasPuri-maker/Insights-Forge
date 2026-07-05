# DecisIQ Backend — API Contract (v1)

> **Single source of truth for the frontend.** This file is the human-readable
> contract; **`docs/openapi.json`** (same folder) is the machine-readable OpenAPI
> 3.1 spec generated from the running app — import it into Postman / Insomnia / a
> client generator. Regenerate after any API change with:
> `python -c "import json; from app.main import app; open('docs/openapi.json','w').write(json.dumps(app.openapi(), indent=2))"`

For the **frontend developer**. This is the full request/response contract for
every endpoint. Live interactive docs (Swagger UI) are also served at
`http://localhost:8000/docs` while the app runs.

- **Base URL:** `http://localhost:8000`
- **All endpoints are prefixed with:** `/api/v1`
- **Content type:** `application/json` (except file upload, which is `multipart/form-data`)
- **Auth:** send the access token as `Authorization: Bearer <access_token>` on every protected route.
- **Sectors:** `retail` | `service` | `education` | `agriculture`. A user is fixed to **one** sector. That sector is baked into the JWT, so you don't send it separately — the backend reads it from the token. A user may only read/write **their own** sector.

---

## Standard shapes

### Error (every failed request)
```json
{ "error": { "code": "invalid_credentials", "message": "invalid email or password" } }
```
`code` is a stable machine-readable string (use it for UI logic); `message` is human text.
Validation errors (422) add a `details` array.

### Roles (RBAC)
| Role | Can do |
|------|--------|
| `user` | read dashboards, records, decision cards, chat |
| `manager` | everything `user` can + approve/reject decisions + upload data |
| `admin` | everything `manager` can + (future) manage users/org |

A new signup creates the org's first user as **admin**.

---

## 1. Auth

### POST `/api/v1/auth/signup`
Create an organization + its first (admin) user, and log them in.
**Request**
```json
{
  "organization_name": "Acme Retail",
  "email": "owner@acme.com",
  "password": "supersecret123",
  "sector": "retail"
}
```
**Response `201`**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```
**Errors:** `409 email_taken`, `422` (bad email / password < 8 chars / invalid sector).

### POST `/api/v1/auth/login`
**Request**
```json
{ "email": "owner@acme.com", "password": "supersecret123" }
```
**Response `200`** — same token pair as signup.
**Errors:** `401 invalid_credentials`.

### POST `/api/v1/auth/refresh`
Exchange a valid refresh token for a **new** access + refresh pair (old refresh is revoked — rotation).
**Request**
```json
{ "refresh_token": "eyJhbGc..." }
```
**Response `200`** — new token pair.
**Errors:** `401 invalid_refresh`.

### POST `/api/v1/auth/logout`
Revoke a refresh token. Idempotent.
**Request**: `{ "refresh_token": "eyJhbGc..." }`
**Response `204`** (no body).

**Access token payload** (decoded, FYI — you don't need to parse it, but it contains):
```json
{ "type": "access", "organization_id": "<uuid>", "sub": "<user-uuid>", "role": "admin", "sector": "retail", "iat": 0, "exp": 0 }
```
Access token lifetime: **15 min**. Refresh token: **7 days**. On `401` from any protected call, call `/auth/refresh`, then retry.

---

## 2. Ingestion (file upload)

### POST `/api/v1/ingestion/stream`
Upload a raw data file. Streams to S3 and triggers the (separate) cleaning worker.
**Auth:** `manager` or `admin`.
**Content-Type:** `multipart/form-data`
**Form fields:**
| field | type | notes |
|-------|------|-------|
| `sector` | text | must equal the caller's own sector |
| `file` | file | the raw CSV/XLSX/etc. |

**Response `201`**
```json
{ "dataset_id": "<uuid>", "sector": "retail", "status": "uploaded", "size_bytes": 10240 }
```
Poll `GET /datasets/{dataset_id}` for cleaning progress + health score.
**Errors:** `400 invalid_sector`, `403 sector_forbidden`, `403` (role too low), `502 upload_failed` (storage unavailable).

---

## 3. Datasets

### GET `/api/v1/datasets`
List the org's uploaded datasets (newest first). **Auth:** any role.
**Query:** `limit` (1–500, default 100), `offset` (default 0).
**Response `200`**
```json
[
  {
    "id": "<uuid>",
    "sector": "retail",
    "original_filename": "sales_q1.csv",
    "status": "ready",
    "health_score": 92.5,
    "size_bytes": 10240,
    "content_type": "text/csv",
    "uploaded_by": "<user-uuid>",
    "created_at": "2026-07-01T10:00:00Z"
  }
]
```
`status` lifecycle: `pending` → `uploaded` → `cleaning` → `ready` | `failed`.
`health_score` is `null` until the cleaning worker sets it.

### GET `/api/v1/datasets/{dataset_id}`
One dataset (same object shape as above). **Errors:** `404 not_found`.

---

## 4. Sector dashboards

`{sector}` in the path **must match the caller's sector** (else `403 sector_forbidden`;
unknown sector → `404 unknown_sector`). All read-only, any role.

### GET `/api/v1/sectors/{sector}/scorecard`
KPI tiles for the dashboard header.
**Response `200`**
```json
{
  "sector": "retail",
  "cards": [
    { "key": "records", "label": "Cleaned Records", "value": 1240, "unit": null },
    { "key": "datasets", "label": "Datasets", "value": 8, "unit": null },
    { "key": "datasets_ready", "label": "Datasets Ready", "value": 6, "unit": null },
    { "key": "avg_health", "label": "Avg Data Health", "value": 92.5, "unit": "%" },
    { "key": "pending_decisions", "label": "Pending Decisions", "value": 3, "unit": null }
  ]
}
```

### GET `/api/v1/sectors/{sector}/timeseries`
Chart-ready series (records per day).
**Response `200`**
```json
{
  "sector": "retail",
  "labels": ["2026-06-29", "2026-06-30", "2026-07-01"],
  "series": [ { "name": "records", "values": [12, 40, 33] } ]
}
```
Plot `labels` on the X axis; each `series[]` is one line/bar (`name` + `values`, aligned to `labels`).

### GET `/api/v1/sectors/{sector}/records`
Paginated cleaned rows. **Query:** `limit` (1–500, default 50), `offset` (default 0).
**Response `200`**
```json
{
  "sector": "retail",
  "total": 1240,
  "limit": 50,
  "offset": 0,
  "items": [
    {
      "id": "<uuid>",
      "dataset_id": "<uuid>",
      "sector": "retail",
      "data": { "product": "A", "sales": 10, "date": "2026-07-01" },
      "recorded_at": "2026-07-01T00:00:00Z",
      "created_at": "2026-07-01T10:05:00Z"
    }
  ]
}
```
`data` is a **flexible JSON object** — its keys depend on the uploaded file's columns (generic model). Render dynamically.

### GET `/api/v1/sectors/{sector}/records/{record_id}`
A single record (same shape as one `items[]` element). **Errors:** `404 not_found`.

---

## 5. Decision cards

AI-recommended actions a manager approves/rejects. Scoped to the caller's sector.

### GET `/api/v1/decision-cards`
List cards (newest first). **Auth:** any role.
**Query:** `status` = `pending` | `approved` | `rejected` (optional), `limit`, `offset`.
**Response `200`**
```json
[
  {
    "id": "<uuid>",
    "sector": "retail",
    "title": "Restock product A",
    "recommendation": "Sales trending up 18% week-over-week",
    "confidence_score": 0.87,
    "status": "pending",
    "resolved_by": null,
    "resolved_at": null,
    "created_at": "2026-07-01T09:00:00Z"
  }
]
```

### POST `/api/v1/decision-cards/{card_id}/approve`
### POST `/api/v1/decision-cards/{card_id}/reject`
**Auth:** `manager` or `admin`. No request body.
**Response `200`** — the updated card (`status` → `approved`/`rejected`, `resolved_by`/`resolved_at` set).
**Errors:** `404 not_found`, `409 already_decided` (card is not `pending`), `403` (role too low).

---

## 6. Map (GeoJSON)

### GET `/api/v1/sectors/{sector}/geo`
Location points for the map, as a **GeoJSON FeatureCollection**. Any role; sector
must match the caller's. Built from records whose `data` has coordinates
(`lat`/`latitude` + `lng`/`lon`/`longitude`); records without coords are skipped.
**Query:** `limit` (1–5000, default 1000).
**Response `200`**
```json
{
  "type": "FeatureCollection",
  "sector": "retail",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [77.21, 28.61] },
      "properties": { "product": "T-Shirt", "sales": 120, "record_id": "<uuid>" }
    }
  ]
}
```
> GeoJSON coordinates are `[longitude, latitude]` (lng first). Drop `features` straight into Leaflet/Mapbox.

---

## 7. What-if simulator

### POST `/api/v1/simulate`
Recalculate projections **in memory** — nothing is saved. Any role; sector comes
from the token. `projected = current * (1 + change_pct/100)`.
**Request**
```json
{ "metrics": [
  { "key": "sales", "current": 100, "change_pct": 10 },
  { "key": "cost",  "current": 40,  "change_pct": -5 }
] }
```
**Response `200`**
```json
{
  "sector": "retail",
  "projections": [
    { "key": "sales", "current": 100, "projected": 110.0, "change_pct": 10 },
    { "key": "cost",  "current": 40,  "projected": 38.0,  "change_pct": -5 }
  ],
  "total_current": 140.0,
  "total_projected": 148.0
}
```

---

## 8. Reports (async)

### POST `/api/v1/reports/compile`
Kick off a report. Returns immediately (`202`) with a `pending` report; it's
compiled in the background. Any role; sector from token.
**Request**
```json
{ "report_type": "sales_summary", "params": { "quarter": "2026-Q2" } }
```
**Response `202`**
```json
{ "id": "<uuid>", "sector": "retail", "report_type": "sales_summary", "status": "pending", "download_url": null, "created_at": "2026-07-01T10:00:00Z" }
```

### GET `/api/v1/reports/{report_id}`
Poll for status + link. `status`: `pending` → `processing` → `ready` | `failed`.
When `ready`, `download_url` is populated.
**Response `200`**
```json
{ "id": "<uuid>", "sector": "retail", "report_type": "sales_summary", "status": "ready", "download_url": "/reports/<uuid>/download", "created_at": "2026-07-01T10:00:00Z" }
```
**Errors:** `404 not_found`.

---

## 9. KPI thresholds

### GET `/api/v1/thresholds`
List the caller's sector thresholds. Any role.
**Response `200`**
```json
[
  { "id": "<uuid>", "sector": "retail", "metric_key": "sales", "label": "Sales per product", "warning_value": 50.0, "critical_value": 20.0 }
]
```

### PUT `/api/v1/thresholds/{threshold_id}`
Update warning/critical bounds. **Auth:** `manager` or `admin`.
**Request**: `{ "warning_value": 70, "critical_value": 30 }`
**Response `200`** — the updated threshold. **Errors:** `404 not_found`, `403` (role too low).

---

## 10. User management

**Admin only.** New users always belong to the caller's own organization (the org
is taken from the token, never the request body).

### GET `/api/v1/users`
List users in the caller's org.
**Response `200`** — array of:
```json
{ "id": "<uuid>", "organization_id": "<uuid>", "email": "staff@acme.com", "role": "user", "sector": "retail", "created_at": "2026-07-01T10:00:00Z" }
```

### POST `/api/v1/users`
**Request**
```json
{ "email": "staff@acme.com", "password": "staffpass123", "role": "user", "sector": "retail" }
```
`role` ∈ `user|manager|admin` (default `user`). **Response `201`** — the created user.
**Errors:** `409 email_taken`, `422` (bad email / short password / invalid role or sector).

### DELETE `/api/v1/users/{user_id}`
**Response `204`**. **Errors:** `400 cannot_delete_self`, `404 not_found`.

---

## 11. Chat (WebSocket)

### WS `/api/v1/chat/stream`
Server-side LLM chat, streamed. Auth via the access token as a **query param**.

**Connect:** `ws://localhost:8000/api/v1/chat/stream?token=<access_token>`
(Invalid/missing token → the socket is closed with code `1008` before accepting.)

**Client → server** (one frame per user message):
```json
{ "message": "Why did retail sales dip last week?" }
```

**Server → client** (streamed frames):
```json
{ "type": "token", "content": "Sales " }
{ "type": "token", "content": "dipped " }
{ "type": "done" }
```
- `type: "token"` — append `content` to the current reply (many of these).
- `type: "done"` — the reply is complete; ready for the next message.
- `type: "error"` — `{ "type": "error", "message": "..." }` (e.g. empty message, or LLM failure). The socket stays open.

You can send multiple messages on the same open socket.
> Note: until an LLM key is configured server-side, replies are a simple stubbed echo so you can build the UI. The frame protocol above will not change when the real LLM is wired in.

---

## Quick reference

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/api/v1/auth/signup` | public | create org + admin user |
| POST | `/api/v1/auth/login` | public | log in |
| POST | `/api/v1/auth/refresh` | public (refresh token) | rotate tokens |
| POST | `/api/v1/auth/logout` | public (refresh token) | revoke refresh token |
| GET  | `/api/v1/health` | public | liveness check |
| POST | `/api/v1/ingestion/stream` | manager/admin | upload raw file |
| GET  | `/api/v1/datasets` | any | list datasets |
| GET  | `/api/v1/datasets/{id}` | any | one dataset |
| GET  | `/api/v1/sectors/{sector}/scorecard` | any | KPI tiles |
| GET  | `/api/v1/sectors/{sector}/timeseries` | any | chart data |
| GET  | `/api/v1/sectors/{sector}/records` | any | paginated rows |
| GET  | `/api/v1/sectors/{sector}/records/{id}` | any | one row |
| GET  | `/api/v1/decision-cards` | any | list cards |
| POST | `/api/v1/decision-cards/{id}/approve` | manager/admin | approve |
| POST | `/api/v1/decision-cards/{id}/reject` | manager/admin | reject |
| GET  | `/api/v1/sectors/{sector}/geo` | any | map GeoJSON |
| POST | `/api/v1/simulate` | any | what-if projection |
| POST | `/api/v1/reports/compile` | any | start a report (async) |
| GET  | `/api/v1/reports/{id}` | any | report status + link |
| GET  | `/api/v1/thresholds` | any | list KPI thresholds |
| PUT  | `/api/v1/thresholds/{id}` | manager/admin | update threshold |
| GET  | `/api/v1/users` | admin | list org users |
| POST | `/api/v1/users` | admin | create user |
| DELETE | `/api/v1/users/{id}` | admin | delete user |
| WS   | `/api/v1/chat/stream?token=` | any | streaming chat |

**HTTP status codes used:** `200` OK · `201` created · `202` accepted (report queued) · `204` no content · `400` bad request · `401` unauthorized · `403` forbidden (role/sector) · `404` not found · `409` conflict · `422` validation · `502` upstream storage failure.
