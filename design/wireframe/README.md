# Portfolio dashboard wireframe (rough pass, not yet approved)

**Live canvas:** https://claude.ai/artifact/MsRKZyrShvDELK1n3KRuvW (private until shared from its
Share menu). The files here are its source: one `.dc.html` per artboard, laid out by `canvas.json`.
They are Claude Design component files; they don't open as plain HTML pages.

Static mockups with real numbers from `backend/fixtures/seed.json`, the mock CRM and the generated
performance history. Desktop-first, neutral fintech, light, one teal accent, CAD only.

| Artboard | Shows | Data from |
|---|---|---|
| `Main.dc.html` | Happy path, P-9001: header card, performance chart (range buttons), allocation bar, holdings table sorted by market value | all four endpoints |
| `Stale.dc.html` | Task 9: CRM down, cached copy shown with an amber "saved data from 1:31 PM" banner | `GET /portfolios/:id` (`stale`, `cachedAt`) |
| `CrmDown.dc.html` | CRM down, nothing cached (503): error card with Try again; rest of page still loads | `GET /portfolios/:id` |
| `Loading.dc.html` | Skeleton blocks | — |
| `Empty.dc.html` | P-EMPTY: $0.00, no history, nothing to allocate, no holdings | all four |
| `NewSecurity.dc.html` | P-9002: NEW's day change % as "—" (previous close 0); 1Y shows only 60 days | holdings, history |
| `AllocationPie.dc.html` | Allocation in Pie view: P-9001 (two slices) and P-SINGLE (full circle) | `/allocation` |
| `HoldingsFiltered.dc.html` | Holdings filtered (Equity + hide closed → 1 of 3) and a search with no match, with Clear filters | `/holdings` |

**Decisions (screen questions, agreed):** investor checks one portfolio; hero = header card with
total value and today's change; desktop-first; all edge states drawn; portfolio picker is
hard-coded (a real list needs Task 6); holding rows not clickable (Task 8 is Won't); no CAD/USD
switch (Task 7 is a Could).

**Review changes (2026-10-03)**, live canvas with them: https://claude.ai/artifact/DoNXXJ4aLxynedM1N716Lu
(private until shared):
- Header: the client name ("Jane Doe") is the largest text; "Portfolio dashboard" is a small label above it.
- KPIs: Total value, Today and Since inception are three separate bordered tiles (one column under 860 px).
- Allocation: a Bar / Pie toggle in the card header; Bar stays the default (artboard 7 shows Pie).
- Holdings: a filter bar (search by ticker or name, asset-class buttons built from the classes present,
  "Hide closed positions"), a "Showing N of M" count and Clear filters. Filtering is client-side on the
  loaded rows; weights stay relative to the whole portfolio. Artboard 8 shows the filtered and no-match states.

**Open review points** (issue · proposed fix), not yet decided:
1. ZERO (0 shares) shows "+20.00%" today · show "—" for 0-quantity rows in the UI.
2. P-9002 header shows "(0.00%)" from the CRM next to +$500.00, but holdings show "—" · pick one
   display rule, or document the mismatch (A2).
3. Client name is now shown ("Jane Doe"), but the API returns only `clientId` · add `clientName` from
   the CRM's `full_name` to `GET /portfolios/:id` (a Task 1 contract change: BRIEF §7 first).
4. The header waits up to 2 s on the CRM · each card loads on its own.
5. 1D on daily data is one or two points · define 1D in BRIEF R5, or show a "Today" summary.
6. Only "Market value" sorts · make that clear in the header.
