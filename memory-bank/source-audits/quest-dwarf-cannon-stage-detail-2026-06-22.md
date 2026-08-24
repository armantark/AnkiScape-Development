# Dwarf Cannon stage detail audit - 2026-06-22

## Scope

Focused backend slice for Dwarf Cannon. This replaces the generated broad
`Lvl 2 Goblins` combat blocker with the local Darkan/2012scape quest's actual
noncombat stage flow, while keeping the generated pre-EOC quest reward surface.

## Sources

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/dwarfcannon/DwarfCannon.java`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/dwarfcannon/CaptainLawgofD.java`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/dwarfcannon/LollkD.java`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/dwarfcannon/NulodionD.java`
- `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/developer-information/itemList.txt`
- Generated catalog source for quest metadata/rewards: `https://runescape.wiki/w/Dwarf_Cannon?oldid=6427607`

## Source facts used

- Darkan's Dwarf Cannon quest handler declares `combatText = "None."`.
- The Darkan implementation advances through rail repairs, Lawgof reports,
  Gilob's remains, goblin hideout route, Lollk rescue, toolkit/cannon repair,
  Nulodion handoff, and Lawgof completion dialogue.
- Captain Lawgof gives six `Railing` items before the rail repair step consumes
  them and requires a hammer/tool.
- The watchtower route produces `Dwarf remains` before the Captain Lawgof
  hand-in consumes them.
- Lawgof gives a `Toolkit`; the cannon repair step requires it but does not
  consume it.
- Nulodion gives `Ammo mould` and `Nulodion's notes`; Captain Lawgof consumes
  both before the final recommendation/completion.
- Local item identity confirms: item 14 `Railing`, item 0 `Dwarf remains`,
  item 1 `Toolkit`, item 3 `Nulodion's notes`, and item 4 `Ammo mould`.

## Implementation

- Added a focused `QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID["dwarf_cannon"]`
  chain in `quest_data.py` with thirteen source-backed gate rows and no combat
  encounters.
- Added Dwarf Cannon metadata replacement support so focused stage replacements
  can override generated stage count, journal stages, and combat summary.
- Dwarf Cannon now has 14 total quest states: thirteen active gates plus a
  final completion state, matching the existing focused-quest convention.
- Added quest item registry entries and fetched icons for `Railing`,
  `Dwarf remains`, `Toolkit`, `Nulodion's notes`, and `Ammo mould`.
- `assets_provenance.json` records these new `questitems/` PNGs. The art source
  is OSRS wiki file art as a practical icon fallback; the game mechanics source
  remains local Darkan/2011Scape evidence.
- Removed Dwarf Cannon from the remaining combat-stat gap assertions because
  the local quest source says no combat is required.

## Audit deltas

Post-slice `tools/audit_quest_stage_gate_coverage.py`:

- 194 quests.
- 194 quests with at least one machine-readable stage requirement.
- 471 stage requirement rows.
- 174 quests with item/tool/option blockers.
- 119 quests with combat blockers.
- 284 combat encounter rows.
- 179 combat encounter rows with resolver-ready stats.
- 47 produced-inventory rows.

Post-slice `tools/audit_quest_combat_stat_gaps.py`:

- 105 statless combat encounters remain.
- Classifications: 51 Darkan hitpoints-only metadata rows, 18 Darkan rows
  missing resolver-critical stats, 7 same-name/wrong-level rows, 10 no-local
  source rows, and 19 parser/variant-level rows.

## Tests

Targeted tests added or updated:

- `tests.test_quest_catalog.TestQuestCatalog.test_dwarf_cannon_has_source_backed_noncombat_stage_requirements`
- `tests.test_logic.TestLogic.test_dwarf_cannon_real_stage_emitters_complete_and_reward_once`
- `tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_progresses_dwarf_cannon_repairs_without_goblin_gate`
- `tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_progresses_dwarf_cannon_repairs_without_combat_gate`
- `tests.test_quest_combat_stat_gap_audit`
- `tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`

Required full-suite verification passed:

- `python3 run_tests.py` passed with 498 tests (116 skipped).
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
  passed with 498 tests.

Manual Anki smoke checklist:

1. Open Anki with this add-on, open AnkiScape, and pick Dwarf Cannon in the
   Quests tab.
2. Confirm the quest card shows combat as `None.` and does not show a goblin
   battle as the current blocker.
3. Answer the first Quest review and confirm Captain Lawgof gives
   `Railing x6`, moving the quest to `Dwarf Cannon 2/14`.
4. At `Dwarf Cannon 2/14`, remove the railings or hammer, answer one Quest
   review, and confirm questing turns off with the relevant missing item/tool
   blocker.
5. Restore `Railing x6` and `Hammer x1`, answer one Quest review, and confirm
   the quest advances to `Dwarf Cannon 3/14`, consumes the railings, keeps the
   hammer, and does not create a combat encounter.
6. Walk the remaining stage blockers by adding the required action/route flags
   and items in order: Lawgof repair report, `Dwarf remains`, goblin hideout
   route, Lollk rescue, Lollk safe report, cannon repair, cannon repaired
   report, `Ammo mould` plus `Nulodion's notes`, and final recommendation.
7. Confirm `Dwarf remains`, `Toolkit`, `Ammo mould`, and `Nulodion's notes` are
   produced before their later stages require or consume them.
8. Confirm `750 Crafting XP` and one quest point are awarded only after the
   final recommendation stage completes.

## Quest-Only Item Follow-Up

A later same-day correction split the old repair/remains/Nulodion hand-ins so
the quest first produces `Railing`, `Dwarf remains`, `Ammo mould`, and
`Nulodion's notes`. These items are still real blockers at their current
stages, but they are not treated as impossible external inventory requirements.

## Deferred

This is a focused Dwarf Cannon replacement, not all-quest minute-detail parity.
The remaining generated rows still need per-quest source reconciliation, route
flags, item transformations, branch/partner state, and combat-stat enrichment
before the broad quest-parity goal can be called complete.
