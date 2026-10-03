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
[me] Task 1 GET /portfolios/{id} live: table-driven CRM mapper (ok/nested/missing), 404 not_found, 503 crm_unavailable on error or 2 s deadline; shared httpx client + CRM default 127.0.0.1 (localhost cost ~450 ms on Windows); 45 tests green
