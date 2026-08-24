# Combat Tutorial Starter Kit Audit - 2026-06-23

Status: implemented as a one-time Bank Claim.

## Scope

- Adds `tutorial_island_starter_kit` as an always-eligible one-time Bank Claim
  backed by source tutorial handouts, not as a hidden Combat gift.
- Adds generic `item_bundle` claim support so future source-backed bundles can use
  the same claim path instead of custom inventory mutation code.
- Seeds existing saves with an unclaimed flat claim flag through the existing
  claim migration path. Claiming is optional and rollback-safe through the normal
  Anki review/save transaction behavior.

## Source Evidence

2011Scape does not include a complete Tutorial Island implementation in the
local checkout, so this slice uses the local pre-EOC Darkan Tutorial Island
implementation as the source of record, plus local 2011Scape item constants for
identity checks.

| Source | Captured facts |
| --- | --- |
| `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/tutorialisland/CombatInstructor.java:50-60` | Combat Guide/Vannaka grants Wooden shield x1, Bronze sword x1, Shortbow x1, Bronze arrows x50. |
| `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/tutorialisland/MagicInstructor.java:43-47` | Magic Instructor/Terrova grants Air rune x5 and Mind rune x5. |
| `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/tutorialisland/MiningInstructor.java:51-59` | Mining Instructor/Dezzick grants Bronze pickaxe x1 and Hammer x1. |
| `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/tutorialisland/SurvivalExpert.java:41-50` | Survival Expert/Brynna grants Bronze hatchet x1, Tinderbox x1, and Small fishing net x1. |
| `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/cfg/Items.kt` | Confirms item identities including Air rune 556, Mind rune 558, Shortbow 841, Bronze arrow 882, Wooden shield 1171, Bronze sword 1277, and Tinderbox 590. |

## Implemented Claim Contents

- Bronze sword x1
- Wooden shield x1
- Shortbow x1
- Bronze arrows x50
- Air rune x5
- Mind rune x5
- Bronze pickaxe x1
- Hammer x1
- Bronze hatchet x1
- Tinderbox x1
- Small fishing net x1

## Assets

- Existing icons cover Bronze sword, Shortbow, Bronze arrows, Air rune, Mind rune,
  Bronze pickaxe, Hammer, Bronze hatchet, and Small fishing net.
- New `combatitems/` icons were fetched for Wooden shield and Tinderbox through
  `tools/fetch_assets.py`; provenance is recorded in `assets_provenance.json`.
- `constants.COMBAT_ITEM_IMAGES` now reuses existing skill/quest art first, then
  falls back to `combatitems/<slug>.png` for combat-only items.

## Deferred Notes

- The Wooden shield is claimable and registered as an equipment-category item,
  but broad non-Smithing equipment import/equip support is still future Combat
  equipment work. Do not treat this claim as completing full shield mechanics.
- If a real Tutorial Island activity is later implemented, migrate or delete this
  bootstrap claim rather than letting it duplicate source tutorial rewards.

## Verification

- `python3 -m unittest tests.test_logic.TestLogic.test_wicked_hood_claim_requires_rune_mysteries tests.test_logic.TestLogic.test_tutorial_starter_kit_claim_grants_source_backed_bundle_once tests.test_storage_pure.TestStoragePure.test_default_player_data_has_expected_keys tests.test_storage_pure.TestStoragePure.test_migrate_from_old_schema_total_exp tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_registered_asset_paths_exist_for_current_manifest tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_combat_items_are_registered_with_icons`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_bank_claims_expose_eligible_wicked_hood_claim tests.test_main_menu_widget.MainMenuWidgetTest.test_bank_claims_expose_tutorial_starter_kit_bundle tests.test_main_menu_widget.MainMenuWidgetTest.test_bank_claims_hide_locked_rows_entirely tests.test_main_menu_widget.MainMenuWidgetTest.test_bank_claims_inbox_is_capped_above_inventory`
- `python3 run_tests.py` (564 tests, 127 skipped)
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` (564 tests)
- `git diff --check`
