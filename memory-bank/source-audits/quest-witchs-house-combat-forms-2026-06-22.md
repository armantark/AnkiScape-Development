# Quest Witch's House Combat Forms - 2026-06-22

## Scope

This slice does not complete every quest to minute-detail parity. It replaces a
known weak generated combat row for Witch's House with source-backed, resolver
ready battle data and tightens the remaining combat-stat backlog classification
so partial Darkan metadata is not treated as enough for combat.

## Source Priority

- Historical quest walkthrough source:
  `https://runescape.wiki/w/Witch's_House?oldid=6474931`.
- Darkan/2012scape NPC combat definitions:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/witch's_experiment/witch's_experiment_(19) (noanims).json`
  through the matching level 30, 42, and 53 form files.
- Local 2011Scape remains first preference for future quest scripts/NPC
  definitions, but this quest's local stat evidence was not sufficient for the
  four experiment forms.

## Backend Changes

- `quest_data.py` replaces Witch's House generated stage requirements with a
  focused source-backed stage model:
  - Stage 1 keeps the source item gate for `Leather gloves x1` and `Cheese x1`.
  - Stage 2 requires four combat encounters: Witch's experiment Skavid form
    level 19, Spider form level 30, Bear form level 42, and Wolf form level 53.
- Each form records Darkan-backed hitpoints, attack, strength, defence, magic,
  ranged, max hit, attack style/range/bonus, aggressiveness, and source path.
- The combat resolver still writes one encounter id per Quest review and does
  not advance the stage on that same review, so all four forms must be recorded
  before normal stage progression can continue.
- `tools/audit_quest_combat_stat_gaps.py` now splits the old partial Darkan
  bucket into:
  - `darkan_hitpoints_only_metadata`
  - `darkan_missing_resolver_stats`
  - `darkan_incomplete_metadata`

## Frontend Changes

- The Quests tab uses the existing `blocked_at_stage` surface. A started
  Witch's House at the experiment stage shows `Battle required` when the global
  resolver is enabled and the player's combat level is sufficient.
- The resolver-enabled row remains selectable as the active Quest target; no
  start-lock behavior was added.

## Current Audit

`python3 tools/audit_quest_stage_gate_coverage.py`:

```text
quests: 194
quests_with_stage_requirements: 194
stage_requirement_rows: 382
quests_with_item_or_tool_blockers: 171
quests_with_combat_blockers: 119
combat_encounter_rows: 285
combat_encounters_with_any_stats: 153
combat_encounters_with_resolver_stats: 153
requirement_row_kinds:
  inventory: 212
  inventory_options: 63
  tools: 91
quests_without_stage_requirements:
```

`python3 tools/audit_quest_combat_stat_gaps.py`:

```text
statless_combat_encounters: 132
classifications:
  darkan_hitpoints_only_metadata: 74
  darkan_missing_resolver_stats: 6
  darkan_same_name_wrong_level: 9
  no_local_source_match: 16
  parser_or_variant_level: 27
```

## Deferred Gaps

- The 74 hitpoints-only Darkan rows remain blocked until attack, strength, and
  defence evidence exists from source data.
- The 6 `darkan_missing_resolver_stats` rows have more than hitpoints but still
  do not have enough stats for the current combat-level resolver contract.
- The remaining same-name/wrong-level, no-local-source, and parser/variant
  buckets still need quest-specific evidence before promotion.
- Full combat simulation, per-enemy kill loops, branch choice state,
  transformations, required weapons, food/prayer/resource handling, and exact
  per-step quest routing remain open.

## Verification

- `python3 -m unittest tests.test_quest_combat_stat_gap_audit tests.test_quest_catalog tests.test_logic tests.test_runtime_actions tests.test_integration_smoke tests.test_main_menu_widget`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_witchs_house_form_combat_gate_selection`
- `python3 run_tests.py` passed with 425 tests, 99 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
  passed with 425 tests.

## Manual Anki Smoke Checklist

1. Restart Anki with this add-on checkout loaded and use a throwaway profile or
   backed-up save.
2. Set Witch's House to started, progress 2, incomplete.
3. Set `player_data["quest_combat_config"]["resolver_enabled"] = True` only for
   the smoke test and set combat levels high enough for level 53.
4. Open the Quests tab and confirm Witch's House is in progress and shows the
   compact multi-blocker summary beginning with
   `Blocked: Battle required: Witch's experiment (Skavid form) level 19` and
   including Spider, Bear, and `+1 more` for Wolf.
5. Select Witch's House as the active Quest target and complete one successful
   review. Confirm the save records
   `quest_combat_encounters["witchs_house"] =
   ["witchs_house_witchs_experiment_first_form"]`, the quest remains at
   progress 2, and no quest completion reward fires.
6. Repeat reviews or pre-seed the first form id and confirm the next blocker is
   the Spider form, then Bear form, then Wolf form.
7. Disable the resolver and confirm Witch's House shows the global combat-locked
   reason instead of completing.
