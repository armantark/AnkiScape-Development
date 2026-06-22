# Biohazard Stage Detail Source Audit - 2026-06-22

## Status

Biohazard now has a focused Darkan-backed stage replacement instead of relying
on broad generated quest-detail rows. The quest remains strict to start through
its generated prerequisites, but the West Ardougne route, pigeon distraction,
Mourner HQ item chain, Guidor smuggling route, and King Lathas completion are
current-stage blockers and item mutations.

Coverage after this slice from `python3 tools/audit_quest_stage_gate_coverage.py`:

- 194 total pre-EOC quest rows.
- 194 quests with at least one machine-readable stage requirement.
- 529 runtime stage requirement rows.
- 174 quests with item, tool, or item-alternative blockers.
- 120 quests with combat blockers.
- 285 combat encounter rows.
- 180 combat encounter rows with resolver-ready source stats.

## Source Policy Used

- Local 2011Scape was used for item identity evidence:
  - `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`
- Local Darkan/2012scape was used for quest implementation, stages, item
  transforms, dialogue routes, object actions, and the Mourner combat payload:
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/biohazard/Biohazard.kt`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/biohazard/utils/BiohazardConstants.kt`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/biohazard/utils/BiohazardUtils.kt`
  - Darkan Biohazard NPC/object dialogue files for Elena, Jerico, Omart,
    Kilron, Chemist, Hops, Da Vinci, Chancy, Guidor, Guidor's wife, Varrock
    guards, Guidor's door, Varrock gate, Mourner HQ doors, and the mourner with
    key.
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/areas/west_ardougne/mourner/mourner_(13).json`
- Pinned historical RuneScape Wiki data remains the generated catalog source for
  release-order inclusion, prerequisites, rewards, and historical display
  fields. OSRS was used only as an asset provenance fallback for item icons.

## Backend Changes

- `quest_data.py` adds a focused 14-stage Biohazard journal/stage model.
- Stage-local gates now model:
  - Jerico and Omart route actions before crossing the wall.
  - Bird feed and Pigeon cage production at Jerico's house.
  - Bird feed consumption and retained Pigeon cage use at the release tile.
  - West Ardougne rope-ladder route state.
  - Rotten apple production from the Mourner HQ garden, then rotten apple
    consumption and Doctors' gown production at Mourner HQ.
  - Doctors' gown tool requirement, level 13 Mourner combat, Key production,
    cage unlocking, and Distillator production.
  - Distillator hand-in to Elena, producing Liquid honey, Ethenea, Sulphuric
    broline, and Plague sample.
  - Chemist touch paper production.
  - Priest gown x2 disguise requirement, errand-boy vial route, Guidor hand-in,
    and vial/sample/touch-paper consumption.
  - Elena and King Lathas report actions before completion.
- The Mourner encounter is resolver-ready from Darkan stats:
  hitpoints 190, attack 24, strength 24, defence 24, magic 1, ranged 0,
  max-hit 20, melee style, passive aggression.
- Biohazard quest-required items are registered in `quest_reward_items_as_dict()`
  and icon assets were fetched under `questitems/` with provenance.

## Frontend Changes

- No new UI contract was needed. The Quests tab already consumes
  `blocked_at_stage` reasons for missing items, tools, actions, routes, and
  combat.
- A Qt/offscreen test now proves the Biohazard Guidor stage displays
  `Blocked: Needs Priest gown x2`, disables the quest action button, and keeps
  the quest visible as in-progress rather than treating it as a start lock.

## Explicit Remaining Gaps

- Wrong-dialogue failure branches are source-recorded but not modeled as
  alternate failure states in the current flat quest-progress contract. Examples
  include telling the chemist about the plague sample, giving wrong vials to
  errand boys, and Varrock guard confiscation. The successful source route is
  modeled through required actions and route state.
- The two Priest gown pieces are represented as `Priest gown x2` because the
  local item cache exposes both pieces with the same display name. This preserves
  the real quantity gate without adding synthetic item names.
- Full all-quest minute-detail parity remains open. Biohazard is one more
  focused replacement in that broader pass.

## Manual Anki Test Instructions

Use a throwaway Anki profile or back up the current AnkiScape save first.

1. Start Biohazard in a save that satisfies Plague City, Agility 33, and Magic
   33. Confirm those are start locks, not current-stage item locks.
2. Set Biohazard to progress 3 with the Jerico cupboard and pigeon-cage actions
   present. Answer one Quest card and confirm progress moves to 4 while adding
   `Bird feed x1` and `Pigeon cage x1`.
3. At progress 4, remove Bird feed and confirm the quest is blocked with the
   missing item/tool/route/action reason and does not mark complete.
4. At progress 6, answer the garden stage and confirm `Rotten apple x1` is
   produced before any Mourner HQ stew hand-in consumes it.
5. At progress 7, remove the rotten apple and confirm the stew stage blocks
   without producing `Doctors' gown`.
6. Restore `Rotten apple x1`, advance the stew stage, then keep combat resolver
   disabled and confirm the Mourner stage is
   blocked as combat-locked, with no XP or completion reward.
7. Enable `quest_combat_config.resolver_enabled`, give the test save sufficient
   combat stats, resolve `biohazard_mourner_13`, and confirm the next valid
   stage progress produces Key and Distillator without completing the quest.
8. At progress 11, remove `Priest gown` and confirm the Guidor stage blocks
   without consuming Liquid honey, Ethenea, Sulphuric broline, Plague sample, or
   Touch paper.
9. Restore `Priest gown x2`, route state, and errand-boy actions. Confirm stage
   11 consumes the vials/sample/touch paper and advances.
10. Complete the Elena and King Lathas report stages. Confirm Biohazard awards 3
   quest points, adds `Combat Training Camp x1`, and queues `thieving_exp:
   1250.0` exactly once.

## Quest-Only Item Follow-Up

A later same-day correction split the Mourner HQ garden pickup from the stew
poisoning step. The rotten apple is now produced by Biohazard before it is
consumed, so the player is not blocked on a quest-specific item that cannot be
obtained outside the quest route.

## Verification

- `python3 -m unittest tests.test_quest_catalog.TestQuestCatalog.test_biohazard_has_source_backed_stage_requirements tests.test_logic.TestLogic.test_biohazard_stage_gates_pigeons_mourner_distillator_and_guidor tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_blocks_biohazard_guidor_without_priest_gown tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_progresses_biohazard_pigeon_setup_gate tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_biohazard_guidor_disguise_blocker`
- `python3 -m py_compile quest_data.py tests/test_quest_catalog.py tests/test_logic.py tests/test_runtime_actions.py tests/test_integration_smoke.py tests/test_main_menu_widget.py tests/test_skill_and_item_registry.py`
- `python3 -m json.tool assets_provenance.json`
- `python3 tools/audit_quest_stage_gate_coverage.py`
- `python3 tools/audit_quest_combat_stat_gaps.py`
