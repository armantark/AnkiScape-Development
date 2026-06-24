# Combat V1 Implementation Audit - 2026-06-23

Status: implemented ordinary-combat V1 slice plus recovery/loadout foundation,
Tutorial Island starter kit claim bridge, simple ordinary-enemy expansion,
Spider/Giant spider drop-range expansion, Scorpion and higher Spider variant
expansion, Highwayman and Al-Kharid warrior humanoid expansions, Barbarian
level 8/9 and level 10 ordinary-enemy expansions, Goblin
ordinary-enemy expansion, first Ranged/ammo path plus standard bow/ammo
progression, and the standard elemental Combat spell ladder, plus ordinary
dangerous-target confirmation, safe-boundary ammo recovery, and persistent
poison status recovery and first source NPC poison application.

## Implemented Scope

- Combat is a general review action (`Combat`) routed through
  `action_registry.py` and `runtime_actions.py`, not a quest-only resolver and
  not a fake levelled registry skill.
- `combat_data.py` seeds source-backed ordinary enemies with complete combat
  stats and drop behavior: Chicken, Rat, Spider, Spider level 24, Giant rat,
  Giant spider level 2, Giant spider level 50, Goblin level 2 armed/unarmed,
  Cow, Cow calf, Ram, Highwayman, Al-Kharid warrior, Barbarian level 8/9,
  Barbarian level 10, Seagull, Scorpion, Poison scorpion, Deadly red spider,
  and Poison spider.
- `apply_combat_burst_pure()` simulates bounded RuneScape-shaped combat time:
  50 ticks per `Actions per review`, player/enemy attack speed, accuracy rolls,
  max-hit rolls, persistent lifepoints, persistent partial enemy HP, auto-eat,
  death/grave state, per-damage XP, guaranteed drops, one roll per
  non-guaranteed drop table, and inclusive quantity ranges for winning slots.
- Combat food now comes from a finite `combat_supply_loadout["food"]` instead
  of the whole Bank during an active encounter. Starting a fresh target, killing
  a target, or completing a safe noncombat review can refill the loadout from
  the configured auto-eat food priority; an active paused fight cannot pull
  extra Bank food mid-encounter.
- Safe noncombat reviews apply one review-tick recovery packet per card, not
  once per `Actions per review` sub-action. The packet heals or decays
  lifepoints by 100, regenerates 10 special-attack energy per 50 ticks, recovers
  one stat-drain level per 100 safe ticks, refills carried food, Magic runes,
  and Ranged ammo at safe boundaries, advances active poison status, and remains
  covered by the existing Anki undo snapshot.
- Additive save fields now exist for future combat systems:
  `combat_supply_loadout`, `combat_special_attack_energy`,
  `combat_stat_drains`, `combat_status_effects`, and
  `combat_recovery_progress`.
- `combat_status_effects["poison"]` now stores local source-shaped poison ticks
  and tick progress. Poison advances every 30 source ticks during Combat bursts
  and safe noncombat recovery reviews, applies local
  `Poison.getDamageForTicks` lifepoint damage, clears on death, and can route a
  poison death through the existing Combat grave path. Poison scorpion and
  Poison spider apply this status from source `poisonDamage = 3` attacks with
  the local 4-in-10 NPC poison chance. Antipoison auto-cure, broader enemy
  poison coverage, player weapon poison, poison immunity, and broader status
  effects are still deferred.
- Melee styles route XP as Attack, Strength, Defence, or controlled shared
  Attack/Strength/Defence, with Constitution XP awarded per damage.
- Ranged styles now support standard bows from Shortbow through Magic longbow
  with Bronze through Rune arrow compatibility through the same burst engine.
  Broad arrows stay deferred until the ammo path can enforce their source
  Slayer/level gates. `ranged_accurate` and `ranged_rapid` route damage XP to
  Ranged; `ranged_longrange` splits damage XP between Ranged and Defence; every
  damage hit still awards Constitution XP. Ranged consumes one arrow per attack
  attempt from `combat_supply_loadout["ammo"]`, which refills from inventory
  only at fresh-fight or safe-boundary refill points.
- The Skills hub has a Combat category/card, enemy target tree, attack-style
  selector, availability gate, food-readiness tooltip line, and HUD
  target/lifepoint display.
- Enabled ordinary Combat target rows rated `Death possible` now require
  non-persistent confirmation before the selection callback runs; declining
  leaves the previous target unchanged and no new save flag is added.
- The source-backed Tutorial Island starter kit is available as a one-time Bank
  Claim (`tutorial_island_starter_kit`) that grants Bronze sword, Wooden shield,
  Shortbow, 50 Bronze arrows, Air rune x5, Mind rune x5, Bronze pickaxe, Hammer,
  Bronze hatchet, Tinderbox, and Small fishing net.
- Generic `item_bundle` claim support now handles multi-item Bank Claims without
  custom inventory mutation code.
- Storage config version 23 seeds and sanitizes Combat/claim state while preserving
  the flat save model.

## Source Anchors

- Formula: `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/formula/MeleeCombatFormula.kt`
- Damage roll/old-hitpoint scaling:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/PawnExt.kt`
- Damage XP routing:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/strategy/MeleeCombatStrategy.kt`
- Food healing:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/food/Food.kt`
- Chicken:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/chicken_level_1.plugin.kts`
- Rat:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/rat_level_1.plugin.kts`
- Giant rat:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/critters/giant_rat_level_2.plugin.kts`
- Cow:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions/animals/cow_level_2.plugin.kts`
- Barbarian level 8/9:
  `memory-bank/source-audits/combat-barbarian-2026-06-23.md`
- Barbarian level 10:
  `memory-bank/source-audits/combat-barbarian-level-10-2026-06-23.md`
- Goblin level 2:
  `memory-bank/source-audits/combat-goblin-level-2-2026-06-23.md`
- Drop item IDs:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt`
- Tutorial starter kit:
  `memory-bank/source-audits/combat-tutorial-starter-kit-2026-06-23.md`
- Simple ordinary enemies:
  `memory-bank/source-audits/combat-simple-enemies-2026-06-23.md`
- Spider/drop-range expansion:
  `memory-bank/source-audits/combat-spider-drop-range-2026-06-23.md`
- Scorpion/higher Spider variant expansion:
  `memory-bank/source-audits/combat-scorpion-spider-variants-2026-06-23.md`
- Highwayman expansion:
  `memory-bank/source-audits/combat-highwayman-2026-06-23.md`
- Al-Kharid warrior / nested minor herb table expansion:
  `memory-bank/source-audits/combat-al-kharid-warrior-2026-06-23.md`
- Ranged/ammo path:
  `memory-bank/source-audits/combat-ranged-ammo-2026-06-23.md`
- Ranged bow/ammo progression:
  `memory-bank/source-audits/combat-ranged-progression-2026-06-23.md`
- Standard combat spell ladder:
  `memory-bank/source-audits/combat-standard-spells-2026-06-23.md`
- Dangerous target confirmation:
  `memory-bank/source-audits/combat-danger-confirmation-2026-06-23.md`
- Safe recovery ammo refill:
  `memory-bank/source-audits/combat-safe-recovery-ammo-2026-06-23.md`
- Persistent poison status recovery:
  `memory-bank/source-audits/combat-poison-status-recovery-2026-06-23.md`
- Poison enemy application:
  `memory-bank/source-audits/combat-poison-enemies-2026-06-23.md`

## Deferred

- Broader enemy registry import, including NPCs with nested/shared tables,
  variant splits, access locks, or special mechanics.
- Full non-Smithing combat equipment import/equip support. Wooden shield is now
  source-backed and claimable, but shield mechanics still belong to the broader
  equipment audit.
- God/Ancient/Lunar combat spells with source gates/effects, and noncombat
  Magic actions.
- Broader Ranged equipment/ammunition support beyond the standard bow ladder,
  including Broad arrow gates, composite/ogre/dark/crystal bow families, thrown
  weapons, crossbows/bolts/darts/knives, stack-aware ammunition equipment, ammo
  preference controls, and arrow recovery.
- Prayer effects, drain, and Prayer skilling.
- Antipoison auto-cure, broader enemy poison application, player weapon/ammo
  poison, poison immunity, and non-poison persistent status effects.
- Richer risk previews, including time-to-kill and Wilderness/equipment-risk
  opt-in surfaces.
- Full Death's Office reclaim UI and stacked-death handling. Safe noncombat
  recovery can now advance simple grave recovery, but the complete
  pre-EOC-shaped reclaim surface is still not built.
- Quest combat migration from the existing lightweight quest resolver onto the
  shared combat engine.

## Verification

- `python3 -m py_compile combat_data.py constants.py logic_pure.py storage_pure.py action_registry.py runtime_actions.py target_metadata.py ui.py __init__.py`
- `python3 -m unittest tests.test_combat_logic tests.test_runtime_actions tests.test_storage_pure tests.test_skill_and_item_registry tests.test_target_metadata tests.test_review_hud`
- `python3 -m unittest tests.test_integration_smoke.TestIntegrationSmoke.test_hunter_supply_purchase_runs_once_and_switches_off tests.test_integration_smoke.TestIntegrationSmoke.test_utility_fishing_bait_batches_without_skill_xp tests.test_integration_smoke.TestIntegrationSmoke.test_utility_multiplier_runs_feather_scavenging_ticks tests.test_integration_smoke.TestIntegrationSmoke.test_successful_noncombat_review_applies_one_safe_combat_recovery_and_undo_restores_it tests.test_combat_logic tests.test_storage_pure tests.test_target_metadata`
- `python3 run_tests.py`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
