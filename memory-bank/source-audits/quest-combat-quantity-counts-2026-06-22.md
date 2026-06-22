# Quest Combat Quantity Counts - 2026-06-22

## Scope

This slice answers a concrete parity gap in the quest-stage model: generated
combat rows already had a `quantity` field, but runtime completion treated a
multi-enemy encounter as complete after one Quest review. That was wrong for
source rows such as TokTz-Ket-Dill's "Two Lava monsters - level 47".

The slice is backend-first with frontend verification:

- Backend: parse written combat quantities in
  `tools/build_pre_eoc_quest_catalog.py`, regenerate
  `quest_catalog_generated.py`, add save-safe partial combat counts, and keep
  legacy completed encounter ids compatible.
- Frontend: no new widget contract was required; the Quests tab already renders
  current-stage blocker reasons. Qt coverage now verifies initial and partial
  remaining quantity wording.

## Source-Backed Inputs

- Generated catalog source rows remain pinned historical wiki revisions through
  `tools/build_pre_eoc_quest_catalog.py`; this file was regenerated rather than
  hand-edited.
- TokTz-Ket-Dill source text now serializes:
  - `Two Lava monsters - level 47` as `quantity: 2`
  - `Two Fire monsters - level 47` as `quantity: 2`
- The same generator rule also corrects written quantities in rows such as
  Desert Treasure's "Five Ice Trolls", Spirits of the Elid's
  "Three level 75 Golems", Defender of Varrock's "Six armoured zombies",
  Blood Runs Deep's "Two Dagannoth Sentinels", Elemental Workshop III's
  "Three Earth Elementals", and Stolen Hearts' "Three Mercenaries".

## Runtime Model

`player_data["quest_combat_encounter_counts"]` is a flat quest-id to
encounter-id count map. One Quest review increments the current resolver-ready
encounter by one defeated enemy. The compatibility list
`player_data["quest_combat_encounters"]` receives the encounter id only when
the count reaches the sourced encounter quantity.

This keeps old saves valid:

- If an old save already has an id in `quest_combat_encounters`, that id still
  satisfies the blocker for the whole encounter.
- New partial progress is explicit and undo-safe because it remains inside
  `player_data`, which the existing review snapshot/rollback path tracks.

## Current Proof Case

TokTz-Ket-Dill stage 6 now behaves as follows when combat resolving is enabled
and the player has sufficient combat level:

1. Current blockers show `Battle required: Lava monster level 47 x2`.
2. The first Quest review records
   `quest_combat_encounter_counts["toktz_ket_dill"]["toktz_ket_dill_lava_monster_47"] = 1`.
3. The quest remains at stage 6 and the blocker becomes
   `Battle required: Lava monster level 47`.
4. The second Quest review records count `2` and writes
   `quest_combat_encounters["toktz_ket_dill"] = ["toktz_ket_dill_lava_monster_47"]`.
5. The stage still remains blocked by the other unresolved combat rows until
   their stats are source-backed or they are otherwise audited.

## Deferred Gaps

This is not every-quest combat parity. The audit still reports 159/285
resolver-ready combat rows and 126 statless rows. The unresolved rows remain
blocked by `combat_missing_stats`, `combat_locked`, or related current-stage
blockers. Full combat simulation, enemy special mechanics, food/prayer/death,
equipment hit chance, and the remaining source-stat extraction are still open
quest debt.
