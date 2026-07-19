# Shades of Mort'ton loop model

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-settled loop shape (persistent open loop with simulated
population); period values and rates remain harvest work.**

## Pinned Darkan evidence

`darkan-world-server`,
`src/main/java/com/rs/game/content/minigames/shadesofmortton/ShadesOfMortton.java`
(plus `TempleWall.java`, `Shade.java`, `ShadeCatacombs.java`,
`ShadeChest.java`):

- a communal temple repair state (0–100) aggregated from individual wall
  repair percentages;
- a personal 0–100 sanctity meter decaying ~1 per 30 seconds while present;
- the altar lights at repair ≥99, enabling sacred-oil blessing;
- pyre cremation of shade remains grants Firemaking/Prayer XP and shade keys;
  keyed catacomb chests hold the loot.

Darkan values need the ordinary corroboration gate before shipping.

## Owner-settled model (2026-07-18)

Persistent open loop — no session boundary, matching the source's open area —
**with a simulated public population** (owner amendment to the recommendation):

- Temple repair and personal sanctity are persisted meters. Personal sanctity
  decays at the source rate only while the activity is the active target and
  is never contributed by the crowd.
- The area uses the shared naturalized-population inputs already settled for
  Shooting Stars and Big Chinchompa: answered-card time-of-day drives a
  Quiet/Normal/Busy population level with bounded jitter, rising and falling
  across the simulated day.
- The population affects the minigame exactly where source players would:
  communal wall repairs raise (and their absence lets decay lower) the temple
  repair state, including keeping the altar lit during busy periods. It never
  grants the player sanctity, XP, keys, resources, or loot.
- One review = one repair beat (Crafting XP, sanctity gain) or one cremation
  (Firemaking + Prayer XP, key chance). Shade combat runs as live six-tick
  encounters. Sacred oil and serums route through ordinary production; chest
  opening is a direct command.

## Harvest work

1. Pin the pre-cutoff wiki revision: repair XP and materials, sanctity gains,
   sacred-oil dosing, pyre log tiers, shade tiers and key colors, chest loot
   tables, serum mechanics.
2. Reconcile Darkan's decay/aggregation constants against the period record.
3. Calibrate the population contribution as a bounded rate through the shared
   profile; record derivation as `provisional/<source>` where unattested.
