# Combat Monk of Zamorak Source Audit - 2026-06-23

## Source

- Enabled local source file: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/monk_of_zamorak_lvl_45.plugin.kts`
- Enabled source ID: `Npcs.MONK_OF_ZAMORAK_190`
- Drop callback: `on_npc_death(*ids)` calls `DropTableFactory.getDrop(...)`.
- Combat definition: attack speed 4, respawn 250, hitpoints 400, Attack 38, Strength 38, Defence 42, Magic 40, Ranged 1, and aggro radius 4.
- Deferred conditional source file: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/monks_of_zamorak.plugin.kts`

## Implemented

- Added `COMBAT_ENEMY_DATA["monk_of_zamorak_level_45"]` as a Humanoids melee target at combat level 45.
- Added the source 20-slot main table: `Items.ZAMORAK_ROBE_1035`, `Items.ZAMORAK_ROBE`, and an 18-slot nothing branch.
- Added the source 1000-slot charm table: Gold charm 10, Green charm 100, Crimson charm 20, Blue charm 10, and 860 empty slots.
- Registered `Zamorak robe top` and `Zamorak robe bottom` as Combat equipment drops and fetched icons/provenance for both.

## Name Mapping

- The local `items.yml` names item IDs 1033 and 1035 both `Zamorak robe`.
- AnkiScape uses a flat inventory keyed by item display string, so using the same key for both drops would collapse separate equipment slots.
- The implementation maps `Items.ZAMORAK_ROBE_1035` to `Zamorak robe top` because its source equipment slot is 4, and maps `Items.ZAMORAK_ROBE` to `Zamorak robe bottom` because its source equipment slot is 7.

## Deferred

- The level-30 Monk of Zamorak source row remains deferred because it conditionally adds `Items.GOLDEN_KEY` only when the player lacks the key. Combat currently has unconditional and nested drop-table support, but not player-state-conditioned drop branches.
- Aggro radius is recorded in the row source string but does not change review gameplay yet.

## Backend Notes

- The new row uses existing fixed drop-table and charm-table runtime support; no combat engine change was required.
- Tests cover the source stats, robe mapping, main table, charm table, drop rolls, target tooltip, and item registry icons.

## Frontend Notes

- No frontend component change is required. The existing Combat target selector exposes `Monk of Zamorak`, robe/charm drop summaries, and the source file through `combat_target_rows(...)`.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py tests/test_skill_and_item_registry.py tests/test_target_metadata.py` passed.
- Focused Monk of Zamorak row/drop/item/metadata tests passed.
- `python3 -m unittest tests.test_combat_logic tests.test_skill_and_item_registry tests.test_target_metadata` passed with 146 tests.
- `git diff --check` passed.
- `python3 run_tests.py` passed with 670 tests and 132 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` passed with 670 tests.
