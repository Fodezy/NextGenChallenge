# CLAUDE.md

A three-person backend build for a wealth-management portfolio dashboard (Electric Mind Super Day,
backend track). **Read BRIEF.md before every task**: it holds the scope and owners, the architecture,
the API contract and the business rules. **Read the last 10 lines of LOG.md** too: what the other
sessions changed.

## How we work
- **Be brief.** Report in 3 lines at most: what changed · how to check it · what's next. No filler.
- **Commit only with permission.** After a step, report, then ask "Commit?". Commit only after a yes.
  One branch per person, small merges to `main`, pull before each prompt.
- **Log every step.** After each step, add one line to the end of LOG.md, prefixed with who:
  `[me]`, `[A]`, `[B]` or `[plan]`, e.g. `[A] GET /portfolios/:id/holdings live: ZERO row all 0`.
  Never edit earlier lines.
- **Stay in your files.** All work is in `backend/solution/`. Each router and service has one owner
  (BRIEF.md §6). Shared files: `app/main.py` (one `include_router` line each), `app/schemas.py`
  (add your own models, don't change others'), `app/errors.py` and `app/data/repository.py` (change
  only after we agree). A contract change: update BRIEF.md §7, log it, and say so.
- **Keep going.** Stop and ask (one line) only before: an endpoint or table not in BRIEF.md, a
  contract change, or work outside your current task. A prompt that lists its own scope counts as
  approval, **except at the stop points in Business rules and Screens below**.
- **Fix setup problems** (imports, config, packages) silently.

## Business rules: tests first
Rules are in BRIEF.md §8.
1. Write the tests from the examples, list them (test · why), then **stop for our OK**.
2. Build, run, report passed / failed.
3. On a failure: expected vs actual, plus a diagnosis (code bug · test bug · spec gap). Then stop.

**Never change an approved test to make it pass.**

## Screens: design first (only once the backend Shoulds are done)
**Never write web/src code beyond the scaffold before the design is approved.**
1. **Questions.** Ask these, plus up to 3 of your own that fit this brief. **Give your recommended
   answer for each**, numbered, so we can reply "all yes" or "yes except 3: …". Then stop.
   1. Who uses this screen, and what's the one thing they must see or do?
   2. The demo happy path, click by click?
   3. The hero number or view: a card, a table, or which chart?
   4. Desktop-first or mobile-first?
   5. The look: neutral fintech, light or dark, an accent colour?
   6. Which edge case do we show: empty, error, or a flagged item?
2. **Rough pass** of all the screens at once, from the answers. Then stop.
3. **Review** it against the checklist: list issues (issue · fix, at most 8, most important first) and
   fix only the ones we pick. Repeat until we say "approved".
   Checklist: flow matches §5 and the demo path · Musts only, nothing invented · every number exists
   in §7 · money uses the format helper · loading, empty and error states · one primary action per
   screen · contrast and spacing.
4. After "approved", ask "Build the web UI?" Build only after a yes, **one screen at a time**: build
   it, click through its happy path in the browser, report, stop. Next screen after our OK. If you
   can't open a browser, say so and give us the click steps; never claim you checked it.

## Review (after the freeze)
No code changes. List findings with a severity; don't fix them. Fix only what breaks the demo, and
only after our OK. Everything else goes in README.md next steps.

## Code
- **Backend:** Python 3.14, FastAPI, Pydantic v2, async httpx (CRM only), pytest, Ruff. Type hints
  everywhere. Routes are thin; calculations are pure functions in `app/services/`, unit tested
  without HTTP.
- **Frontend:** TypeScript strict, React, Tailwind, Vitest, npm (`backend/solution/web/`).
- **Responses:** JSON camelCase via `CamelModel` subclasses in `app/schemas.py` and `response_model=`.
- **Money:** decimal CAD, rounded to 2 dp only when the response is built; percentages are unrounded
  decimals (0.0032 = 0.32%). Never invent a 0 for missing data: use `null` and document it.
- **Errors:** raise `ApiError(status, code, message)`; every error is flat
  `{ "error": "<code>", "message": "<text>" }`. Codes are listed in BRIEF.md §7.
- **Before every merge:** `ruff format .`, `ruff check .`, `pytest` all clean.
- Any choice the spec leaves open goes in BRIEF.md §9 and the README.

## Commands
npm scripts work the same everywhere. Wherever a command differs (env vars, copying or deleting
files), write it twice: **macOS / Linux (bash, zsh)** and **Windows (PowerShell)**. Same in README.md.

Backend: `backend/solution/` (FastAPI, Python 3.14). Web: `backend/solution/web/` (Vite, React, TS).
Mock token: `superday-demo-token`. Ports: API 3000, mock CRM 4002, web 5173.

- **Setup venv + install** (in `backend/solution/`):
  - bash: `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements-dev.txt`
  - PowerShell: `py -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements-dev.txt`
- **Activate venv later:** bash `source .venv/bin/activate` · PowerShell `.\.venv\Scripts\Activate.ps1`
- **Run API** (venv active, in `backend/solution/`): `uvicorn app.main:app --port 3000 --reload`
- **Test:** `pytest` · **Lint/format:** `ruff format .` then `ruff check .` (venv active)
- **Generate history** (repo root, needed for history endpoints): `node backend/fixtures/generate-history.mjs`
- **Mock CRM** (repo root): `node backend/mock-crm.mjs`
- **Web** (in `backend/solution/web/`): `npm install` · `npm run dev` · `npm test` ·
  `npm run typecheck` · `npm run build`
- **Web token override:** bash `cp .env.example .env.local` · PowerShell `Copy-Item .env.example .env.local`
