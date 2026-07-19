# Temple Trekking trek model

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-settled trek shape (hybrid nodes); all period values remain
harvest work.**

## Evidence position

Darkan has no Temple Trekking implementation (only quest references in
`InAidOfTheMyreque.kt`), so the contract leans on a pinned pre-cutoff wiki
revision of the 2011-reworked activity plus dated-cache corroboration. Nothing
below is source-closed yet.

## Owner-settled model (2026-07-18): hybrid nodes

- A trek is a seeded short sequence of event nodes, generated at entry from
  the chosen route tier and companion.
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
