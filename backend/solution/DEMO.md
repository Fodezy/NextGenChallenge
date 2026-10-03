# Demo script (4 minutes): the dashboard

Everything is shown in the web app at **http://localhost:5173**. The audience never sees an API
request. Three speakers: **Eric** (header, CRM, cache), **Vishek** (holdings), **Betty**
(performance, allocation). Edit the names if the split changes.

## Before the demo (5 minutes earlier)

1. `node backend/fixtures/generate-history.mjs` (repo root), so the chart ends today.
2. Start the mock CRM, the API and the web app (README "Run it"). Put the CRM in normal mode:
   ```powershell
   Invoke-RestMethod -Method Post http://127.0.0.1:4002/__control -ContentType 'application/json' -Body '{"mode":"ok"}'
   ```
3. Open the dashboard in a full-screen browser window and load **P-9001** once, so the cache holds
   a copy for the stale moment.
4. Keep a terminal **off screen** with the two presenter switches ready (used only in step 4 of the
   walkthrough):
   ```powershell
   # CRM down
   Invoke-RestMethod -Method Post http://127.0.0.1:4002/__control -ContentType 'application/json' -Body '{"mode":"error"}'
   # CRM back
   Invoke-RestMethod -Method Post http://127.0.0.1:4002/__control -ContentType 'application/json' -Body '{"mode":"ok"}'
   ```
   The UI has no button to break the CRM, so this is the one thing done off screen. Run the "CRM
   down" switch **30 seconds before** step 4, or the cached copy is still fresh and no banner appears.

## 1 · Problem (30 s) · Eric

> "An investor wants one screen that says what they own, what it's worth and how it has changed.
> The data comes from a legacy CRM that uses odd field names and fails one call in five. We built a
> backend that hides all of that, and this dashboard on top of it."

## 2 · Walkthrough, clicks only (2 min)

**Eric: the header**
1. Dashboard on **P-9001**: "Jane Doe, **$48,930.00** in total, up **$30.00 today**, **+18.70%**
   since inception. That comes from the CRM, mapped into our own clean schema."
2. Picker → **P-9002**, then back to **P-9001**: "Each card loads on its own, so the page is never
   blank while one source is slow."

**Vishek: holdings**
3. Holdings table: "AAPL: 120 shares × $227.50 = **$27,300.00**, **55.79%** of the portfolio, up
   **$3,300.00** on what was paid. Every number is calculated on the server."
   - Type `bnd` in the search box: "Showing 1 of 3". Click **Clear filters**.
   - Tick **Hide closed positions**: "ZERO is a sold-out position: 0 shares, so every figure is 0
     instead of an error, and its day change shows a dash." Untick it.
   - Click the **Market value** header to flip the sort.

**Betty: performance and allocation**
4. Performance chart: click **YTD** ("starts on January 1, not on the first data point"), then
   **1M**, then back to **All**. Hover the line to read a day's value.
5. Allocation: "Equity 55.79%, Fixed Income 44.21%: the same total as the holdings." Click **Pie**,
   then **Bar**.
6. Picker → **P-9002**, click **1Y**: "This account has only 60 days of history, so 1Y shows the 60
   we have and says so. No invented data." Point at the NEW row: "its day change is a dash because
   its previous close is zero. That's 'unknown', not '0%'."
7. Picker → **P-EMPTY**: "An empty account: every card shows a clear empty state, no errors."

**Eric: the CRM goes down (the resilience moment)**
8. Back on **P-9001** (CRM switched to `error` 30 s ago, off screen): pick **P-9002** and then
   **P-9001** again. The amber banner appears: "**Showing saved data from …**. The CRM is down, so
   we show the last good copy and say how old it is." Point at the tiles: "The numbers are still
   there, and holdings, chart and allocation below are unaffected because they don't use the CRM."
9. Run the "CRM back" switch off screen, pick another portfolio and return: the banner is gone.

## 3 · How it works (30 s) · Vishek

> "One contract, agreed before coding: every endpoint, field and error shape is written down. That
> let three of us build in parallel, and this dashboard was built against that contract before
> holdings and allocation existed, then switched to the real endpoints. Every response is checked
> against the contract, so a mismatch shows up as a named field, not a blank table. Calculations
> are pure functions and the business rules were written test-first."

Show the test results in a terminal: `pytest` → **126 passed**; `npm test` (in `web/`) → **16 passed**.

## 4 · AI (30 s) · Betty

> "We used Claude Code throughout, with a shared rulebook: it reads the brief before every task,
> writes tests first and waits for our OK, never edits an approved test to make it pass, and logs
> every step to a shared file so three sessions stayed in sync. We decided, it drafted, we
> reviewed. The product itself has no AI feature: we spent the time on correctness and resilience."

## 5 · Next (30 s) · Eric

> "Auth is the one Must we didn't finish. The design is ready and the dashboard already sends the
> token, so it's a backend-only change. After that: a household view, which replaces the
> hard-coded portfolio picker; USD display; and ledger replay, so quantities come from transactions."

## If something goes wrong

- **Chart empty on 1D or YTD:** the history file is from another day. Regenerate it (step 1) and
  restart the API.
- **No amber banner:** the cached copy is under 30 s old. Wait, then pick another portfolio and
  return to P-9001.
- **Red "Portfolio summary unavailable" card:** the CRM is in `error` mode and nothing is cached.
  Run the "CRM back" switch and click **Try again**. That is also worth showing.
- **The CRM fails by itself:** it does so one call in five. That is the stale banner; explain it.
