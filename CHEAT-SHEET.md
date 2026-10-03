# Cheat sheet

**Setup (my laptop, minutes 0–10):**
1. Make the folder and copy the kit in (BRIEF, CLAUDE, LOG and PROMPTS, so my partner has the prompts):
   - Windows PowerShell: `mkdir <name>; cd <name>; $k="C:\Users\ericf\Personal\electric-minds-system"; Copy-Item "$k\BRIEF.md","$k\CLAUDE.md","$k\LOG.md","$k\PROMPTS.md" .`
   - macOS / Linux: `mkdir <name> && cd <name> && cp <kit>/BRIEF.md <kit>/CLAUDE.md <kit>/LOG.md <kit>/PROMPTS.md .`
2. Two Claude Code terminals in accept-edits mode: one scaffolds (**prompt 2**), the other drafts the brief (**prompt 1**).
3. After the scaffold's first commit, share it: `gh repo create <name> --private --source . --push`, then add my partner
   (`gh api -X PUT repos/<me>/<name>/collaborators/<their-username>`). They `git clone` it and open Claude Code in it.
   **One shared laptop?** Skip push and pull; everything else is the same.

**Staying in sync:** backend session in `api/`, frontend in `web/`; `shared/` changes only by agreement.
After each step: one line in `LOG.md`, commit and push. **Pull before each prompt.**

## Window 1: plan, then one thin slice
| Min | Do |
|---|---|
| 0–10 | Read the challenge. Setup (above): scaffold (**prompt 2**) or map the given code, then share the repo |
| 10–25 | **Plan together in BRIEF.md**: **prompt 1** drafts the scope (≤3 Musts, one AI idea), we cut; **prompt 1b** drafts the contract and rules, **we agree them**. Then **prompt 3** (contract and mocks), before we split |
| 25–45 | **Build in parallel.** Me: data, endpoints, rules tests-first (**prompt 4**). Partner: questions → rough pass → review → build on mocks (**prompt 5a–d**) |
| 45–60 | Join up: one flow works end to end. Commit, `git tag demo-1` |

## Window 2: fill in, polish, freeze
| Min | Do |
|---|---|
| 0–30 | Remaining Musts → the AI feature (**prompt 6**) → Shoulds. Commit after each |
| 30–40 | Polish: states, number formatting, spacing |
| 40 | **Freeze.** Only fix what breaks the demo. `git tag demo-final` |
| 40–50 | **Review** (**prompt 7**): final README + REVIEW.md. Cross-read: I take the frontend and AI, partner takes API, database, rules |
| 50–60 | Demo script (**prompt 8**), one dry run |

## Rules
1. **Always demoable.** Small commits, tag safe points.
2. **Cut scope, not time.** One finished Must beats three half-done.
3. **Contract first.** Agree the API table together; then nobody waits.
4. **Money in cents, rules tested first, UI approved before code.** I approve the tests and the design before code. Never edit an approved test to pass.
5. **Claude commits only after a yes.** Short reports, a line in LOG.md; it asks before anything outside the plan.
6. **AI explains, rules calculate, a human approves.** Works without an API key.
7. **Say assumptions out loud.** Propose the system to your partner; don't impose it.

## Demo (4 minutes)
1. **Problem:** the persona and their pain, in one sentence (30 s).
2. **Walkthrough:** the happy path plus one edge case, on seeded data (2 min).
3. **How it works:** the contract split, money in cents, the tests passing (30 s).
4. **AI:** in the product (rules calculate, AI explains, a person approves) and in how we built it (30 s).
5. **Next:** the Won'ts, as a short roadmap (30 s).

## If it goes wrong
- **Behind at minute 40?** Cut to one Must and make it work end to end.
- **Join-up failing?** Check the contract table first: field names, cents vs dollars.
- **Claude going in circles for 3+ minutes?** Restate the goal in one line, or do it by hand.
