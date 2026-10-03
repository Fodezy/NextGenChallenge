# Prompts (paste into Claude Code)

## 1 · Brief (minutes 10–15)
```
Challenge: [paste]. Fill in BRIEF.md §1–5 and §9: the problem and one outcome we can show live; up
to 2 personas; MoSCoW with at most 3 Musts forming one demoable flow (auth, live data and payments
go in Won't); 1–3 AI ideas that explain or summarise for the user, recommending one; the flow;
assumptions. Ask at most 3 questions.
```
→ We read it aloud, cut, and agree.

**1b · Contract and rules** (after we agree the scope)
```
Draft BRIEF.md §7 and §8 for the Musts only. §7: the tables (key columns) and one row per endpoint
(method, path, response shape). §8: the business rules, each with a worked example whose numbers add
up and one edge case. Then wait.
```
→ We read both together, cut, and agree. This is the contract both sides build against.

## 2 · Scaffold (minute 5, second terminal)
```
Set up an empty npm-workspaces monorepo, no features:
- web/: Vite + React + TypeScript + Tailwind; one page showing GET /api/health.
- api/: Express + TypeScript (tsx), SQLite with better-sqlite3 (if it needs compiling, use node:sqlite
  instead), schema.sql run on start, empty seed.ts, CORS.
- shared/: Zod types used by both.
- Vitest with one passing test. Root scripts: dev (api :3001 + web :5173), test, seed. git init.
- Pin the Node version: .nvmrc and "engines" in package.json.
- Scripts run the same on macOS, Linux and Windows: no inline env vars, no rm -rf, concurrently for
  dev. Secrets in api/.env (gitignored), loaded on start; commit api/.env.example.
- .gitattributes with "LOG.md merge=union", so both sessions' log lines merge without conflicts.
Confirm "ok" shows in the browser and fill in CLAUDE.md Commands.
```
→ We check; Claude asks "Commit?". Tip: allow `npm`, `npx`, `node` and `git init` in
`.claude/settings.json` so it doesn't wait for clicks. Leave `git commit` and `git push` off the list,
so they still ask.

**If they give us existing code instead:**
```
Map this codebase without changing anything, in 25 lines or fewer: stack, run and test commands
(try them), where screens, routes, data and logic live, and conventions to copy. Then fill in
CLAUDE.md Commands and add a Conventions section.
```

## 3 · Contract and mocks (minutes 20–25, after we agree BRIEF.md §7)
Run once, before we split: the only prompt that touches api/, shared/ and web/.
```
From BRIEF.md §7: schema.sql (cents, text ids, ISO dates), Zod types in shared/, a deterministic
seed.ts with realistic data, web/src/mocks.ts shaped exactly like the responses, and every endpoint
stubbed against the database. This prompt may write to all three folders.
```

## 4 · Business rules (backend)
```
Write failing tests for the BRIEF.md §8 rules from their examples plus edge cases, named after each
rule. No implementation yet. List them (test · why), then wait.
```
→ We read the list and say "OK, build it". Claude builds, runs and reports.

## 5 · Screens (frontend): questions → rough pass → review → build
Each step ends in a stop (CLAUDE.md "Screens").

**5a · Questions**
```
Before any UI, ask me the CLAUDE.md screen questions plus up to 3 of your own that this brief needs.
Give your recommended answer for each, numbered, so I can reply "all yes" or "yes except 3: …".
Then wait.
```
**5b · Rough pass**
```
Make a rough pass of all the BRIEF.md §5 screens from our answers: [a Claude Design canvas, copied
to design/ | static HTML + Tailwind in design/ | a prompt I can paste into <tool>]. Musts only,
realistic numbers from seed.ts. Then stop.
```
**5c · Review**
```
Review design/ against the CLAUDE.md screen checklist. List at most 8 issues (issue · fix), most
important first. Wait, then fix only the ones I pick.
```
→ Repeat until we say "approved". Claude asks "Build the web UI?"

**5d · Build** (after our yes)
```
design/ is approved: match its layout and look, not its exact code. Build the BRIEF.md §5 screens in
web/src (React + Tailwind) on mocks.ts, with web/src/api.ts holding one function per §7 endpoint.
Musts only. One screen at a time: build screen 1, click through its happy path in the browser (if
you can't open one, say so and give me the click steps), report, then stop. Next screen after our OK.
```
**Join up (minute 45):**
```
Switch web/src/api.ts to the real API (localhost:3001), same signatures, validated with the shared
Zod types. List any field mismatches.
```
**Polish (window 2):** `Polish the screens, no new features: states, number formatting, spacing, contrast, focus.`

## 6 · AI feature (window 2)
**Smoke test first, once we have a key** (in `api/.env` as `ANTHROPIC_API_KEY`, so no shell differences):
```
Run one call with @anthropic-ai/sdk: model "claude-opus-5-5", max_tokens 16000,
output_config { effort: "low" }, message "Reply with OK." Print stop_reason and the text.
```
**Build:**
```
Build the BRIEF.md §4 AI feature. facts.ts builds the facts from our tested rules (ids, not names),
with a test. summarize.ts calls @anthropic-ai/sdk with the same settings and the system prompt
"Explain these facts in plain language. Use only these numbers; never calculate new ones. 3 short
bullets." No key, stop_reason "refusal" or Anthropic.APIError → 503 { error: { code:
"ai_unavailable" } }. POST /api/<thing>/:id/summary → { summary, facts }. UI panel: "AI draft",
the facts beside it, Regenerate, and Approve (saves approvedAt in an ai_summaries table and shows
"Approved 14:32"). Unavailable → "AI summary unavailable"; the rest of the page still works.
```

## 7 · Review and handover (minutes 40–50, after the freeze)
```
Review the code; no code changes. Write README.md (final): run commands (macOS/Linux and Windows
PowerShell wherever they differ, starting from a fresh clone), what's done (each Must and
Should with its status), assumptions, next steps (the Won'ts plus your findings). Write REVIEW.md, a
5-minute read: 1 architecture in 5 lines plus a folder map · 2 API: each endpoint, what it does, its
errors, any drift from BRIEF.md §7 · 3 database: tables, key columns, why cents and text ids ·
4 business rules: rule → code location → test name → pass/fail · 5 frontend: screens → components,
style decisions, format helper, states · 6 AI: facts → prompt → fallback → approve · 7 findings:
bugs, risks, shortcuts, each with a severity, not fixed · 8 likely panel questions with short
answers (why this stack, scaling, security, what next). Then list any finding that would break the
demo, and wait.
```
→ We cross-read: I take frontend and AI (§5–6), my partner takes API, database and rules (§2–4).
Fix only demo-breakers, with our OK; everything else stays in next steps.

## 8 · Demo (minutes 50–60)
```
From BRIEF.md, REVIEW.md and the git log: DEMO.md, a 4-minute script following the cheat-sheet
outline (who says what, exact clicks). No code changes.
```
