# Portfolio dashboard: backend + web UI (Electric Mind Super Day, backend track)

A FastAPI backend that turns a flaky legacy CRM and local seed data into one clean API for an
investment dashboard, plus a React dashboard that uses it. Built by a team of three; scope,
contract and rules are in [`BRIEF.md`](../../BRIEF.md), decisions in
[`architecture/DECISIONS.md`](../../architecture/DECISIONS.md), the demo script in
[`DEMO.md`](DEMO.md).

**Stack:** Python 3.14 · FastAPI · httpx (async) · Pydantic v2 · pytest · Ruff ·
React 19 + TypeScript (strict) + Tailwind + Recharts + Zod · Vite · Vitest. Data is in memory
(loaded from `backend/fixtures/seed.json` on start); no database was needed.

## Run it (from a fresh clone)

Needs Python 3.14+ and Node 24+. Four terminals; paths are from the repo root.

| Step | macOS / Linux (bash, zsh) | Windows (PowerShell) |
|---|---|---|
| 1 · Backend install (once) | `cd backend/solution && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt` | `cd backend\solution; py -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements-dev.txt` |
| 2 · History data (**each demo day**) | `node backend/fixtures/generate-history.mjs` | same |
| 3 · Mock CRM (:4002) | `node backend/mock-crm.mjs` | same |
| 4 · API (:3000), venv active | `cd backend/solution && uvicorn app.main:app --port 3000 --reload` | `cd backend\solution; uvicorn app.main:app --port 3000 --reload` |
| 5 · Web (:5173) | `cd backend/solution/web && npm install && npm run dev` | `cd backend\solution\web; npm install; npm run dev` |

Open **http://localhost:5173** (dashboard) and **http://127.0.0.1:3000/docs** (API docs).
If PowerShell blocks activation: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
The history file's dates end on the day it is generated, so regenerate it before a demo or 1D/YTD
look empty (D1).

**Config** (env vars, defaults): `PORT=3000` · `CRM_BASE_URL=http://127.0.0.1:4002` ·
`CRM_TIMEOUT_SECONDS=2.0` · `CACHE_TTL_SECONDS=30` · `API_TOKEN=superday-demo-token` (unused until
auth exists). Use `127.0.0.1`, not `localhost`: on Windows `localhost` tries IPv6 first and cost
~450 ms per CRM call.

## Tests

| What | Command | Result |
|---|---|---|
| Backend: calculations, CRM mapping, cache, routes | `pytest` (in `backend/solution`, venv active) | **126 passed** |
| Backend lint and format | `ruff check .` · `ruff format --check .` | clean |
| Web: format helper, contract checks | `npm test` (in `web/`) | **16 passed** |
| Web types and build | `npm run typecheck` · `npm run build` | clean |

Business rules were written tests-first from the BRIEF.md §8 examples. Calculations are pure
functions tested without HTTP; the CRM and the clock are faked, so the cache tests take
milliseconds instead of waiting 30 s.

## What's done

| Task | Priority | Status | Owner |
|---|---|---|---|
| 1 · `GET /portfolios/:id` from the CRM (mapping, timeout, 404) | Must | ✅ Done, in UI | Eric |
| 2 · `GET /portfolios/:id/holdings` (server-side calculations) | Must | ✅ Done, in UI | Vishek |
| 4 · Auth middleware | Must | ❌ **Not done** (see below) | — |
| 9 · CRM cache with stale fallback | Should | ✅ Done, in UI | Eric |
| 3 · `GET /portfolios/:id/performance-history` | Should | ✅ Done, in UI | Betty |
| 5 · `GET /portfolios/:id/allocation` | Should | ✅ Done, in UI | Betty |
| 10 · Ledger replay · 6 · Household view · 7 · Currency | Could | Not started | — |
| 8 · Holding detail | Won't | Not started | — |
| Web dashboard (not required by the track) | extra | ✅ Done | Eric |

## Endpoints

All errors are flat: `{"error": "<code>", "message": "<text>"}`. Money is decimal CAD rounded to
2 dp at the response; percentages are unrounded decimals (`0.0032` = 0.32%).

| Endpoint | Source | Returns | Errors |
|---|---|---|---|
| `GET /health` | — | `{status: "ok"}` | |
| `GET /portfolios/{id}` | mock CRM, cached 30 s | `portfolioId, clientId, clientName, label, currency, totalMarketValue, dayChangeAmount, dayChangePercent, totalReturnSinceInception, asOf, stale, cachedAt` | 404 `not_found` · 503 `crm_unavailable` |
| `GET /portfolios/{id}/holdings` | seed data | one row per position with `marketValue, weightPercent, unrealizedGainLoss, dayChangeAmount, dayChangePercent` | 404 |
| `GET /portfolios/{id}/performance-history?range=1D\|1M\|YTD\|1Y\|All` | generated history | `[{date, marketValue}]`, oldest first | 400 `invalid_range` · 404 |
| `GET /portfolios/{id}/allocation` | seed data | `[{assetClass, value, percent}]` | 404 |

**CRM behaviour (Tasks 1 and 9):** the mapper reads each field through a table of candidate paths,
so the CRM's nested variant and missing fields are handled (missing → `null`, never an invented
0). Each call has a 2 s overall deadline. A fresh copy (< 30 s) is served without calling the CRM.
If the CRM errors, times out or sends something unreadable, the last good copy is served with
`stale: true` and its original `cachedAt`; with no copy, 503. A CRM 404 is never cached. A
successful call after a stale period replaces the copy. Verify with the mock's `POST /__control`
and `GET /__stats` (`backend/CRM.md`).

## Web dashboard (`web/`)

One page from the approved wireframe (`design/wireframe/`): client header and KPI tiles,
performance chart with range buttons, allocation (Bar/Pie), holdings with search, asset-class
filter, "hide closed" and sort. Each card loads on its own with loading, empty and error states, so
a CRM outage only affects the header (stale banner, or an error card with Try again). `src/api.ts`
has one function per endpoint and checks every response against the contract (`src/contract.ts`,
Zod); a backend that drifts fails with the field name. Vite proxies `/api/*` to the API, so there
is no CORS in development.

## Assumptions and decisions

Full list: `BRIEF.md` §9 (A1–A16) and `architecture/DECISIONS.md` (D1–D5). The ones that change
what you see:
- **Zero previous close** (NEW): `dayChangePercent: null` ("unknown"), shown as "—" (A2). The CRM
  reports `0` for P-9002's portfolio-level %; we pass it through and show it as-is.
- **Closed position** (ZERO, 0 shares): all calculated fields 0; the UI shows "—" for its day %.
- **History ranges** count back from today (UTC), calendar months, inclusive; less history than
  the range → whatever exists, no padding; unknown range → 400 (A6, A9–A11).
- **Allocation** sums the holdings' market values, not the CRM total; only classes present (A13–A14).
- **Cache** is in memory and per process; it empties on restart; no lock on concurrent misses (A12).

## Unfinished work and next steps

1. **Auth (Task 4, a Must) is not implemented**, by team decision when time ran out. Every endpoint
   answers without a token. Planned: one check in `app/auth.py` on every route but `/health`;
   missing, malformed (`Token x`, bare `Bearer`) or wrong token → 401
   `{"error": "unauthorized", ...}`, never 500. The web app already sends
   `Authorization: Bearer superday-demo-token`, so no frontend change is needed.
2. Coulds: ledger replay (10), household view (6, also replaces the hard-coded portfolio picker),
   `?currency=USD` (7).
3. Production: serve web and API from one origin (the `/api` proxy exists only in dev); move the
   cache to a shared store if more than one API process runs; code-split the web bundle (Recharts
   makes it > 500 kB).

## Layout

```
app/main.py              app, error handlers, /health, router registration
app/config.py            settings from env vars
app/errors.py            ApiError + handlers (flat error shape)
app/schemas.py           response models (camelCase JSON)
app/routers/             portfolios (1, 9) · holdings (2) · history (3) · allocation (5)
app/services/            crm_client, crm_mapper, cache, holdings_calc, history_filter, allocation
app/data/repository.py   read access to seed.json and performance-history.json
app/auth.py              placeholder for Task 4
tests/                   pytest, one file per module
web/src/                 App, sections/ (Summary, Performance, Allocation, Holdings), api, contract, format
```

## Optional AI provider key

Not used by the dashboard. If needed later: put `OPENROUTER_API_KEY` in `backend/solution/.env`
(ignored by Git; copy `.env.example`), start with
`uvicorn app.main:app --port 3000 --reload --env-file .env`, and never put provider keys in
frontend code or `VITE_` variables.
