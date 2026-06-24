# Combat Pirate Source Audit - 2026-06-23

## Source

- Local source file: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/pirate_level_23.plugin.kts`
- Source IDs: `Npcs.PIRATE`, `Npcs.PIRATE_183`, `Npcs.PIRATE_184`
- Drop callback: `on_npc_death(*ids)` calls `DropTableFactory.getDrop(...)`.
- Combat definition: attack speed 5, respawn 25, hitpoints 200, Attack 21, Strength 21, Defence 21, `attackBonus = 8`, `strengthBonus = 10`, `defenceStab = 3`, and `defenceSlash = 2`.

## Implemented

- Added `COMBAT_ENEMY_DATA["pirate"]` as a Humanoids melee target at combat level 23.
- Mirrored the source `attackBonus` and `strengthBonus` pattern already used by Al-Kharid warrior: generic source attack bonus maps to all melee attack bonuses, and source strength bonus maps to `melee_strength`.
- Added the full 1024-slot main drop table: Iron dagger, Bronze scimitar, Iron platebody, Iron bolts x2-12, runes, Bronze arrows, Coins, Eye patch, Chef's hat, Iron bar, one explicit nothing slot, and nested `Gems.gemTable`.
- Added `Eye patch` as Combat equipment metadata and fetched `combatitems/eye_patch.png` with provenance in `combatitems/eye_patch.provenance.json`.

## Deferred

- Ring of Wealth boosted gem and mega-rare table branches remain deferred until Combat supports equipment-conditioned drop modifiers.
- Death sound/animation differences are not modeled in ordinary target metadata; the enabled row preserves the stat, timing, and drop behavior that affect review gameplay.

## Backend Notes

- The new row uses the existing Combat drop-table and nested-table runtime, so no runtime engine changes were required.
- Tests cover the exact table total, representative slots, quantity-range roll, nested gem roll, target-row tooltip, and item registry icon.

## Frontend Notes

- No frontend component change is required. The generic Combat target selector surfaces `Pirate`, its drop summary, and the source file through existing `combat_target_rows(...)` tooltip metadata.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_skill_and_item_registry.py tests/test_target_metadata.py` passed.
- Focused Pirate/item/metadata unit tests passed after correcting the local registry test selector.
- `python3 -m unittest tests.test_combat_logic tests.test_skill_and_item_registry tests.test_target_metadata` passed with 144 tests.
- `git diff --check` passed.
- `python3 run_tests.py` passed with 668 tests and 132 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` passed with 668 tests.
