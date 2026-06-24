# Combat Al-Kharid Warrior Audit - 2026-06-23

Status: implemented ordinary Combat target expansion for the source-backed
level-9 Al-Kharid warrior and the first shared/global drop-table primitive.

## Implemented Scope

- Added recursive Combat drop-table slots so a winning parent slot can roll a
  source-backed nested table. The implementation is deliberately generic but
  only enabled through explicit table data in `combat_data.py`.
- Added `COMBAT_MINOR_HERB_DROP_TABLE` from local 2011Scape
  `Herbs.minorHerbTable`: 1024 total slots across Grimy guam, marrentill,
  tarromin, harralander, ranarr, irit, avantoe, kwuarm, cadantine, lantadyme,
  and dwarf weed.
- Registered the eleven grimy herbs as Combat material items so nested herb
  drops are valid inventory keys. Icons remain deferred until Herblore/Farming
  has a player-facing item surface for them.
- Added `al_kharid_warrior` as a selectable Humanoids target using local
  2011Scape level-9 data: attack speed 4, respawn delay 25, 190 lifepoints,
  Attack 7, Strength 5, Defence 4, defence bonuses 12/15/10/-1/12, generic
  `attackBonus = 10`, and `strengthBonus = 9`.
- The source generic melee `attackBonus` is represented across stab/slash/crush
  attack fields because the current Combat formula chooses the best melee
  attack bonus. The source `strengthBonus` maps to `melee_strength`.
- Imported the warrior's guaranteed Bones, 1024-slot main table, nested
  `minorHerbTable` slot, Bronze bolts x2-12 quantity range, and 1024-slot easy
  clue tertiary table.

## Source Anchors

- Al-Kharid warrior:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/humanoids/alkharid_warrior_level_9.plugin.kts`
- Minor herb table:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/drops/global/Herbs.kt`
- Item IDs:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`

## Deferred

- The source TODO for surrounding Al-Kharid warriors assisting each other is
  not modeled yet; the current engine still resolves one enemy encounter at a
  time.
- Farmer remains deferred because it also needs `Seeds.allotmentSeedTable`.
- Higher Goblin rows can now reuse `COMBAT_MINOR_HERB_DROP_TABLE`, but they
  still need a row-by-row source import and audit.

## Verification

- `python3 -m py_compile combat_data.py logic_pure.py constants.py tests/test_combat_logic.py tests/test_skill_and_item_registry.py`
- `python3 -m unittest tests.test_combat_logic tests.test_skill_and_item_registry tests.test_target_metadata tests.test_storage_pure tests.test_review_hud`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
- `git diff --check`
