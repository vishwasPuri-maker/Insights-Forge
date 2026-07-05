# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Frontend for **DecisIQ** — an AI Decision Intelligence Platform (multi-tenant, multi-sector: Retail, Service, Education, Agriculture). This repo is the **React SPA only**; it consumes a separate FastAPI backend over REST (base path `/api/v1`). It renders JSON; it does not process data or own auth issuance. The parent directory's `CLAUDE.md` describes that backend — do not confuse the two.

Not a git repository. There is no ESLint config despite `npm run lint` calling `eslint`; linting is actually done via **oxlint** (`.oxlintrc.json`).

## Commands

```bash
npm run dev              # Vite dev server (HMR)
npm run build            # tsc -b type-check, then vite build
npm run preview          # serve production build
npm test                 # vitest run (all tests, one shot)
npm run test:ui          # vitest interactive UI
npm run test:coverage    # vitest with v8 coverage
npx oxlint               # lint (npm run lint's eslint is not configured)
```

Run a single test file / filter:
```bash
npx vitest run src/features/dashboard/api/dashboardMapper.test.ts
npx vitest run -t "maps dashboard summary"     # by test name
```

There is no `.env` committed. The API base URL comes from `VITE_API_URL` (defaults to `/api/v1`).

## Architecture

**Stack:** React 19 + Vite + TypeScript, TanStack Query (server state), Zustand (client state), react-router-dom v7, axios, shadcn/ui (Radix + Tailwind, `components.json`), ECharts (`echarts-for-react`) for charts, react-hook-form + zod for forms, MSW for mocked APIs, framer-motion.

**`@/` aliases `src/`** (configured in `vite.config.ts`, `vitest.config.ts`, `tsconfig.app.json`).

### Feature-slice pattern (the core convention)
Each domain lives in `src/features/<name>/` and is self-contained with the same internal shape. Follow it exactly when adding a feature:

```
features/<name>/
├── api/<name>Client.ts     # axios calls via shared apiClient; returns mapped domain types
├── api/<name>Mapper.ts      # maps backend snake_case DTOs -> frontend camelCase domain models
├── hooks/use<Name>.ts       # TanStack Query hook; reads tenant/sector from store; enabled gating
├── components/              # presentational components for the feature
├── pages/<Name>Page.tsx     # route entry, lazy-loaded in app/router.tsx
└── __tests__/               # client, mapper, hook, isolation, accessibility tests
```

Existing features: `dashboard`, `dataset`, `reasoning`, `simulation`, `reports`, `recommendation`, `governance`, `administration`. Domains model the product's "WHAT / WHY / WILL / SHOULD" paradigm (dashboard=what, reasoning=why, simulation=will, recommendation=should).

### DTO → domain mapping is mandatory
Backend responses are snake_case DTOs (`*DTO` types in `src/types/`). **Clients never return raw DTOs** — they pass through a mapper that converts to camelCase domain models. Components and hooks only ever see mapped domain types. When adding an endpoint, add both the DTO type and the mapper.

### Data fetching
- `src/services/apiClient.ts` — the single shared axios instance. Request interceptor injects the JWT from `sessionStorage['insight-auth-storage']`. Response interceptor normalizes every error into the `ApiErrorResponse` shape (`code`/`message`/`details`/`timestamp`) — the INF-12 error contract. Consumers `catch` this shape, not raw axios errors.
- All query keys are centralized in `src/lib/queryKeys.ts`. Tenant + sector are part of the key (e.g. `[tenantId, sectorId, 'dashboard']`) so cache is isolated per tenant/sector. Use these; do not inline key arrays.
- Query hooks read `tenantId`/`sectorId` from `useTenantStore` and gate with `enabled: !!tenantId && !!sectorId`.

### State (Zustand stores in `src/store/`)
- `authStore` — `isAuthenticated`, `role`, `token`; persisted to **sessionStorage** under `insight-auth-storage` (this is where apiClient reads the token).
- `tenantStore` — `tenantId`, `sectorId`; persisted to localStorage.
- `uiStore` — UI state.

### Routing & multi-tenant isolation
`src/app/router.tsx` uses URL structure `/:tenant_id/:sector_id/<page>`. Pages are `React.lazy` + Suspense. `AuthGuard` (`src/app/guards/`) redirects to `/401` when unauthenticated and `/403` on RBAC/tenant/sector failure. `RouteErrorBoundary` handles route errors. `MockAuthGateway` at `/` is a localhost demo login that bypasses the identity provider — replace when wiring real auth.

### Providers & entry
`src/main.tsx` wraps the app in `ThemeProvider` (default dark) → `QueryProvider` → `AppRouter`, and calls `bootstrapAxe()` for dev-time a11y checks.

### Testing
- Vitest + jsdom + Testing Library. `src/setupTests.ts` registers jest-dom + jest-axe matchers, starts the **MSW server with `onUnhandledRequest: 'error'`** (any unmocked request fails the test), and globally mocks `echarts` and `ResizeObserver`.
- Mock API handlers live in `src/mocks/handlers/` (`index.ts` plus per-feature files); `src/mocks/server.ts` (node/tests) and `src/mocks/browser.ts` (dev worker) consume them. When adding an endpoint, add a handler here or tests will error.
- Use `src/utils/test-utils.tsx` for rendering with providers.
- Each feature ships `*Isolation` (tenant/sector cache separation) and `*Accessibility` (axe) tests — mirror them for new features.

## Conventions

- Endpoints are relative to `/api/v1` (apiClient baseURL); sector is a path param: `/sectors/${sectorId}/...`.
- Tailwind design tokens: `brand.*` and `ai.*` semantic colors + CSS-variable-based shadcn colors (`tailwind.config.ts`). Prefer these tokens over hardcoded colors. Note both `.js` and `.ts` variants of `tailwind.config` / `vite.config` exist — the `.ts` files are authoritative (referenced by `components.json` and tooling).
- Charts go through `src/components/charts/BaseChart.tsx`; shared UI primitives in `src/components/ui/` (shadcn).
- **Backend API contract:** `openapi.json` at repo root is the source of truth for backend endpoints/DTO shapes (`contract_reference.json.json` is a duplicate copy). Check it when adding an endpoint rather than guessing snake_case field names.
- **Two client locations exist.** The feature-slice pattern puts clients in `features/<name>/api/`, but some older clients also live in `src/services/` (`authClient.ts`, `dashboardClient.ts`, `datasetClient.ts`, `healthClient.ts`). New features should follow the feature-slice pattern (`features/<name>/api/`); don't add new clients to `src/services/` except `apiClient.ts` itself. DTO types are centralized in `src/types/*.ts` (one file per domain), not co-located in features.
- **App shell:** authenticated routes render inside `src/layouts/ApplicationShell.tsx`.
