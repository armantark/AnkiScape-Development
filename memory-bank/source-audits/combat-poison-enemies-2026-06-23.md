# Combat Poison Enemy Application - 2026-06-23

## Scope

This slice connects source-backed NPC poison attacks to the existing persistent
player poison status path and enables two ordinary poison enemies whose local
2011Scape definitions have complete combat stats and explicit runtime drop
behavior.

## Source Files

| Local source | Imported facts |
| --- | --- |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/Combat.kt` | NPC poison rolls after attacks when `poisonDamage > 0` and `world.random(10) < 4`. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/poison/Poison.kt` | Initial poison damage maps to ticks with `initialDamage * 5 - 4`; poison damage follows `((ticks / 5) + 1) * 10`. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/poison_scorpion_lvl_20.plugin.kts` | Poison scorpion stats, attack speed, respawn delay, stab style, `poisonDamage = 3`, Slayer XP, and no registered drop table. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/poison_spider_lvl_31.plugin.kts` | Poison spider stats, attack speed, respawn delay, stab style, `poisonDamage = 3`, Slayer XP, and no registered drop table. |

## Implemented Enemy Contract

- `poison_scorpion`: display `Poison scorpion`, combat level 20, group
  `Scorpions`, hitpoints 230, Attack 16, Strength 17, Defence 15, Magic 1,
  Ranged 1, attack speed 4, respawn delay 25, poison damage 3, Slayer XP 23.0.
- `poison_spider`: display `Poison spider`, combat level 31, group `Spiders`,
  hitpoints 250, Attack 28, Strength 28, Defence 28, Magic 1, Ranged 1, attack
  speed 4, respawn delay 30, poison damage 3, Slayer XP 25.0.
- Both rows use empty drop specs because their local definitions do not call
  `DropTableFactory.register` and do not define `on_npc_death` drop delivery.

## Runtime Behavior

- During a Combat burst, a source-poisonous NPC attack rolls a 40% poison chance
  after the enemy attack event.
- A successful poison roll writes `combat_status_effects["poison"]` through the
  existing source-shaped poison status schema.
- Existing stronger poison is preserved; equal or weaker poison can refresh.
- Combat target previews mark poison enemies at least `Food advised` and expose
  the initial poison lifepoint damage plus attack poison chance in row tooltips.

## Asset and Registry Notes

- This slice adds no new item drops, so it requires no new item icons.
- The current Combat target UI does not use NPC portrait icons. If enemy art is
  added later, these rows will need sourced/fallback NPC icons then.

## Deferred

- `cave_slime_lvl_23.plugin.kts` remains deferred because it has a Slayer level
  17 requirement and a nested shared `Gems.gemTable` drop entry. Enable it only
  after per-enemy Slayer gates and first-class shared drop-table references are
  in place.
- Weapon/ammo poison, enemy poison immunity, antipoison dose handling, and
  non-poison statuses remain future work.

## Verification

- `python3 -m py_compile combat_data.py logic_pure.py target_metadata.py tests/test_combat_logic.py`
- `python3 -m unittest tests.test_combat_logic`
- `python3 -m unittest tests.test_combat_logic tests.test_target_metadata tests.test_storage_pure tests.test_review_hud`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
