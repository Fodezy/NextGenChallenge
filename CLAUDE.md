# CLAUDE.md

A 2-hour pair build for a wealth-management platform. **Read BRIEF.md before every task**: it holds
the scope, the API contract and the business rules. **Read the last 10 lines of LOG.md** too: what the
other session changed.

## How we work
- **Be brief.** Report in 3 lines at most: what changed · how to check it · what's next. No filler.
- **Commit only with permission.** After a step, report, then ask "Commit?". Commit only after a yes.
- **Log every step.** After each step, add one line to the end of LOG.md:
  `[api] POST /decision live: 409 when already decided`. Never edit earlier lines.
- **Stay in your folder.** The backend session works in `api/`, the frontend session in `web/`.
  `shared/` is the contract: change it only after we agree. Update BRIEF.md §7, log it, and say so.
- **Keep going.** Stop and ask (one line) only before: a screen, endpoint or table not in BRIEF.md,
  a contract change, or work outside the current Must. A prompt that lists its own scope counts as
  approval, **except at the stop points in Business rules and Screens below**.
- **Fix setup problems** (imports, config, packages) silently.

## Business rules: tests first
Rules are in BRIEF.md §8.
1. Write the tests from the examples, list them (test · why), then **stop for our OK**.
2. Build, run, report passed / failed.
3. On a failure: expected vs actual, plus a diagnosis (code bug · test bug · spec gap). Then stop.

**Never change an approved test to make it pass.**

## Screens: design first
**Never write web/src code before the design is approved.**
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
- TypeScript strict. npm.
- **Money:** integer cents everywhere, rounded to cents when created; percentages unrounded until
  display. One format helper: en-CA, CAD, "+" on gains, "−" on losses.
- API errors are `{ error: { code, message } }`. Every screen has loading, empty and error states.
  No buttons that do nothing.
- **AI:** rules calculate, the AI explains, a human approves (marked "AI draft"). No names or emails
  in prompts. With no API key, the feature shows "unavailable" and everything else works.

## Commands
npm scripts work the same everywhere. Wherever a command differs (env vars, copying or deleting
files), write it twice: **macOS / Linux (bash, zsh)** and **Windows (PowerShell)**. Same in README.md.

_Filled in by the scaffold (PROMPTS.md prompt 2) or the codebase map._
