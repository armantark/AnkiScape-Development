# Deferred GPT work

Archived 2026-10-02; selection is in [../goal-priority-matrix.md](../goal-priority-matrix.md).

Status: **live queue.** The owner's goal says to defer GPT work until the quota
hook reports the Codex subscription is back inside its daily share.

The hook prints a `[quota used/allowed]` line on every turn. When `codex` is no
longer marked OVER, drain this queue before starting new GPT work.

## Why these items are GPT's rather than anyone else's

Each one is mechanical, high-volume, or verification-shaped — the work Codex does
better and cheaper than the alternatives. None of them blocks a family from
reaching breadth level one, so deferring them costs nothing today.

## Queue

| item | why GPT | blocked family, if any |
| --- | --- | --- |
| ~~Independent verification pass over every family that reached breadth one this week~~ **done 2026-07-26.** Found four real bugs three earlier passes missed; all four fixed and merged | Sol is the right verifier for did-this-actually-run questions, and a different lineage from the Claude models that wrote all nine families | none; a quality gate, not a blocker |
| Exhaustive drop-table and rare-roll harvest for the boss families | high-volume, bounded extraction from Darkan and the rev-727 cache | none; the breadth rule defers exhaustive catalogs |
| Period-art provenance sweep across the asset library | mechanical, ~83% of the library, tedious rather than hard | Evil Tree only; `woodcuttingitems/evil_tree_kindling.png` is pinned to `2020-11-24T10:56:22Z`, after the cutoff. Wicked hood cleared: `runecraftingitems/wicked_hood.png` is pinned to `2011-10-17T18:06:33Z` |
| Placeholder retirement pass | each row in `placeholder-values.md` is a bounded dig | none by construction |

## Rules for draining it

1. Read the quota line first. Do not start on a subscription the hook marks OVER.
2. Take items in order. The verification pass comes first because it can
   invalidate work the later items would otherwise build on.
3. A GPT run never gets git, release, or other external side effects. Those stay
   with Claude, per the owner's routing rules.

## Art sweep tranche ledger (2026-07-27; closed 2026-07-29)

Tranche 1 (combatenemies + shopitems, 672 assets): 39 replaced with verified
pre-cutoff revisions; ~237 lost to tool failure and queued for re-research.

**Tranche 2 closed 2026-07-29.** One 56-agent workflow re-researched all 2,984
post-cutoff assets (tranche-1 leftovers included) through
`tools/reresearch_period_art.py`, which owns the endpoint, full-history, and
sha-of-served-bytes protocol: **2,385 replaced** with verified pre-cutoff
revisions, **356 no-period-art with recorded evidence** (earliest-upload
timestamps or exhausted title variants), **243 unresolved** (unreachable
archives and unrecoverable sha mismatches, evidence in the run's
`summary.json`). One recovery was manually reverted: the desert lizard came
back under the orange-variant title against the roster's green pin, so the
honest post-cutoff green art stays. The remaining 243 rows are the only
re-research candidates left; a further pass needs a different lever (Wayback
snapshots or cache sprites), not another wiki sweep.

**Sweep boundary, 2026-07-29:** `icon/` is navigation vocabulary settled by
the owner-grilled 2026-07-20 icon audit, not sweepable art. Tranche 2 replaced
seven of its glyphs (including the Stats bar graph the owner prefers) and they
are reverted; future sweeps exclude `icon/` entirely. `equipment_slots/` stays
swept — no owner settlement covers it.
