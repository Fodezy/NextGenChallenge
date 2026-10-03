# Portfolio API (FastAPI) + web shell (Vite/React/TS)

Backend for the portfolio dashboard (see `BRIEF.md` at the repo root). Python 3.14, FastAPI,
httpx, Pydantic v2, pytest, Ruff. Service on **:3000**, mock CRM on **:4002**, web dev server on
**:5173**.

- **Mock auth token:** `superday-demo-token` (env `API_TOKEN`). Send `Authorization: Bearer superday-demo-token`.
  `/health` needs no token.
- **Errors** are always flat: `{"error": "<code>", "message": "<text>"}`.
- **Config** (env vars, defaults): `PORT=3000`, `CRM_BASE_URL=http://127.0.0.1:4002`,
  `CRM_TIMEOUT_SECONDS=2.0`, `API_TOKEN=superday-demo-token`, `CACHE_TTL_SECONDS=30`.

All commands run from `backend/solution/` unless noted.

## Install

macOS / Linux (bash, zsh):
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Windows (PowerShell):
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```
(If activation is blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.)

## Sample history (once per day)

From the repo root (same on every OS). Creates `backend/fixtures/performance-history.json`
(not in Git). Without it, history is `[]` and the server logs a warning.
```sh
node backend/fixtures/generate-history.mjs
```
Restart the server after regenerating.

## Run

With the venv active (same on every OS):
```sh
uvicorn app.main:app --port 3000 --reload
```
Open <http://localhost:3000/health> and <http://localhost:3000/docs>. The mock CRM runs from the
repo root: `node backend/mock-crm.mjs`.

Override a setting for one run:

macOS / Linux: `API_TOKEN=other uvicorn app.main:app --port 3000 --reload`

Windows (PowerShell): `$env:API_TOKEN = "other"; uvicorn app.main:app --port 3000 --reload`

## Test and lint

With the venv active (same on every OS):
```sh
pytest
ruff format .
ruff check .
```

## Web (backend/solution/web)

Vite + React + TypeScript (strict) + Tailwind. One page for now: it calls `/health` and shows
"API: ok" or an error. Vite proxies `/api/*` to `http://localhost:3000` with the `/api` prefix
stripped, so there is no CORS. `src/api.ts` sends `Authorization: Bearer $VITE_API_TOKEN`
(default `superday-demo-token`).

From `backend/solution/web` (same on every OS):
```sh
npm install
npm run dev        # http://localhost:5173 (start uvicorn first)
npm test
npm run typecheck
npm run build
```

Custom token: macOS / Linux `cp .env.example .env.local` Â· Windows (PowerShell)
`Copy-Item .env.example .env.local`, then edit `VITE_API_TOKEN`.

## Layout

```
app/main.py        app, error handlers, /health, router registration (one line per router)
app/config.py      settings from env vars
app/errors.py      ApiError + handlers (flat error shape)
app/schemas.py     CamelModel base (camelCase JSON), ErrorResponse
app/auth.py        Task 4 goes here (placeholder)
app/routers/       one file per owner: portfolios, holdings, history, allocation
app/services/      pure functions (tested) and the CRM client
app/data/repository.py  read access to seed.json and performance-history.json
tests/             test_<module>.py
web/               frontend shell
```
