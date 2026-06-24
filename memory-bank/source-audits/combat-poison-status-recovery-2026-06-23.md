# Combat Poison Status Recovery - 2026-06-23

## Scope

This slice turns the existing `combat_status_effects` save hook into the first
source-backed persistent Combat status path: player poison tick recovery and
damage during review-driven Combat and safe noncombat time.

## Source Anchors

- Local poison source:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/poison/Poison.kt`
- Local poison timer source:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/mechanics/poison/poison_plugin.plugin.kts`
- Local NPC poison application source:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/combat/Combat.kt`
- Local antipoison source:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/potion/PotionType.kt`

## Implemented Scope

- `combat_status_effects["poison"]` is now sanitized to the known poison schema:
  `ticks_left`, `tick_progress`, and `source`.
- Initial poison damage maps to source poison ticks with `initialDamage * 5 - 4`.
- Poison damage uses the local source curve `((ticksLeft / 5) + 1) * 10`
  lifepoints.
- Poison advances every 30 source ticks during Combat bursts and safe noncombat
  recovery reviews.
- Poison death clears active statuses and reuses the existing Combat grave path.
- The review HUD shows a compact active poison countdown for Combat and
  noncombat review skills.
- Follow-up poison enemy application is now covered in
  `memory-bank/source-audits/combat-poison-enemies-2026-06-23.md`.
- Follow-up antipoison dose handling and poison immunity are now covered in
  `memory-bank/source-audits/combat-antipoison-loadout-2026-06-23.md`.

## Deferred

- Broader enemy poison coverage beyond the first two enabled ordinary poison
  enemies.
- Player weapon/ammo poison application.
- Non-antipoison immunity sources and potion effects.
- Disease, bleed-style statuses, antifire, stat-restore potions, Prayer restore,
  and broader potion/status effect metadata.

## Verification

- `python3 -m py_compile logic_pure.py ui.py tests/test_combat_logic.py`
- `python3 -m unittest tests.test_combat_logic tests.test_storage_pure tests.test_review_hud`
