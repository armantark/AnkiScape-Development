# Quest Conflict Combat Stat Enrichment - 2026-06-22

## Scope

This follow-up did not complete every quest to minute-detail parity. It made the
remaining quest-combat gap set explicit, fixed one generated item-alternative
shape bug across the catalog, and promoted two previously conflicting combat
rows to resolver-ready status with focused source-backed overrides.

## Source Priority

- Local 2011Scape remains first-preference evidence for quest scripts, journal
  text, object/NPC interactions, and NPC definitions.
- Darkan/2012scape is used when local 2011Scape does not provide enough NPC
  stat evidence.
- Historical runescape.wiki revisions through 2012-11-19 remain the generator
  source for the broad pre-EOC quest-details catalog.

## Changes

- `tools/build_pre_eoc_quest_catalog.py` now preserves generated
  `required_inventory_options` as independent option groups. This matters for
  rows such as Goblin Diplomacy, where `Coins x5 OR Blue dye` and
  `Coins x10 OR Orange dye` are two separate current-stage gates, not one flat
  four-way alternative and not four required items.
- `quest_data.py` now imports nested option groups correctly and serializes
  runtime `QUEST_DATA` in the same grouped shape. The pure blocker parser still
  accepts the earlier flat shape as a compatibility guard.
- Priest in Peril's `Monk of Zamorak level 30` now uses the Paterdomus Darkan
  combat definition after the Darkan quest code proved the quest kill handler
  uses NPC ids 1044-1046. The level 30 id 1046 row supplies hitpoints 250,
  attack 25, strength 25, defence 25, magic 40, ranged 1, max hit 20, and magic
  attack style.
- Troll Stronghold's `Dad level 101` now uses the area-specific
  `areas/death_plateau/dad.json` Darkan combat definition after the Darkan
  Troll Stronghold quest code proved it instantiates `DAD` for the arena fight.
  That row supplies hitpoints 1200, attack 60, strength 120, defence 50,
  max hit 275, and melee attack style.
- `quest_current_stage_resolvable_combat_blockers_pure()` now refuses to expose
  a combat review action while current-stage item/tool/action/route blockers
  are still unmet. This keeps stage order intact: combat can be resolved one
  encounter at a time, but not before earlier current-stage noncombat gates.
- `tools/audit_quest_combat_stat_gaps.py` records the remaining statless combat
  rows and classifies them into follow-up buckets.

## Current Audit

`python3 tools/audit_quest_stage_gate_coverage.py`:

```text
quests: 194
quests_with_stage_requirements: 194
stage_requirement_rows: 382
quests_with_item_or_tool_blockers: 171
quests_with_combat_blockers: 119
combat_encounter_rows: 286
combat_encounters_with_any_stats: 149
combat_encounters_with_resolver_stats: 149
requirement_row_kinds:
  inventory: 212
  inventory_options: 63
  tools: 91
quests_without_stage_requirements:
```

`python3 tools/audit_quest_combat_stat_gaps.py`:

```text
statless_combat_encounters: 137
classifications:
  darkan_partial_metadata_available: 80
  darkan_same_name_wrong_level: 11
  no_local_source_match: 18
  parser_or_variant_level: 28
```

## Deferred Gaps

- The 80 `darkan_partial_metadata_available` rows need a deliberate decision on
  whether partial Darkan rows are acceptable for the combat resolver, or whether
  they should remain blocked until full attack/strength/defence metadata exists.
- The 28 `parser_or_variant_level` rows need quest-specific parsing or explicit
  branch/stage modeling. Examples include multi-form fights and level ranges.
- The 11 `darkan_same_name_wrong_level` rows need source reconciliation before
  any stats can be attached.
- The 18 `no_local_source_match` rows still need historical wiki or additional
  local source evidence.
- This slice does not solve full combat simulation, branch choice state,
  follower/puzzle state, quest-item transformations, or exact per-step routing
  for every quest.

## Verification

- `python3 -m unittest tests.test_quest_catalog tests.test_quest_combat_stat_gap_audit tests.test_logic tests.test_runtime_actions tests.test_integration_smoke`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_conflict_overridden_dad_combat_gate_selection`
- `python3 run_tests.py` passed with 421 tests, 98 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
  passed with 421 tests.

## Manual Anki Smoke Checklist

1. Restart Anki with this add-on checkout loaded.
2. Open AnkiScape, go to Quests, and start or inspect The Knight's Sword.
3. Confirm a started The Knight's Sword at Thurgo's food stage shows
   `Needs Redberry pie x1` and does not complete or award Smithing XP until the
   pie exists in inventory.
4. Enable quest combat resolver in the flat save data only for the smoke test,
   then load Troll Stronghold at progress 2 with Coins or climbing boots
   satisfying the current-stage route gate.
5. Confirm the Quests tab shows `Battle required: Dad level 101` when Twig and
   Troll General have already been recorded, and one Quest review records
   `troll_stronghold_dad_101` without advancing the quest stage.
6. Disable the resolver again and confirm stat-backed combat rows show
   `Combat locked until battle support is enabled` instead of completing.
