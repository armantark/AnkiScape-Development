# Minigames & Activities Design Seed

Status: captured 2026-07-07, not implemented. Parked stub — this is a seed to
anchor future discussion, not a spec. Do not build from it until it is grilled.

This is the surface that will let reward-gated content (Fist of Guthix gauntlets,
Barbarian Assault, Pest Control, etc.) enter AnkiScape without inventing a
smithing/crafting/fletching path it never had in the real game. The immediate
motivating case is the metal gauntlets and metal boots, which are minigame- and
drop-only at the 2011 baseline (see [[Cross-links]] below).

## Owner Intent (seed)

- A minigame/activity is **just another activity in the existing Utility /
  Activities tab** — not a new top-level surface, not a skill. It reuses the
  no-XP hub that already exists (`UTILITY_ACTIVITY_DATA` / `current_utility` /
  `DEFAULT_UTILITY_ACTIVITY`, `_UTILITY_HUB_NAME = "Utility / Activities"` in
  `ui.py`), which today holds material-prep conversions like `make_soft_clay`
  and `tan_soft_leather`.
- Each run should be able to fire **random events** so it feels realistic and
  varied rather than a fixed conversion. The randomness is flavor plus a light
  outcome spread, not a new economy.
- Long-term this is how minigame **reward shops / reward currencies** get modeled
  (e.g. Fist of Guthix tokens → the degradable metal gauntlets), so gear that has
  no craft/smith/fletch path can still be earned.

## How this differs from a material-prep activity

Today a Utility activity is a deterministic input→output conversion with a fixed
`requirements` / `output_item` / `output_qty` / `batch_size`. A minigame activity
is the same *surface* but a different *payoff shape*:

| Aspect            | Material-prep activity        | Minigame/activity                          |
|-------------------|-------------------------------|--------------------------------------------|
| Payoff            | Fixed converted item          | Reward currency and/or a rolled reward      |
| Determinism       | Deterministic                 | Random events + outcome spread              |
| Inputs            | Consumes materials            | May cost nothing (or a ticket/entry)        |
| Progress          | None (no XP)                  | Possibly per-minigame reward-shop credit    |

The key new primitives (names TBD, all open questions below): a per-minigame
**reward currency** the player accumulates, a **reward shop** that spends it
(reuse the NPC-shop model if it fits — see `npc-shop-design-seed.md`), and a
**random-event table** rolled per run.

## Random events (seed idea)

Per run, roll against a small weighted event table for the active minigame:
a common "normal round" outcome, occasional better/worse rounds, and rare flavor
events. Keep it source-faithful where the real minigame has documented event
variety; otherwise keep the spread deliberately small and note it as a
non-source approximation (parity-over-safeguards still applies — do not invent
balance clamps, but do flag any non-source flavor explicitly).

## Source Policy

Same policy as the rest of AnkiScape: prefer local 2011Scape definitions, treat
the Darkan/2012scape checkout as an equal source when 2011Scape is incomplete,
and fall back to pre-EOC (Nov 2012 or earlier) Wiki revisions on heavy conflict.
Note that **2011Scape does not implement the Fist of Guthix minigame itself** —
only the reward items exist in `items.yml` / `Items.kt` (the `WORNOUT_*` /
`_NOTED` degrade variants confirm the FoG reward mechanic). So minigame *logic*
will lean on Wiki/Darkan more than on the local server.

## Open Questions (to grill later)

- Review-cost model: does a minigame run cost reviews like a bank run, or is it
  free like a material-prep conversion? Does it have an entry ticket?
- Reward currency: one shared "activity points" pool, or per-minigame currencies
  (FoG tokens, Pest Control points, Void knight commendations…)? Real games use
  per-minigame currencies.
- Reward shop: reuse the NPC-shop backend, or a lighter reward-shop model?
- Randomness surface: how much event variety is source-backed vs. flavor, and how
  to keep it from becoming a balance knob.
- Degradable gear: metal gauntlets degrade and recharge in FoG. Do we model
  charge/degrade, or grant a static-stat version? (Simplest first pass: static.)
- Which minigame is the proof case? Fist of Guthix is the natural first one
  because its only purpose here is unblocking the metal gauntlets.

## Cross-links

- Parked gear this unblocks: **metal gauntlets** (Bronze→Dragon, ids 12985–13006,
  FoG reward-shop, defence-only) and **metal boots** (Bronze→Rune, drop-only).
  Both are deliberately excluded from the 2026-07-07 crafting/fletching equipment
  generator pass because they have no craft/fletch/smith path.
- Related surfaces: `npc-shop-design-seed.md` (reward shop could reuse this),
  `fake-grand-exchange-design.md` (separate economy surface), the equipment
  generator work in `tools/generate_equipment_data.py`.
