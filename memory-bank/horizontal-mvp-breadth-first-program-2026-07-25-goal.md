# Breadth-first loop: standing goal and budget

Date: `2026-07-25`

Status: **owner-issued standing goal.** This does not change the program in
`horizontal-mvp-breadth-first-program-2026-07-20.md`; it is the instruction that
drives it and the budget that bounds it.

## The goal, as issued

> Finish implementing everything that doesn't require my design input. If you
> come across any design gaps, record them clearly so I can pick it up easily in
> the design thread. Work breadth-first across AnkiScape. Prioritize making every
> settled skill and feature family mechanic-complete using the smallest readily
> available, period-appropriate data set needed to exercise all of its mechanics
> end to end. Do not confuse horizontal MVP with a partial demo: entry gates,
> gameplay states, policies, failure modes, rewards, persistence, undo, UI,
> assets, and tests must all work. Defer exhaustive catalogs, rare-roll
> precision, difficult source reconciliation, and other slow data harvesting
> until every family is mechanically complete. Record genuine design conflicts or
> blockers clearly for the design thread.

## Budget

**90%/7 per day, per subscription.** GPT (Codex), Claude, and Kimi each carry
their own daily share of their own weekly quota, roughly 12.9%. A subscription
that breaches its daily share is **out of rotation for the rest of that day** —
the others keep working. Kimi's ceiling is **100%/7** (about 14.3%) because the
owner uses it for nothing else.

Metering reality, which matters because two of the three cannot be checked:

- **Kimi is measurable.** `~/.codex/skills/ask-kimi/scripts/kimi_quota.py
  --require-fresh` reports weekly and five-hour used percentages. Record the
  day's opening figure and stop at opening + 14.3.
  Baseline 2026-07-25: 3.0% weekly used.
- **Codex is not.** `codex-cli 0.145.0-alpha.30` exposes no usage or quota
  subcommand. Bound it by work volume instead — a breadth-one family costs
  roughly two to four hours of agent time, so about three families is a day's
  share — and report rather than guess.
- **Claude is not measurable from inside a session either.** Same treatment.

When a budget cannot be measured, say so instead of implying it was checked.

## What "no design input required" means here

Ship families whose contracts are already settled. When a family turns out to
need an owner decision, do not invent one and do not quietly pick the easy
reading: stop that family, record the fork with its options and a recommendation
in the design-thread queue, and move to the next family. A recorded fork is a
successful outcome for this loop; an invented mechanic is not.
