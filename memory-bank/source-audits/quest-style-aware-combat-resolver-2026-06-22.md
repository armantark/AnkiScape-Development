# Quest Style-Aware Combat Resolver Audit - 2026-06-22

## Purpose

This slice does not complete every quest. It narrows the combat backlog by
making the quest combat resolver/generator attack-style aware, so sourced magic
and ranged enemies with zero melee Strength are not falsely treated as statless.

## Source Hierarchy Used

Local 2011Scape was checked first, but it did not provide complete quest/NPC
combat stats for these newly resolved rows. Darkan/2012scape combat definitions
were then used per project source hierarchy, with historical wiki revisions
remaining the quest-row identity and combat-level evidence.

Primary local combat sources:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/h.a.m._mage (noanims).json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/torcher/torcher_(63) (nostats).json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/defiler/defiler_(50) (nostats).json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/fight_kiln/tokhaar-xil.json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/fight_kiln/tokhaar-mej.json`

Historical quest/source identity revisions:

- `https://runescape.wiki/w/Another_Slice_of_H.A.M.?oldid=6548739`
- `https://runescape.wiki/w/The_Void_Stares_Back?oldid=6549183`
- `https://runescape.wiki/w/The_Elder_Kiln?oldid=6579162`

## Backend

The resolver contract is now style-aware:

- Magic encounters require hitpoints, defence, and magic.
- Ranged encounters require hitpoints, defence, and ranged.
- Melee or unknown-style encounters require hitpoints, attack, strength, and defence.
- Complete melee stats remain a fallback when Darkan style metadata is inconsistent, as with TokHaar-Mej.

`tools/build_pre_eoc_quest_catalog.py` now preserves zero-valued Darkan combat
stats and accepts style-complete rows instead of requiring positive melee
attack/strength/defence for every enemy. `logic_pure.py`,
`tools/audit_quest_combat_stat_gaps.py`, and
`tools/audit_quest_stage_gate_coverage.py` use the same style-aware readiness
rule, so runtime, generated data, and audits agree.

New resolver-ready generated rows:

- `another_slice_of_h_a_m_h_a_m_mage_30`
- `the_void_stares_back_torcher_63`
- `the_void_stares_back_defiler_50`
- `the_elder_kiln_tokhaar_xil_140`

This is still one completed current-stage encounter per Quest review behind
`player_data["quest_combat_config"]["resolver_enabled"]`. It is not combat
simulation, hit chance, food, prayer, death, equipment, or quest-specific boss
mechanics.

## Frontend

No new UI state was required. The existing Quests tab `blocked_at_stage`
surface now benefits from the style-aware backend data. For the proof row,
Another Slice of H.A.M. can offer the H.A.M. mage battle while still showing
H.A.M. ranger as missing stats until a source-backed ranger row exists.

Expected compact label:

`Blocked: Battle required: H.A.M. mage level 30, Combat stats required before battle support can resolve: H.A.M. ranger level 30`

## Current Audit Output

`python3 tools/audit_quest_stage_gate_coverage.py`:

```text
quests: 194
quests_with_stage_requirements: 194
stage_requirement_rows: 382
quests_with_item_or_tool_blockers: 171
quests_with_combat_blockers: 119
combat_encounter_rows: 285
combat_encounters_with_any_stats: 157
combat_encounters_with_resolver_stats: 157
```

`python3 tools/audit_quest_combat_stat_gaps.py`:

```text
statless_combat_encounters: 128
classifications:
  darkan_hitpoints_only_metadata: 56
  darkan_missing_resolver_stats: 20
  darkan_same_name_wrong_level: 9
  no_local_source_match: 16
  parser_or_variant_level: 27
```

## Deferred Gaps

The goal is still open. The audit still has 128 statless combat rows, and
minute-detail per-stage quest parity is not complete. Known examples:

- Land of the Goblins remains hitpoints-only/statless for the goblin generals.
- H.A.M. ranger in Another Slice of H.A.M. still has no local source match.
- Vanstrom Klause, Jungle demon, Nomad, and many high-level quest bosses remain blocked until style-critical stats or stronger source reconciliation exist.
- Full combat simulation remains intentionally locked behind the global quest combat config.

## Verification

Focused verification already passed:

```bash
python3 -m unittest tests.test_quest_combat_stat_gap_audit tests.test_quest_catalog tests.test_logic tests.test_runtime_actions tests.test_integration_smoke tests.test_main_menu_widget
```

Result: 255 tests passed, 100 skipped.

Required full-suite verification for this slice passed:

```bash
python3 run_tests.py
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests
```

Results:

- `python3 run_tests.py`: 430 tests passed, 100 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`: 430 tests passed.

## Manual Anki Test Instructions

1. Start Anki with the add-on installed in a test profile.
2. Seed a save with `quest_combat_config.resolver_enabled = True`, `another_slice_of_h_a_m` started at progress `4`, `quest_combat_encounters["another_slice_of_h_a_m"] = ["another_slice_of_h_a_m_sigmund_64"]`, and player combat level at least 40.
3. Open AnkiScape > Quests and verify Another Slice of H.A.M. shows: `Blocked: Battle required: H.A.M. mage level 30, Combat stats required before battle support can resolve: H.A.M. ranger level 30`.
4. Select/answer a card with Quests active and verify the activity gain says `Defeated H.A.M. mage`, quest progress remains `4`, the H.A.M. mage encounter id is recorded, and H.A.M. ranger still blocks progression.
5. Disable `quest_combat_config.resolver_enabled` and verify the same quest becomes combat locked instead of auto-completing.
