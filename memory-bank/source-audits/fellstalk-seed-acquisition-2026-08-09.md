# Fellstalk seed acquisition audit — 2026-08-09

## Scope and verdict

This slice closes the minimum authentic acquisition route for `Fellstalk seed`.
The existing Farming and Herblore mechanics were already complete but their
input graph was blocked.

**Verdict:** a Master Farmer can yield exactly one Fellstalk seed. The cutoff
wiki proves the route, quantity, and `Very Rare` classification. It does not
publish the hidden relative weight. AnkiScape therefore adds one slot to the
existing 2,199-slot Master Farmer table and registers that one-slot weight as a
placeholder. No other acquisition route is claimed.

## Period evidence

### Fellstalk seed

- RuneScape Wiki `Fellstalk seed`, oldid `6565142`, timestamp
  `2012-11-17T06:16:49Z`:
  <https://runescape.wiki/w/Fellstalk_seed?oldid=6565142>.
- The cutoff wikitext states that Fellstalk seeds come from Evil Trees, Master
  Farmers, Managing Miscellania, and the rare drop table. Its monster table
  also lists Aberrant spectres, Mutated jadinko guards and males, Dark beasts,
  Mature grotworms, Skeletal Wyverns, and baby blue dragons.
- The same revision pins level 91, 225 planting XP, 315.6 harvest XP, and four
  20-minute growth cycles. Those crop values were already live and are not
  changed by this slice.

### Master Farmer

- RuneScape Wiki `Master Farmer`, oldid `6565826`, timestamp
  `2012-11-17T10:29:27Z`:
  <https://runescape.wiki/w/Master_Farmer?oldid=6565826>.
- The cutoff table requires level 38 Thieving, awards 43 XP, and gives one
  random seed per successful pickpocket. Its Fellstalk row states quantity `1`
  and rarity `Very Rare`.
- The page does not expose a numerical probability or relative table weight.

### Item identity and existing reconstructions

- OpenRS2 revision 742 item `21621` is `Fellstalk seed`, model `7201`,
  stackable and exchangeable, with the ordinary `Drop` inventory option.
- AnkiScape's existing 2011Scape-derived Master Farmer table contained 42 rows
  with 2,199 total slots and no Fellstalk row. Darkan's current
  `data/npcs/drops/pickpocketing/pp_masterfarmer.json` reconstruction also omits
  Fellstalk and therefore does not settle the cutoff weight.

## Product translation

- `pickpocket_master_farmer` now includes `("Fellstalk seed", 1, 1, 1)` and a
  total of 2,200 slots.
- `thieving.master_farmer_fellstalk_weight` records the one-slot extension as a
  placeholder. A period server table or qualified cutoff sample can replace it
  without changing the route or quantity.
- The row reuses the existing Thieving success, stun, multi-pick, inventory,
  persistence, telemetry, and answer-undo path. There is no new runtime or UI
  pattern.
- The route makes eight existing item states reachable and closes five blocked
  actions. The graph changes from 1,549 actions / 2,413 reachable items / 117
  orphan inputs / 118 blocked actions to 1,549 / 2,421 / 112 / 113.

## Asset correction

The existing `farmingitems/fellstalk_seed.png` was a modern upload from
`2025-05-06T23:46:06Z`. It is replaced with the latest pre-cutoff file-history
revision of `File:Fellstalk seed 5.png`:

- timestamp: `2012-11-17T05:53:59Z`
- SHA-1: `4c7b64493ad5beb0a06eb0bdd5ff4864fb323706`
- dimensions: 31×26 pixels with a tight alpha box
- archive URL:
  <https://runescape.wiki/images/archive/20160503051728%21Fellstalk_seed_5.png?bb7f9>

## Explicit omissions

- Evil Trees, Managing Miscellania, rare-drop-table monsters, and other monster
  drops remain separate catalog-depth routes.
- The exact Master Farmer weight remains unrecovered. `Very Rare` is not
  converted into a fabricated percentage.
- Vinesweeper continues to exclude Fellstalk, matching its own cutoff audit.
- This slice does not change Farming growth, yield, disease, herb cleaning, or
  potion recipes.

## Acceptance contract

- The Master Farmer table weights must sum to its declared total.
- The final slot must yield one Fellstalk seed in pure and runtime paths.
- Reachability must name `Thieving:pickpocket_master_farmer` as the seed route.
- The local icon and provenance record must match the cutoff timestamp and
  SHA-1 above.
- Focused Thieving, Farming, reachability, placeholder, asset, and real Qt
  checks must pass before closure.
