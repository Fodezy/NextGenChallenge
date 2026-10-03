# DECISIONS

Architecture decisions, newest at the bottom. Each one: what we chose · why · what we rejected.
Assumption IDs refer to BRIEF.md §9.

## D1 · Task 3: history ranges count back from the real date (A6, A11)
- **Chose:** windows are inclusive and counted back from today's UTC date. The router gets `today`
  through a FastAPI dependency (`get_today`), so tests fix the date.
- **Why:** it is what 1D/1M/YTD mean to an investor; the date is injectable, so tests stay stable.
- **Rejected:** counting back from the latest date in the data. It never returns empty, but shows
  old data as current. Consequence: a stale history file returns `[]` for `1D`; regenerate the file
  on demo day (`node backend/fixtures/generate-history.mjs`).

## D2 · Task 3: strict range validation, before the lookup (A9)
- **Chose:** exact, case-sensitive `range` values; validate before loading the portfolio.
- **Why:** the spec forbids silent fallbacks; validating first is cheaper and gives one answer for
  a bad request regardless of id.
- **Rejected:** case-insensitive matching (looser contract, more to test); FastAPI `Literal` query
  typing (its 422 message is harder to turn into our `invalid_range` code).

## D3 · Task 3: calendar month/year steps with month-end clamping (A10)
- **Chose:** 1M = same day last month, 1Y = same day last year, clamped to the month's last day.
- **Why:** matches how people read "one month"; never crashes on 31 March or 29 February.
- **Rejected:** fixed 30/365-day windows (drift against calendar months and leap years).

## D4 · Task 3: the filter is a pure function; the route only orchestrates
- **Chose:** `app/services/history_filter.py` (`is_valid_range`, `range_start`, `filter_by_range`)
  takes points, range and today; `app/routers/history.py` validates, loads, filters, rounds.
- **Why:** unit-testable without HTTP (BRIEF §6); output is sorted oldest first even if the file
  is not; `marketValue` is rounded to 2 dp only when the response is built.

## D5 · Task 9: in-memory TTL cache with a stale fallback (A7, A12)
- **Chose:** `app/services/cache.py` `TtlCache`, pure, time from an injected clock (one clock for
  freshness and `cachedAt`, like D1's `get_today`). The route serves a fresh copy without calling
  the CRM; otherwise it calls and maps, saves on success, falls back to any older copy as
  `stale: true` on `CrmUnavailableError` (error, timeout, unreadable shape), and deletes the copy
  on a 404. `get_portfolio_cache` is a FastAPI dependency so tests swap in a fake-clock cache.
- **Why:** the spec's three checks (one CRM call within the TTL, stale after expiry, clear error
  when cold) are testable in milliseconds; the stale copy is the last thing the CRM confirmed.
- **Rejected:** caching the raw CRM body (re-maps on every hit, and a bad body could be cached);
  a max stale age or eviction (4 ids, and the spec asks for the fallback); a per-id lock against
  concurrent misses (not needed at this scale; noted in A12).
