# Quest Stage Gates Catalog-Wide Source Audit - 2026-06-22

## Status

This pass broadens the stage-gate model across the generated pre-EOC quest
catalog, but it still does not complete minute-detail parity for every quest.
The important change is that the generator now preserves machine-readable
quest-wide item/tool/alternative requirements and combat encounter rows from
pre-EOC `Quest details` fields instead of leaving those facts only in prose.

Coverage from `python3 tools/audit_quest_stage_gate_coverage.py`:

- 194 total pre-EOC quest rows.
- 179 quests with at least one machine-readable stage requirement.
- 331 generated/runtime stage requirement rows.
- 163 quests with item, tool, or item-alternative blockers.
- 112 quests with combat blockers.
- 274 combat encounter rows.
- 15 combat encounter rows matched local 2011Scape NPC combat stats.

## Source Policy Used

- Primary catalog fields are pinned RuneScape Wiki revisions before the
  2012-11-20 EOC cutoff.
- Journal stage placement still prefers local 2011Scape quest-stage source when
  available, then quick-guide checklist lines, then walkthrough prose.
- Local 2011Scape NPC definition files under
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/content/npcs/definitions`
  are used to enrich generated combat encounters with hitpoints, attack,
  strength, defence, magic, ranged, attack speed, attack style, and defensive
  bonuses when a name/level match is available.
- OSRS sources were not used for this pass.

## Backend Changes

- `tools/build_pre_eoc_quest_catalog.py` now extracts `items` and
  `kills`/`combat` from pre-EOC `Quest details` templates.
- Generated stage requirements can express:
  - `required_inventory`
  - `required_inventory_options`
  - `required_tools`
  - `combat_encounters`
- The parser skips recommended/optional/not-required item and combat prose where
  it can identify that safely, and it models simple coin/item alternatives such
  as `Beer or 2 coins`.
- `quest_data.py` deserializes generated stage rows into
  `QuestStageRequirement` and richer `QuestCombatEncounter` rows.
- `logic_pure.py` adds a global
  `player_data["quest_combat_config"]["resolver_enabled"]` switch. It defaults
  to `False`, so all incomplete combat encounters fail closed as
  `combat_locked` blockers until real battle support exists.
- Storage config version 20 seeds and migrates `quest_combat_config`,
  `quest_combat_encounters`, `quest_stage_actions`, and `quest_route_states`.

## Frontend Changes

- The Quests tab continues to consume the backend lifecycle states:
  `can_start`, `in_progress`, `blocked_at_stage`, `completed`, and `locked`.
- Generated combat blockers surface through the same compact current-stage
  blocker display used by The Knight's Sword item blockers.
- A Qt/offscreen test now proves Demon Slayer displays the generated combat lock
  and disables the quest action while combat is globally disabled.

## Explicit Remaining Gaps

This pass is not the final "every quest down to the most minute detail" goal.
The generated layer is catalog-wide, but it is still quest-wide source-field
extraction, not a completed hand audit of every stage action.

Known gaps:

- 15 runtime quest rows currently have no stage requirements:
  `the_restless_ghost`, `lost_city`, `jungle_potion`, `rune_mysteries`,
  `tai_bwo_wannai_trio`, `mournings_end_part_ii`, `swan_song`,
  `lunar_diplomacy`, `kenniths_concerns`, `legacy_of_seergaze`,
  `deadliest_catch`, `wolf_whistle`, `song_from_the_depths`,
  `carnillean_rising`, and `some_like_it_cold`.
- Several of those are hand-audited overrides in `quest_data.py`; generated
  stage rows should be merged or replaced only after checking the local
  2011Scape/source hierarchy, because overrides may intentionally be stricter
  than wiki prose.
- Exact per-stage placement still needs manual/source-backed audit for many
  quests. The generator infers item stages from journal text and otherwise uses
  a conservative stage row; it does not prove minute-by-minute quest scripting.
- Combat is represented as hard blockers and optional future battle metadata.
  No combat resolver exists yet, so no combat quest can legitimately pass a
  generated encounter unless `quest_combat_encounters` is explicitly marked by a
  future combat system and the global resolver config is enabled.
- Route-specific branches, partner requirements, cat/companion state, subquest
  choices, quest-specific item transformations, and action-family requirements
  remain backlog items unless already captured by a hand override.

## Manual Anki Test Instructions

Use a throwaway Anki profile or back up the current AnkiScape save first.

1. Open AnkiScape and go to the Quests tab.
2. Start Cook's Assistant with no Bucket and no Empty pot. Confirm the quest is
   startable but current progress is blocked with missing item reasons.
3. Add Bucket and Empty pot to the save/inventory, resume Cook's Assistant, and
   confirm the quest can progress and still awards its generated item rewards
   only on completion.
4. Start Demon Slayer and set its progress to the Delrith stage in a test save.
   Confirm the quest card shows `Blocked: Combat locked until battle support is
   enabled: Delrith level 27`, the action button is disabled, and Hide unable to
   start does not hide the started quest.
5. Confirm The Knight's Sword still blocks at Thurgo without Redberry pie,
   consumes the pie when supplied, blocks later on Blurite ore plus two Iron
   bars, and awards 12,725 Smithing XP only on valid completion.
6. Do not enable `quest_combat_config.resolver_enabled` in a live save until a
   real combat resolver writes completed encounter ids from character-vs-NPC
   battle results.

## Verification

- `python3 -m unittest tests.test_quest_catalog tests.test_logic tests.test_storage_pure`
- `python3 -m unittest tests.test_runtime_actions tests.test_integration_smoke`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_stage_blockers_without_hiding_started_quests tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_generated_combat_gate_as_stage_blocker tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_lists_stage_items_before_knights_sword_start`
- `python3 tools/audit_quest_stage_gate_coverage.py`
