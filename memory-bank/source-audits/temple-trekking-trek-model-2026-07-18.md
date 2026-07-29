# Temple Trekking trek model

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-settled trek shape; breadth implementation source-audited, with
registered placeholders for unrecovered server orchestration.**

## Evidence position

Darkan has no Temple Trekking activity controller (only quest references in
`InAidOfTheMyreque.kt`), so route generation, event weights and token scoring
still lean on pinned pre-cutoff wiki revisions. The rev-727 client record does
close several data seams that the first audit missed:

- `developer-information/enums.txt:51827-51834` — companion milestone structs;
- `developer-information/enums.txt:51837-51936` — exact level 1-99 cumulative
  companion XP curve, ending at 16,000 XP;
- `developer-information/npcList.txt:14018-14069` — companion and ambush
  identities/levels;
- OpenRS2 cache 309 — corroborating item and NPC definitions.

The breadth implementation uses that exact XP curve. Unrecovered event counts,
combat pressure/stats, companion XP awards, event selection, campsite/swamp
branches, token mapping/scoring and reward rolls are all registered in
`memory-bank/placeholder-values.md`, not presented as canon.

Druid pouch charging is source-pinned rather than reconstructed:

- pinned `Druid pouch` oldid `6356857` says a fill consumes at least three Mort
  Myre fruits, fungi add one charge each, stems add two, pears add three, and
  charges accumulate; it explicitly says no charge limit was known;
- Darkan `c95aca409` `quests/naturespirit/Blooming.kt:16-19,37-50` gathers held
  Bloom resources, sorts them by descending 1/2/3-charge value, requires at
  least three, and consumes exactly the first three while adding their values
  to the existing charged pouch, with no fixed cap; it corroborates charge
  weighting and accumulation, not the compact action's three-fungi preparation;
- Darkan `quests/naturespirit/Ghasts.kt:67-75` consumes exactly one pouch charge
  when a ghast becomes visible.

The compact preparation action therefore gathers the minimum three fungi and
adds three charges to the existing pouch. Repeated preparations accumulate.

## Owner-settled model (2026-07-18): hybrid nodes

- A trek is a seeded short sequence of event nodes. Source audit supersedes the
  earlier whole-trek route lock: the saved route is the next encounter choice,
  frozen at each node boundary and retained in `route_history`.
- Non-combat obstacle events (bog, broken bridge, river, and the rest of the
  period event table) resolve as one review beat each with their source
  consequences.
- Combat ambushes (ghasts, vampyres, nail beasts, and the rest of the period
  ambush table) run as live six-tick Combat encounters, following the
  Barrows/Troll Invasion/Pest Control precedent.
- The companion is persisted ally state; companion death fails the trek. That
  is the real risk of escorting a frailer, better-paying companion.
- The companion's LP is always visible as a health bar in the activity UI
  (owner requirement 2026-07-18), both during ambush encounters and between
  nodes — the protection stakes must never be hidden state.
- Reward tokens pay at the destination, per route/companion tier.

## Harvest work

1. Pin the pre-cutoff wiki revision: route tiers, companion roster and their
   difficulty/reward pairing, companion leveling if attested, the full event
   table, ambush rosters and stats, token tiers, and the token redemption
   catalog.
2. Derive the per-trek node count from the period record; record as
   `provisional/<source>` if unattested.
3. Reconcile Burgh de Rott Ramble (the reverse direction) — one activity
   surface or two — from the period record.
4. Token XP redemption rows are XP rewards; check them against packet decision
   12-B (hidden until the cadence invariant accounts for them) before any row
   ships.
