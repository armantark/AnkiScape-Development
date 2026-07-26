# Breadth-first: the next tranche

Status: **prepared 2026-07-25, not started.** Written while four families build in
the worktree, so the run after that one starts precise instead of re-deriving.

## Why this ordering

The programme picks the next slice by source and design readiness first, then by
how many unrepresented families it unlocks, then reward reachability, then the
smallest data set that still exercises the whole mechanic graph. Under the
2026-07-25 placeholder amendment, a missing value no longer blocks a family, so
"source readiness" now means *how much harvest stands between here and a complete
mechanic*, not *whether every number is recoverable*.

Estimates are the frontier audit's, and they predate the placeholder rule, so
treat them as ceilings rather than forecasts.

## Batch A — smallest, and two already have audits

| family | estimate | source state |
| --- | --- | --- |
| Enchanted Key | 6-9 h | no audit yet; disposition settled as a one-time cache with Penguin-style flattening |
| Skeletal Horror | 8-11 h | `source-audits/skeletal-horror-implementation-harvest-2026-07-19.md` — phases, LP thresholds, attack-style changes, rewards and cadence already harvested |
| Tears of Guthix | 8-12 h | `source-audits/tears-of-guthix-cutoff-reconciliation-2026-07-17.md` — identity and eligibility safe, exact values still open |

Skeletal Horror is the strongest candidate to lead: its harvest is largely done,
so it tests the placeholder rule on a family that needs it least, which is the
right order for a new policy.

## Batch B — mid-sized

The Crucible (10-14 h, no audit), Goblin Raids (10-15 h, no audit), Gnome
Restaurant (12-18 h, **carries an open presentation fork** — see below), Shattered
Heart, Troll Invasion, Mage Training Arena, Temple Trekking, Dominion Tower
(14-20 h each), Mobilising Armies (18-26 h).

## Batch C — large, and one is gated

Achievement Diaries (30-45 h). Dungeoneering (40-64 h plus source research; its
data module explicitly parks the Skills surface). Conquest (20-30 h) is sequenced
**after** Dungeoneering by the programme.

## Two families that are not merely unstarted

**Bork** is dependency-blocked, not source-blocked. It needs the `Hunt for Surok`
miniquest and the regional Achievement Diary substrate, and neither exists. Do not
schedule it as an ordinary family; it waits for those, or it ships an always-open
row that fakes its own gate. See `source-audits/bork-loop-2026-07-18.md`.

**Gnome Restaurant** carries a real fork: the compact order and reward
presentation was deliberately deferred "after the data surface is known"
(`source-audits/gnome-restaurant-delivery-loop-2026-07-17.md`). The placeholder
rule now lets that surface be approximated, so the fork becomes answerable — but
it is still the owner's, and it should reach the design queue as a concrete choice
once the data shape exists, not as an abstract question now.

## What to carry into the next brief

Everything in the run-3 brief still applies, plus the three failures this session
produced, because each one shipped and survived review:

1. An **inert row** — a reward gated on a state no player could reach, in a
   family reported complete.
2. An **invention presented as settled** — a Fish Flingers weight that nothing
   read, under a name that already meant something else in that family's own
   audit, documented into the audit by the same change that added the code.
3. A **test that pinned the defect** — asserting a sourced medal was *absent*,
   which is how the medal stayed unearnable through a full verification pass.

The placeholder register exists to stop the second of those recurring. The first
and third need the verifier to keep constructing player state through real paths
rather than reading reports.
