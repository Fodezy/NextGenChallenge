# LOG

Shared memory between the two Claude sessions (and the two of us). **Append-only, one line per step,
newest at the bottom.** Prefix with who: `[api]`, `[web]` or `[plan]`. Read the last 10 lines before
each task.

[plan] MoSCoW: Must 1 CRM metadata, 2 holdings, 4 auth · Should 9 cache, 5 allocation, 3 history · Could 10 ledger, 6 household, 7 currency · Won't 8 holding detail
[plan] Split (3 people, backend track, code in backend/solution/): me 1 → 9 · partner A 2 → 4 · partner B 5 → 3
[plan] Next together: high-level architecture, then tech stack, before anyone codes
[plan] Split changed: partner B does 3 first, then 5 (5 depends on partner A's holdings calc)
[plan] Auth shape (header, token, where it mounts) agreed for all endpoints before anyone builds routes
[plan] Error shape everywhere: flat { error: "<code>", message } (Task 4's schema), not the kit's nested one
[plan] Stack: Python backend, TypeScript frontend, SQLite only when needed (in-memory seed data first)
[plan] BRIEF.md filled: scope + owners, FastAPI/httpx(async)/pytest architecture, API contract §7, rules R1–R9, assumptions A1–A7 (to confirm)
[plan] Stack changed: Flask (not FastAPI) + Pydantic response models + Ruff; CRM call now sync httpx 2 s timeout on threaded server (async gives Flask no benefit). BRIEF §6 updated
[plan] Back to FastAPI (Flask dropped): FastAPI + async httpx + Pydantic + pytest + Ruff. BRIEF §6 updated
[plan] Architecture diagrams for Tasks 1–3 (overview, CRM outcome flow, holdings 2-pass calc, history range windows): https://claude.ai/artifact/AvG2oPk61AuAuGyWCN3KdW
[plan] ARCHITECTURE.md added: Mermaid versions of the Tasks 1–3 diagrams, range table, responses per endpoint, open points
[plan] Moved ARCHITECTURE.md → architecture/ARCHITECTURE.md; future architecture decisions go in architecture/
[api] Skeleton up in backend/solution: FastAPI app, flat error handlers, seed repository, /health, 7 tests green, ruff clean; web/ shell (Vite+React+TS+Tailwind, /api proxy to :3000, 3 vitest green)
[plan] CLAUDE.md updated for the 3-person Python/FastAPI build: owners, shared files, flat errors, decimal CAD, Ruff + pytest before merge
[plan] Root .gitignore: ignore generated backend/fixtures/performance-history.json
[plan] .gitattributes: LOG.md merge=union, so parallel log lines merge without conflicts
[B] GET /portfolios/{id}/performance-history live: R5 ranges (UTC today, month-end clamp), 400 invalid_range before 404, 20 tests (39 total) green, ruff clean; A8–A10 in BRIEF §9, D1–D4 in architecture/DECISIONS.md
[me] Task 1 GET /portfolios/{id} live: table-driven CRM mapper (ok/nested/missing), 404 not_found, 503 crm_unavailable on error or 2 s deadline; shared httpx client + CRM default 127.0.0.1 (localhost cost ~450 ms on Windows); 45 tests green

[plan] Pulled origin/main: fast-forwarded main to 94a18d9

[plan] Checked git status: main up to date; LOG.md has the required local step entry

[me] Frontend Task 2: approved summary design integrated in web scaffold; existing portfolio API, currency/decimal-percent formatting, neutral zero, null fallback, loading and Retry; no backend contract changes.
[me] Added blank backend .env and .env.example for optional OPENROUTER_API_KEY; Git ignore and run instructions; no credential saved or AI integration added.
[me] Frontend summary changes stashed locally; branch publishes environment template and setup documentation only, with original web scaffold active.
[plan] Wireframe rough pass (Claude Design, 6 artboards: happy path P-9001, stale, CRM down, loading, empty, P-9002 null day %): https://claude.ai/artifact/MsRKZyrShvDELK1n3KRuvW
[plan] Wireframe source committed to design/wireframe/ (README: artboards, agreed answers, 6 open review points) so the team can design from it
[B] Pulled main (Task 1) into task-3 branch: Task 3 assumptions renumbered A8–A10 → A9–A11 (main kept A8 for CRM mapping); 77 tests green
[A] Task 4 step 1: inspected auth placeholder and app registration; no authentication currently registered.
[A] Task 4 step 2: drafted 12 R7 tests for missing/malformed/wrong credentials, configured valid token, open health, and rejection before CRM/history access; awaiting test approval, middleware unchanged.
[A] Created holdings_calc.py function scaffold and 7 R3/R4 tests: AAPL/BND values, zero position/total, zero previous close, empty list, exact money and input preservation; implementation awaits test approval.
[A] Implemented calculate_holdings with Decimal two-pass values/weights; zero quantity fields zero, zero previous close percent null, empty/zero-total handled, inputs preserved, no early rounding; 7 approved tests passed and Ruff clean.
[B] Wireframe review changes on design/wireframe-kpi-allocation-filter: client name larger than title, bordered KPI tiles, allocation Bar/Pie toggle (+ artboard 7), holdings filter bar (+ artboard 8: filtered, no match); needs clientName in /portfolios/:id (open point 3)
[B] Wireframe v2 canvas (review changes, 8 artboards): https://claude.ai/artifact/DoNXXJ4aLxynedM1N716Lu
[me] Task 9 CRM cache live: 30 s TTL, stale fallback on error/timeout/garbage, cold 503, 404 evicts; live check vs mock /__stats (2 calls → +1, stale after expiry, P-SINGLE cold 503, refresh after recovery); 94 tests green
