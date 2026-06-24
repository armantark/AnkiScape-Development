# Combat Scorpion And Spider Variant Audit - 2026-06-23

Status: implemented ordinary Combat target expansion for source-backed Scorpion
and higher Spider rows. Follow-up expansion added King scorpion, the level-59
Scorpion, and the level-64 Poison spider from the same source family.

## Implemented Scope

- Added `scorpion` as a selectable Scorpions target using local 2011Scape
  level-14 Scorpion data: attack speed 4, respawn delay 25, 170 lifepoints,
  Attack 11, Strength 12, Defence 11, and the source charm table.
- Added `spider_level_24` as a selectable Spiders target using local 2011Scape
  level-24 Spider data: attack speed 4, respawn delay 27, 220 lifepoints,
  Attack/Strength/Defence 21, stab/crush attack bonuses 53, all listed defence
  bonuses 53, and the 200-slot charm table.
- Added `deadly_red_spider` as a selectable Spiders target using local
  2011Scape level-34 Deadly red spider data: attack speed 4, respawn delay 30,
  350 lifepoints, Attack 30, Strength 25, Defence 30, listed defence bonuses,
  and the 1000-slot charm table.
- Added `giant_spider_level_50` as a selectable Spiders target using local
  2011Scape level-50 Giant spider data: attack speed 4, respawn delay 25, 500
  lifepoints, Attack 41, Strength 51, Defence 31, source attack/defence
  bonuses, the rune/equipment/tertiary/charm drop tables, and inclusive Air
  rune x4-6 quantity ranges.
- Added `king_scorpion` as a selectable Scorpions target using local 2011Scape
  level-32 King scorpion data: attack speed 4, respawn delay 25, 300 lifepoints,
  Attack 30, Strength 29, Defence 23, Scorpion Slayer XP 37.0, and no item
  drops because the source file has no `DropTableFactory` registration.
- Added `scorpion_level_59` as a selectable Scorpions target using local
  2011Scape level-59 Scorpion data: attack speed 4, respawn delay 22, 550
  lifepoints, Attack 50, Strength 52, Defence 50, Scorpion Slayer XP 55.0,
  higher ranged defence, and the same source charm table as level-14 Scorpion.
- Added `poison_spider_level_64` as a selectable Spiders target using local
  2011Scape level-64 Poison spider data: attack speed 4, respawn delay 30, 640
  lifepoints, Attack 50, Strength 58, Defence 52, Spider Slayer XP 64.0, source
  `poisonDamage = 6`, and no item drops because the source file has no death
  drop callback.
- No new drop-slot shape or asset category was required; these rows reuse the
  existing guaranteed/table/quantity-range drop support and already registered
  charm, rune, arrow, bow, staff, and bronze-equipment item definitions.

## Source Anchors

- Scorpion:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/scorpion_level_14.plugin.kts`
- King scorpion:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/king_scorpion_level_32.plugin.kts`
- Scorpion level 59:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/scorpion_level_59.plugin.kts`
- Poison spider level 64:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/poison_spider_lvl_64.plugin.kts`
- Spider level 24:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/spider_level_24.plugin.kts`
- Deadly red spider:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/deadly_red_spider_level_34.plugin.kts`
- Giant spider level 50:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/giant_spider_level_50.plugin.kts`

## Deferred

- Cave slime remains deferred because it belongs behind Slayer-gated access and
  needs shared gem-table/drop support before it should become enabled gameplay.
- Broader spider/scorpion family parity still needs access/risk modeling for
  source locations and any future poison/immunity/potion interactions.

## Verification

- `python3 -m py_compile combat_data.py tests/test_combat_logic.py`
- `python3 -m unittest tests.test_combat_logic`
- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata tests.test_storage_pure tests.test_review_hud`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
- `git diff --check`
