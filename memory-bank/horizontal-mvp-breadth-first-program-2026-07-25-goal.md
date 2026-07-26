# Breadth-first loop: standing goal and budget

Date: `2026-07-25`

Status: **owner-issued standing goal.** This does not change the program in
`horizontal-mvp-breadth-first-program-2026-07-20.md`; it is the instruction that
drives it and the budget that bounds it.

## The goal, as issued (superseded 2026-07-25 by the text below)

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

## The goal as it now stands

Re-issued by the owner on 2026-07-25 with the harvest clause folded in. This is
the live wording, and it is what the session stop hook enforces:

> Finish implementing everything that doesn't require my design input. If you come
> across any design gaps, record them clearly so I can pick it up easily in the
> design thread. Work breadth-first across AnkiScape. Prioritize making every
> settled skill and feature family mechanic-complete using the smallest readily
> available, period-appropriate data set needed to exercise all of its mechanics
> end to end. Do not confuse horizontal MVP with a partial demo: entry gates,
> gameplay states, policies, failure modes, rewards, persistence, undo, UI,
> assets, and tests must all work. Do enough source harvesting to reach
> mechanical completion: where a value would need an intense dig, use a
> registered placeholder rather than blocking the family, marked at the value and
> listed in memory-bank/placeholder-values.md. Defer exhaustive catalogs,
> rare-roll precision, and other slow data harvesting beyond what mechanical
> completion needs. A placeholder stands in for a value the period game had and
> we could not recover; it is never permission to invent content the period did
> not have. Record genuine design conflicts or blockers clearly for the design
> thread.

One clause changed rather than being appended. The first issue said to defer
"difficult source reconciliation", which is exactly what the remaining families
need, so it had parked twenty-three of them. That phrase is now scoped to
harvesting *beyond* mechanical completion.

## How the amendment came about

The goal as first issued deferred difficult source reconciliation, which parked
twenty-three families that each need some harvest before any mechanic can ship.
The owner amended it:

> include enough source harvesting to get mechanical completion, with placeholder
> values for stuff that you need an intense dig for.

So harvest is now in scope up to the point of mechanical completion, and no
further. A value that would need an intense dig becomes a **placeholder** rather
than a blocker, governed by
`pre-eoc-source-verification-standard.md`, "Breadth-Phase Placeholders":
marked in code as `PLACEHOLDER(<id>)`, listed in
`memory-bank/placeholder-values.md`, and kept honest by
`tests/test_placeholder_register.py`, which fails if the code and the register
disagree in either direction.

What has not changed: a placeholder stands in for a value the period game had and
we could not recover. It never licenses inventing *content* the period did not
have — a target, item, reward or gate. Those still wait. The failures this rule
exists to prevent are the Daily Challenges reroll and the Fish Flingers weight,
both of which were inventions written up as though settled.

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
