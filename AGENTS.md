# AGENTS.md — Insights Forge Project Brain

> **Every AI agent must read this file first.** This file is automatically discovered by agent frameworks. It bootstraps the agent with enough context to work effectively without scanning the entire repository.

---

## 1. Before You Start Any Task

Read these files **in order** before doing anything else:

1. **`brain/master-memory.md`** — Compressed project intelligence (3-min read, covers 95% of what you need)
2. **`brain/architecture.md`** — Full system architecture (read if touching backend or infrastructure)
3. **`brain/patterns.md`** — Approved implementation patterns (read before writing any code)
4. **`brain/decisions.md`** — Engineering decisions (read before making architectural choices)
5. **`brain/mistakes.md`** — Known bugs and fixes (read before debugging)

For feature-specific work, also read:
- **`brain/feature-map.md`** — Maps features to files
- **`brain/dependency-graph.md`** — What breaks when you change something

---

## 2. Project Identity

- **Name:** Insights Forge (PAX 2.0 / DecisIQ)
- **Type:** Multi-tenant AI Decision Intelligence Platform
- **Sectors:** Retail · Service · Education · Agriculture
- **Backend:** FastAPI + PostgreSQL (Neon) + Redis + Celery + Gemini 2.5 Flash
- **Frontend:** React 19 + Vite + TanStack Query + Zustand + shadcn/ui
- **Location:** This repo is at `IsightFordge_v1/IsightFordge_v1/`

---

## 3. Critical Rules (Never Break These)

1. **No async SQLAlchemy** — Celery requires sync. Use `Session`, not `AsyncSession`.
2. **No hard deletes** — Always soft delete (`is_deleted=True`).
3. **UUID primary keys** — All tables, always.
4. **No passlib** — Use `bcrypt` directly (see `app/core/security.py`).
5. **Tenant isolation** — Every query filters by `workspace_id` (or `organization_id`).
6. **Contract freeze** — API paths/shapes in `contract_reference.json.json` are frozen.
7. **Feature slice** — New frontend features use `features/<name>/api/hooks/components/pages/` structure.
8. **DTO mapping** — Frontend clients always map DTOs to domain types before returning.
9. **Query key isolation** — TanStack Query keys always include `[tenantId, sectorId, ...]`.
10. **AppError only** — Backend uses `AppError(status, code, message)`, never `HTTPException` directly.

---

## 4. How to Start Servers

```powershell
# Backend (from backend/backend/)
.venv\Scripts\uvicorn.exe app.main:app --reload --host 127.0.0.1 --port 8000

# Frontend (from frontend/)
npm run dev
```

Health: `GET http://127.0.0.1:8000/api/v1/health` → `{"status": "ok"}`

---

## 5. Active Backlog (What's Not Done Yet)

- Excel (.xlsx) ingestion — add `openpyxl` to `requirements.txt` + parse in `ingestion_service.py`
- Real report generation — bind PDF/XLSX to `/reports/compile`
- Frontend ↔ Backend E2E testing — start servers and verify all flows
- Docker Compose + production deployment

---

## 6. Project Brain Files

| File | Purpose |
|------|---------|
| `brain/master-memory.md` | **First read** — compressed project intelligence |
| `brain/memory.md` | Full project summary + current state |
| `brain/architecture.md` | Complete system architecture |
| `brain/patterns.md` | Approved implementation patterns |
| `brain/decisions.md` | Engineering decisions log |
| `brain/mistakes.md` | Bug prevention — known issues + fixes |
| `brain/roadmap.md` | Future direction + milestones |
| `brain/glossary.md` | Domain and technical terms |
| `brain/dependency-graph.md` | File relationships + change impact |
| `brain/feature-map.md` | Features → implementation files |
