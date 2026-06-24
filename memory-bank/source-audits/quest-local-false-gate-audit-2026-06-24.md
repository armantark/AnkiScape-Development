# Quest-Local False Gate Audit - 2026-06-24

## Scope

This pass followed the Vampyre Slayer beer correction. The target was broad
quest-card requirement text that made quest-local items look like inventory the
player must already own before a quest can proceed.

Backend scope: audit and clean high-confidence quest-wide `Used during quest`
false gates where the same quest already produces the item or grants it through
`start_inventory`.

Frontend scope: no widget changes. The Quests tab consumes the same
`requirements` field, so cleaner backend data removes misleading top-level
quest-card lines.

## Audit Tool

Added `tools/audit_quest_local_item_gates.py`.

The tool reports three categories:

- `quest_wide_same_quest_product`: a quest-wide `Used during quest` line lists
  an item produced by the same quest or granted in that quest's start inventory.
  These are high-confidence false broad gates.
- `stage_requires_same_quest_product_before_source`: a stage requires an item
  before the same quest has produced it. These are high-confidence stage-order
  defects.
- `stage_item_with_acquisition_action`: a stage item blocker appears near
  acquisition wording. These are review candidates only; the script does not
  know whether the item is truly local, buyable, route-specific, or an external
  supply.

`tests/test_quest_catalog.py` now asserts the two high-confidence categories stay
empty.

## Fixed High-Confidence Gates

Removed same-quest-produced or start-inventory items from broad requirement
summaries while preserving their current-stage blockers:

- The Restless Ghost: removed Ghostspeak amulet and Muddy skull from quest-wide
  requirements.
- Ernest the Chicken: removed Pressure gauge, Rubber tube, and Oil can from the
  quest-wide requirements.
- Pirate's Treasure: removed Chest key and Pirate message from the quest-wide
  requirements.
- Dragon Slayer: removed Maze key, Anti-dragon shield, and Map part from the
  quest-wide requirements.
- Witch's House: removed Door key, Magnet, Backroom key, and Ball from the
  quest-wide requirements.
- Heroes' Quest: removed Blamish snail slime, Blamish oil, Oily fishing rod, Raw
  lava eel, Lava eel, Ice gloves, Fire feather, Pete's candlestick, and Thieves'
  armband from the quest-wide requirements.
- Fight Arena: removed Khazard helmet, Khazard armour, Khali brew, and Khazard
  cell keys from the quest-wide requirements.
- Rune Mysteries: removed Air talisman, Research package, and Research notes from
  the quest-wide requirements.

## Remaining Source-Review Candidates

After the cleanup, `python3 tools/audit_quest_local_item_gates.py` reports only
`stage_item_with_acquisition_action` rows:

- Ernest the Chicken stage 5: Spade.
- Merlin's Crystal stage 6: Bread.
- Family Crest stage 12: Antipoison.
- Temple of Ikov stage 8: Limpwurt root.
- Plague City stage 9: Picture of Elena.
- Biohazard stage 11: Priest gown.

These are intentionally not auto-fixed. They need direct quest-source decisions
because the text alone cannot distinguish an easy local pickup from a legitimate
external requirement or route/equipment gate.

## Verification

- `python3 tools/audit_quest_local_item_gates.py`: zero high-confidence
  candidates, six source-review candidates.
- `python3 -m unittest tests.test_quest_catalog`: pass.
- `python3 -m unittest tests.test_quest_catalog.TestQuestCatalog.test_quest_wide_used_during_lines_do_not_gate_same_quest_products tests.test_quest_catalog.TestQuestCatalog.test_source_backed_starter_quest_stage_overrides_replace_generated_guesses tests.test_quest_catalog.TestQuestCatalog.test_heroes_quest_has_source_backed_stage_requirements tests.test_quest_catalog.TestQuestCatalog.test_fight_arena_has_source_backed_stage_requirements`:
  pass.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_vampyre_slayer_easy_items_are_not_prestart_requirements`:
  pass.
- `python3 tools/audit_quest_stage_gate_coverage.py`: 194/194 quests still have
  stage requirements.
- `python3 run_tests.py`: fails in the current dirty worktree on quest-combat
  resolver assertions unrelated to this gate cleanup. The dirty files
  `logic_pure.py`, `runtime_actions.py`, and `storage_pure.py` currently route
  quest combat through ordinary combat bursts and active encounter state, so
  existing tests that expect one-review `combat_resolved` quest encounters now
  fail.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`:
  fails on the same quest-combat resolver assertions.
