# Demo script (4 minutes)

Three speakers: **Eric** (CRM + cache + web UI), **Vishek** (holdings), **Betty** (history +
allocation). Edit the names if the split changes.

## Before the demo (5 minutes earlier)

1. `node backend/fixtures/generate-history.mjs` (repo root) so the chart ends today.
2. Start the mock CRM, the API and the web app (README "Run it"). Set the CRM to normal:
   ```powershell
   Invoke-RestMethod -Method Post http://127.0.0.1:4002/__control -ContentType 'application/json' -Body '{"mode":"ok"}'
   ```
3. Open three tabs: **http://localhost:5173** (dashboard), **http://127.0.0.1:3000/docs** (API docs),
   **http://127.0.0.1:4002/__stats** (CRM call counter).
4. Load P-9001 once, so the cache holds a copy for the stale demo.
5. Have a terminal ready with the `error` and `ok` commands below, and `pytest` ready to run.

## 1 · Problem (30 s) · Eric

> "An investor wants one screen that says what they own, what it's worth and how it's changed. The
> data lives in a legacy CRM that uses odd field names, nests things inconsistently and fails one
> call in five. We built the backend that hides all of that, and a dashboard on top of it."

## 2 · Walkthrough (2 min)

**Eric: the header (Tasks 1 and 9)**
1. Dashboard on **P-9001**: "Jane Doe, $48,930.00, up $30.00 today, +18.70% since inception. All
   from the CRM, mapped into our own clean schema."
2. Refresh twice, then show the **/__stats** tab: "Two page loads, one CRM call. We cache for
   30 seconds."
3. Break the CRM:
   ```powershell
   Invoke-RestMethod -Method Post http://127.0.0.1:4002/__control -ContentType 'application/json' -Body '{"mode":"error"}'
   ```
   Wait 30 s (talk through the holdings meanwhile), then pick P-9001 again: **amber banner, "Showing
   saved data from …"**. "The CRM is down, so we show the last good copy and say how old it is.
   Everything below still works: it doesn't depend on the CRM." Switch the CRM back to `ok`.

**Vishek: holdings (Task 2)**
4. Holdings table: "AAPL is 120 shares × $227.50 = $27,300.00, 55.79% of the portfolio, up
   $3,300.00 on cost. Every number is calculated on the server at request time."
5. Edge case: "ZERO is a closed position: 0 shares, so every calculated field is 0 rather than an
   error." Tick **Hide closed positions**, then click **Clear filters**.

**Betty: performance and allocation (Tasks 3 and 5)**
6. Performance chart: click **YTD** ("starts on January 1, not on the first data point"), then **1M**.
7. Allocation: Equity 55.79%, Fixed Income 44.21%; click **Pie**. "Same total as the holdings."
8. Picker → **P-9002**, click **1Y**: "Only 60 days of history, so 1Y shows the 60 days we have, no
   padding." Point at NEW's day change: "—, because its previous close is 0: unknown, not 0%."
9. Picker → **P-EMPTY**: empty states everywhere, no errors.

## 3 · How it works (30 s) · Vishek

> "One contract, agreed before coding: every endpoint, field and error shape is in BRIEF.md. That
> let three of us build in parallel, and the dashboard was built against that contract before
> holdings and allocation existed. Calculations are pure functions, tested without HTTP; the
> business rules were written tests-first from worked examples."

Run `pytest`: **126 passed**. Show `/docs` for the contract.

## 4 · AI (30 s) · Betty

> "We used Claude Code throughout, with a shared rulebook: it reads the brief before every task,
> writes the tests first and waits for our OK, never edits an approved test to make it pass, and
> logs every step to a shared LOG.md so three sessions stayed in sync. We decided, it drafted, we
> reviewed. The product has no AI feature: we put the time into correctness and resilience."

## 5 · Next (30 s) · Eric

> "Auth is the one Must we didn't finish. The design is ready, and the frontend already sends the
> token, so it's a backend-only change. After that: the household view, which replaces our
> hard-coded portfolio picker; USD display; and ledger replay, so quantities are derived from
> transactions."

## If something goes wrong

- **Chart empty on 1D or YTD:** the history file is from another day. Regenerate it (step 1) and
  restart the API.
- **Header shows "Portfolio summary unavailable":** the CRM is in `error` mode with no cached copy.
  Switch it to `ok` and click **Try again**. That's also a fine thing to show.
- **The CRM fails mid-demo in `auto` mode:** that's the stale banner. Explain it; it's the feature.
