# Personas: demo walkthroughs

Three walkthroughs of the demo path (BRIEF.md §5), using the seed data. Musts and Shoulds only.

## 1. Advisor: Priya, wealth advisor, prepping a client call
*Needs:* trust the numbers while the CRM is flaky, and spot oddities before the client does.
1. She calls the API with no token and gets a 401. Only the token holder gets in.
2. `GET /portfolios/P-9001` shows Jane's mapped metadata: value, day change, return since inception.
3. The mock CRM is set to `error` and the 30 s TTL passes. The same data still comes back, with
   `stale: true` and a `cachedAt` time, so she can say "as of 2 minutes ago".
4. `GET /portfolios/P-9001/holdings` shows AAPL 120 × 227.50 = 27,300.00 (gain 3,300.00). The ZERO
   row is all zeros. She asks why it's there, and the answer is that it's a sold-out position (A5).
5. `GET /portfolios/P-9002` shows `dayChangePercent` as `null` where the CRM says 0. She knows this
   is a data-quality flag (A2), not a 0% move.

## 2. Client: Jane Doe (`abc123`), checking her portfolio on her phone
*Needs:* "What do I own, what's it worth, how has it done?" The numbers must be right.
1. Her portfolio P-9001 shows a total of 48,930.00.
2. Holdings split it into AAPL at 55.79% and BND at 44.21%. The weights come from
   `marketValue / total`.
3. Allocation shows Equity 27,300.00 and Fixed Income 21,630.00, matching her holdings.
4. `performance-history?range=YTD` shows her year so far, starting on or after Jan 1.
5. Her second account, P-9002, has only 60 days of history. `range=1Y` returns those 60 days with no
   padding, so the chart is honest about a young account.
6. A new account like P-SINGLE shows one allocation slice at 100%. P-EMPTY returns `[]` (an empty
   state, not an error).

## 3. Dashboard developer: Sam, building the web UI against the API
*Needs:* consistent JSON, predictable errors, and nothing that hangs.
1. `GET /health` works with no token. Every other route returns a flat `{error, message}`.
2. A bad token (`Token abc`, bare `Bearer`) returns 401, never 500.
3. `range=2Y` returns 400 `invalid_range`, and an unknown id returns 404 `not_found`.
4. With the CRM in `timeout` mode, the answer comes back in about 2 s. With a cold cache and the CRM
   down, it returns 503 `crm_unavailable`. Both are states he must build UI for.
5. He opens `/docs` to see the camelCase contract. He runs `pytest` and sees 94 green.

## Optional: Ops/support engineer
Watches CRM `/__stats` to prove the cache cuts calls (2 requests within 30 s means +1 CRM call).
