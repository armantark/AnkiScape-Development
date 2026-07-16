# All-catalog quest stage-gate audit - 2026-06-22

This audit closes the all-catalog stage-gate update for the current AnkiScape
pre-EOC quest catalog. It should not be read as a claim that every historical
quest dialogue, puzzle flag, route flag, or combat simulation is now reproduced
at minute detail. It does mean every quest row in the plugin now has
machine-readable stage blockers, and unresolved combat rows fail closed instead
of silently allowing quest completion.

## Backend scope

- `tools/build_pre_eoc_quest_catalog.py` remains the source path for generated
  pre-EOC quest catalog data. The generated catalog is not hand-edited.
- The generated catalog emits stage requirements from historical quest item,
  tool, action/checkpoint, route, produced-item, consumed-item, option-group,
  and combat evidence.
- Generated current-stage action checkpoint rows ensure catalog quests without
  focused hand-authored replacements still cannot complete in one start-only
  review path.
- The combat parser now skips no-level list headings such as source prose
  ending in `:` and the Barrows-brothers heading, so those headings do not
  become fake combat encounters.
- The combat quantity parser handles prefix quantities such as `4x Living rock
  brawler` and `3x Warped terrorbirds`. Ambiguous ranges stay unresolved rather
  than being flattened into inaccurate quantities.
- Focused combat rows in `quest_data.py` add or replace source-backed encounters
  where the generator cannot safely infer a machine row:
  - Shilo Village splits Nazastarool into level 91 zombie, level 68 skeleton,
    and level 93 ghost forms.
  - Legends' Quest sets Nezikchened to quantity 3 from historical quest text.
  - The Feud adds the level 75 Tough guy encounter.
  - Recipe for Disaster: Freeing Sir Amik Varze adds the level 227 Black Dragon
    encounter while leaving the Evil Chicken unresolved until enough source
    stats exist.

## Frontend scope

- No new Qt surface was needed in the final slice because the Quests tab already
  consumes the stage-aware backend contract:
  - `quest_availability_state_pure()` supplies `can_start`, `in_progress`,
    `blocked_at_stage`, `completed`, and `locked`.
  - `quest_current_stage_blocker_reasons_pure()` supplies compact player-facing
    blocker labels for missing items/tools, required actions, routes, and
    combat.
  - Existing filters for completed quests, unable-to-start quests, Access,
    Difficulty, Length, and Timeline remain in place.
- `tests/test_main_menu_widget.py` covers representative Qt/offscreen blocker
  labels across item, option, route, action, combat, and missing combat-stat
  cases.

## Current audit output

`python3 tools/audit_quest_stage_gate_coverage.py`:

```text
quests: 194
quests_with_stage_requirements: 194
stage_requirement_rows: 1107
quests_with_item_or_tool_blockers: 174
quests_with_action_blockers: 190
quests_with_route_blockers: 18
quests_with_combat_blockers: 120
combat_encounter_rows: 288
combat_encounters_with_any_stats: 188
combat_encounters_with_resolver_stats: 185
requirement_row_kinds:
  actions: 1013
  consumed_inventory: 107
  consumed_inventory_options: 3
  inventory: 252
  inventory_options: 59
  produced_inventory: 104
  routes: 51
  tools: 148
quests_without_stage_requirements:
```

`python3 tools/audit_quest_combat_stat_gaps.py`:

```text
statless_combat_encounters: 103
classifications:
  darkan_hitpoints_only_metadata: 51
  darkan_missing_resolver_stats: 18
  darkan_same_name_wrong_level: 7
  no_local_source_match: 10
  parser_or_variant_level: 17
```

## Interpretation

- The all-quest start-only failure mode is closed. A quest review now checks the
  current stage and blocks on missing source-backed requirements instead of
  jumping from start to completion.
- Stage blockers are distinct from start locks. The Knight's Sword remains the
  proof case: Mining 10 is still a start requirement, Redberry pie is required
  and consumed at Thurgo's stage, Blurite ore plus two Iron bars are consumed at
  the later materials stage, and 12,725 Smithing XP fires only after legitimate
  completion.
- Combat is intentionally fail-closed. With the global resolver disabled,
  combat blockers surface as locked combat. With the resolver enabled, rows
  missing attack-style-critical source stats surface as `combat_missing_stats`.
- The remaining combat gap list is an audited backlog, not an active silent-pass
  path. It needs either stronger 2011-era local source data, safe Darkan/2012scape
  exact-match evidence, or a future combat simulation/stat-source expansion.

## Deferred gaps

- Minute-detail quest simulation remains open for generated rows that currently
  use broad source-backed action checkpoints instead of every historical
  dialogue, puzzle, and route flag.
- Branch/partner state beyond the current Shield of Arrav route model remains
  intentionally narrow.
- Full combat simulation remains out of scope. Resolver-ready encounters can
  resolve one sourced enemy per Quest review, but combat mechanics are not yet a
  player-facing battle system.
- Rows where source text gives level ranges, player-scaled enemies, optional
  encounters, or metadata-only historical monster pages remain blocked or
  generic until a stronger source class is added.

## Final verification

- `python3 run_tests.py`: 544 tests passed, 124 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`:
  544 tests passed.
- Final completion status artifact:
  `memory-bank/status-updates/archive/2026-06/quest-stage-gates-all-catalog-complete-2026-06-22.html`.
- Postplan mobile URL: `https://p0lvtdijaz75.postplan.dev`.
