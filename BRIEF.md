# BRIEF: Portfolio dashboard backend (Electric Mind Super Day, backend track)

Filled in together at the start. Claude reads this before every task. Full task text:
`backend/REQUIREMENTS.md` · CRM quirks: `backend/CRM.md` · data: `backend/fixtures/seed.json`.

## 1. Problem
A dashboard frontend needs one reliable API to show an investor what they own, what it is worth and
how that has changed, because the legacy CRM is slow, awkwardly shaped and fails about 1 call in 5.
**Demo outcome:** with the mock token, `GET /portfolios/P-9001` keeps answering while the CRM fails
(stale cache), and holdings, history and allocation return tested, correct numbers.

## 2. Personas
- Dashboard developer: calls our endpoints and needs clean, consistent JSON and clear errors.
- Investor (Jane Doe, client `abc123`): sees the numbers the dashboard shows; they must be right.

## 3. Scope
**Must:**
- [ ] Task 1 · `GET /portfolios/:id`: CRM metadata, mapped, with timeout and 404 (owner: **me**)
- [x] Task 2 · `GET /portfolios/:id/holdings`: calculated fields, unit tested (owner: **partner A**)
- [ ] Task 4 · Auth middleware on every route except `/health` (owner: **partner A**)

**Should:**
- [ ] Task 9 · CRM cache with stale fallback (owner: **me**, after Task 1)
- [ ] Task 3 · `GET /portfolios/:id/performance-history` (owner: **partner B**, first)
- [ ] Task 5 · `GET /portfolios/:id/allocation` (owner: **partner B**, after Task 3; uses Task 2's calc)

**Could:** Task 10 ledger replay and schema · Task 6 household view · Task 7 `?currency=USD`

**Won't today** (next steps in the demo): Task 8 holding detail · a TypeScript frontend (only if
the Shoulds are done) · real user auth · live prices · writes (trades, transactions).

**Order of work:** partner A builds the skeleton first (~15 min: app, error handlers, auth stub,
data loader, route registration). Meanwhile, me: CRM mapper + tests; partner B: history filter +
tests (pure functions, no server needed).

## 4. AI feature
Not part of this challenge. None.

## 5. Flow (API, no screens)
**Demo path** (`backend/requests.http`, token `superday-demo-token`): no token → 401 · portfolio
P-9001 → mapped metadata · set CRM to `error`, wait for TTL → same data with `stale: true` · holdings
P-9001 (ZERO row all zeros) · history `range=YTD`, then `range=1Y` on P-9002 (only 60 days) ·
allocation P-SINGLE (`percent: 1.0`) · `pytest` all green.

## 6. Stack and architecture
Python 3.14 · **FastAPI** + uvicorn · **httpx** (async, CRM only) · **Pydantic** v2 for request and
response models (camelCase aliases) · **pytest** + FastAPI `TestClient` · **Ruff** (lint + format,
dev only) · data in memory from `seed.json`; stdlib **sqlite3** only when needed (Task 10) · `venv`
+ `requirements.txt` · service on **:3000**, mock CRM on **:4002**.
**Frontend (TSX):** `backend/solution/web/`: Vite + React + TypeScript strict + Tailwind · Vitest ·
npm · :5173, proxies `/api` → :3000 (prefix stripped). Scaffold only (a /health page); screens wait
until the backend Shoulds are done.

```
client ──Bearer token──▶ FastAPI :3000 (backend/solution/)
  auth (all routes but /health) ─▶ routers/ (thin) ─▶ services/ (pure, tested) ─▶ data/ (seed.json)
                                                      crm_client ──async httpx, 2 s timeout──▶ mock CRM :4002
```

```
backend/solution/
  app/
    main.py        app, error handlers, router registration
                   (only shared file: one line per router)                       [skeleton]
    auth.py        Bearer check → 401 { error, message }                         [A]
    errors.py      ApiError + handlers: ApiError, 422 validation, 404/405 and crashes → our shape [skeleton]
    schemas.py     Pydantic response models (camelCase alias); each owner adds theirs
    routers/       portfolios.py [me] · holdings.py [A] · history.py, allocation.py [B]
    services/      crm_client.py, crm_mapper.py, cache.py [me] · holdings_calc.py [A]
                   history_filter.py, allocation.py [B]
    data/          repository.py: loads seed.json + performance-history.json     [skeleton]
  tests/           test_<module>.py next to each owner's work
  requirements.txt       fastapi, uvicorn, httpx, pydantic
  requirements-dev.txt   pytest, ruff
  pyproject.toml         ruff settings (line length, rules) so all three format the same
```

**Rules of the architecture**
- `GET /portfolios/:id` reads the **CRM**; every other endpoint reads the **local seed data**.
- Routes do no maths: they parse input, call a service, return JSON. Calculations are pure functions.
- The CRM call is **async** (`httpx.AsyncClient(timeout=2.0)`), no retries; the cache is the safety
  net. A slow CRM never blocks other requests.
- Every error has our flat shape, never FastAPI's `{"detail": ...}`: handlers for `ApiError`,
  `RequestValidationError` (422 → 400), `HTTPException` (404/405) and `Exception` (500, logged, no
  stack trace in the body).
- Routes declare `response_model=` with `by_alias` camelCase output, so `/docs` shows the contract.
- Auth is our own check (not `HTTPBearer`, which may return 403): only `Authorization: Bearer <token>`
  passes; token from env `API_TOKEN`, default `superday-demo-token`. Skips `/health`.
- `ruff check` and `ruff format` before every merge.
- Git: one branch each, small merges to `main`, pull before each prompt, one LOG.md line per step.

## 7. Data and API contract
**In-memory data (from seed.json):** clients · portfolios · holdings · holdingDetails · transactions
· `CADtoUSD` · performance history (`node backend/fixtures/generate-history.mjs`, not in Git).
**Tables (only if we move to SQLite / Task 10):** `clients(client_id PK, name)` ·
`portfolios(portfolio_id PK, client_id FK, label, currency)` · `holdings(holding_id PK, portfolio_id FK,
ticker, name, asset_class, price, previous_close_price)` · `transactions(transaction_id PK,
holding_id FK, type BUY|SELL, quantity, price, date)`.

| Method | Path | Response (200) | Errors |
|---|---|---|---|
| GET | `/health` | `{ status: "ok" }` (no auth) | |
| GET | `/portfolios/:id` | `{ portfolioId, clientId, clientName, label, currency, totalMarketValue, dayChangeAmount, dayChangePercent, totalReturnSinceInception, asOf, stale, cachedAt }` | 401 · 404 `not_found` · 503 `crm_unavailable` |
| GET | `/portfolios/:id/holdings` | `[{ ticker, name, assetClass, quantity, costBasisPerShare, price, previousClosePrice, marketValue, weightPercent, unrealizedGainLoss, dayChangeAmount, dayChangePercent }]` | 401 · 404 `not_found` |
| GET | `/portfolios/:id/performance-history?range=1D\|1M\|YTD\|1Y\|All` | `[{ date, marketValue }]`, oldest first | 401 · 400 `invalid_range` · 404 `not_found` |
| GET | `/portfolios/:id/allocation` | `[{ assetClass, value, percent }]` | 401 · 404 `not_found` |

**Conventions:** JSON camelCase · money in **decimal CAD**, rounded to 2 dp only when the response
is sent · percentages are **unrounded decimals** (0.0032 = 0.32%) · dates ISO (`YYYY-MM-DD`,
datetimes with `Z`) · every error is flat **`{ "error": "<code>", "message": "<text>" }`** · codes:
`unauthorized` 401, `not_found` 404, `invalid_range` / `invalid_currency` 400, `crm_unavailable` 503.

## 8. Business rules (the tests come from the examples; seed data)
| ID | Rule | Example (in → out) | Edge case |
|---|---|---|---|
| R1 | CRM mapping: find the account by `acct_ref` (not the first), accounts at `client_record.accounts` **or** `client_record.relationships.accounts` | P-9002 → its own account · `mode=nested` → same result as `ok` | `mode=missing`: null `curr_val.amt`, no nickname → those fields `null`, no crash · unknown id → 404 |
| R2 | CRM failure: 2 s timeout, never hang or 500 | `mode=timeout` → answer in ≈2 s | no cache → 503 `crm_unavailable` |
| R3 | Holding values: `marketValue = qty × price` · `unrealizedGainLoss = (price − cost) × qty` · `dayChangeAmount = (price − prevClose) × qty` · `dayChangePercent = (price − prevClose) / prevClose` | AAPL (P-9001) 120 × 227.50 → MV 27,300.00 · gain 3,300.00 · day 300.00 · day % 0.011111 | ZERO (qty 0) → MV, weight, gain, day all 0 · NEW (prevClose 0) → `dayChangePercent: null` |
| R4 | Weight = `marketValue / portfolio total` at request time, not forced to sum to 1 | P-9001 total 48,930.00 (27,300 + 21,630 + 0) → AAPL 0.557940 · BND 0.442060 | P-EMPTY → `[]` · total 0 → weights 0 |
| R5 | History range, inclusive, counted back from today: 1D = today − 1 day · 1M = − 1 month · YTD = from Jan 1 this year · 1Y = − 1 year · All = everything (default) | P-9001 `range=YTD` → first date ≥ Jan 1 | P-9002 has 60 days: `1Y` → those 60 days, no padding · `range=2Y` → 400 `invalid_range` · P-EMPTY → `[]` |
| R6 | Allocation: sum holding MV by asset class, `percent = value / total` | P-9001 → Equity 27,300.00 (0.557940) · Fixed Income 21,630.00 (0.442060) | P-SINGLE → one entry, `percent: 1.0` · P-EMPTY → `[]` |
| R7 | Auth: only `Authorization: Bearer <API_TOKEN>` passes | valid token → 200 | no header → 401 · `Token abc` / `Bearer` / wrong token → 401, never 500 · `/health` open |
| R8 | Cache: per portfolio id, TTL 30 s | 2 calls within 30 s → CRM `/__stats` +1 only | TTL expired + CRM fails → cached data, `stale: true` · cold cache + CRM fails → 503 · success after stale → replaces cache, `stale: false` |
| R9 | Ledger replay (Could): BUY adds to qty and weighted cost; SELL lowers qty, keeps avg cost | h1: BUY 100 @ 190, BUY 50 @ 220, SELL 30 → qty 120, avg 200.00 | sell to 0 → qty 0, avg `null` · oversell → rejected with error · out of order → sorted by date first (BUY 5 @ 10, SELL 2 → qty 3, avg 10) |

## 9. Assumptions (proposed: confirm, then document in the README)
- A1: one mock token, no users. In-memory data, reloaded from seed.json on start.
- A2: zero previous close → `dayChangePercent: null` in holdings ("unknown", not 0%); the CRM's `0`
  for P-9002 is passed through as given and noted as a known mismatch.
- A3: CRM fields that are null or missing map to `null` (never an invented 0); unknown nesting → 503.
- A4: `dayChangeAmount` follows the spec formula even when previous close is 0 (NEW → 500.00).
- A5: ZERO stays in P-9001's Equity allocation with value 0.
- A6: history ranges count back from today; the history file is regenerated so YTD uses this year.
- A7: on a successful CRM call after a stale period, the cache is replaced and `stale` goes back to
  `false`; `cachedAt` is the time of the CRM fetch.
- A8: CRM mapping is a field → candidate-paths table (first match wins); a new legacy name or nesting
  is one line. Numeric strings are parsed, unreadable values → `null`, currency is upper-cased.
  Percentages are taken as decimals as the spec says; units can't be detected, so no guessing.
- A9: `range` is an exact, case-sensitive match (`ytd`, empty, `2Y` → 400 `invalid_range`); range is
  checked before the portfolio lookup, so a bad range is 400 even for an unknown id.
- A10: 1M and 1Y step back by calendar month/year and clamp to a shorter month's last day
  (31 Mar − 1M = 28 Feb; 29 Feb 2028 − 1Y = 28 Feb 2027). "Today" is the UTC date.
- A11: history that exists but has no points inside the window returns 200 `[]` (e.g. a stale
  history file with `range=1D`); nothing is padded and no older point is substituted.
- A12: the CRM cache (Task 9) is in memory, per portfolio id, TTL 30 s (fresh while under 30 s).
  It caches the mapped metadata. Expired copies are kept with no maximum age, as the stale fallback
  for a CRM error, timeout or unreadable reply. A CRM 404 is never cached and removes any copy.
  Concurrent misses may both call the CRM (no lock); the cache empties on restart.
