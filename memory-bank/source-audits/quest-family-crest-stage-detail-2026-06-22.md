# Family Crest stage detail audit - 2026-06-22

## Scope

Backend: replaced the generated start-heavy Family Crest row with a focused
stage model in `quest_data.py`. The override preserves the Crafting 40,
Magic 59, Mining 40, and Smithing 40 start locks while moving fish, perfect
gold, jewellery, crest pieces, Johnathon's antipoison, Chronozon, and final
Family crest hand-in into current-stage blockers and transformations.

Frontend: no new UI contract was needed. The existing Quests tab
`blocked_at_stage` surface is covered by a new offscreen Qt test for Avan's
perfect jewellery blocker.

Assets: new Family Crest quest-item and gauntlet icons were fetched into
`questitems/` and recorded in `assets_provenance.json`.

Balance: the completion reward is the source-backed Family gauntlets item only.
The generated catalog's extra Chaos/Cooking gauntlet rewards were narrowed
because those are later conversion choices, not quest-completion rewards.

## Source Evidence

- Local Darkan `quests/familycrest/FamilyCrest.kt`: quest stage constants,
  Crafting/Magic/Mining/Smithing start requirements, final Family gauntlets
  reward, and the main Fitzharmon crest flow.
- Local Darkan Family Crest dialogues: Dimintheis start/completion, Caleb's
  cooked fish salad, the Al Kharid gem trader pointer, Avan's perfect ruby
  jewellery request, Boot's perfect-gold route clue, and Johnathon's antipoison
  plus Chronozon handoff.
- Local Darkan `WitchHavenPuzzleFamilyCrest.java`: the Witchaven lever-puzzle
  route to the perfect gold mine.
- Local Darkan `ChronozonBoss.java` and
  `data/npcs/combatdefs/uncategorized/chronozon (noanims).json`: Chronozon
  requires all four elemental blast spells and has resolver-ready level 170
  combat stats.
- Local 2011Scape `data/cfg/items.yml`: canonical item names for moulds,
  perfect gold items, perfect ruby jewellery, crest pieces, Family crest, and
  gauntlets.
- Pinned historical RuneScape Wiki revision
  `https://runescape.wiki/w/Family_Crest?oldid=6548361`: cross-check for
  release metadata, quest requirements, historical details, and Chronozon text.

The local Darkan quest handler text describes Chronozon as level 84 in one
message, but the local NPC/combatdef evidence and historical generated quest
detail identify the fight as level 170. The machine-readable encounter uses
level 170 and records the discrepancy in quest prose.

## Implemented Stage Model

- Stage 1: accept Dimintheis' family-crest recovery request.
- Stage 2: ask Caleb about his crest piece and fish salad.
- Stage 3: consume Shrimps, Salmon, Tuna, Bass, and Swordfish; produce Caleb
  crest.
- Stage 4: ask Caleb where Avan can be found while retaining Caleb crest.
- Stage 5: ask the Al Kharid gem trader about Avan.
- Stage 6: ask Avan about perfect gold ruby jewellery.
- Stage 7: ask Boot where perfect gold is found.
- Stage 8: require Pickaxe, Witchaven route, lever-puzzle action, and mining
  action; produce two Perfect gold ores.
- Stage 9: smelt two Perfect gold ores into two Perfect gold bars.
- Stage 10: consume two Perfect gold bars and two Rubies, require Ring mould
  and Necklace mould, and produce the perfect ruby ring and necklace.
- Stage 11: give Avan the perfect ruby jewellery; produce Avan crest.
- Stage 12: require an unnoted Antipoison plus Caleb/Avan crest proof items,
  then ask Johnathon about Chronozon. The antipoison is not consumed because
  the source says only a small sip is needed.
- Stage 13: require Chronozon's lair route, all four elemental blast hits, and
  resolver-ready Chronozon combat; produce Johnathon crest.
- Stage 14: consume Caleb, Avan, and Johnathon crest pieces; produce Family
  crest.
- Stage 15: consume Family crest at Dimintheis.
- Stage 16: completed state with Family gauntlets reward.

## Manual Anki Smoke

1. Start Anki with this add-on, open the AnkiScape main menu, and switch to the
   Quests tab.
2. Confirm Family Crest is locked before start until Crafting 40, Magic 59,
   Mining 40, and Smithing 40 are met, while the used-during quest items remain
   informational rather than start locks.
3. In a test save, mark Family Crest started at progress 3 with current quest
   `family_crest`, add the five cooked fish, answer one eligible Quest card,
   and confirm the fish are consumed, Caleb crest appears, and progress moves
   to 4.
4. In a test save, mark Family Crest started at progress 10 with two Perfect
   gold bars, both moulds, and only one Ruby. Confirm the Quests tab shows the
   missing Ruby blocker and the quest action button is disabled.
5. In a test save, mark Family Crest started at progress 13 with Caleb crest
   and Avan crest. With the combat resolver disabled, answering a Quest card
   should show a combat-locked quest error and should not produce Johnathon
   crest or complete the quest.

## Verification

Focused tests added:

- `tests.test_quest_catalog.TestQuestCatalog.test_family_crest_has_source_backed_stage_requirements`
- `tests.test_logic.TestLogic.test_family_crest_real_stage_emitters_complete_and_reward_once`
- `tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_blocks_family_crest_jewellery_without_two_rubies`
- `tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_progresses_family_crest_caleb_fish_gate`
- `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_family_crest_jewellery_blocker`
- `tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`

Focused verification passed:

- `python3 -m unittest tests.test_quest_catalog tests.test_logic tests.test_runtime_actions tests.test_integration_smoke tests.test_skill_and_item_registry`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget`
- `python3 tools/audit_quest_stage_gate_coverage.py`
- `python3 tools/audit_quest_combat_stat_gaps.py`

Full verification passed before commit:

- `python3 run_tests.py` - 528 tests, 122 skipped
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests` -
  528 tests

Post-slice audit reports 554 stage rows, 92 produced-inventory rows, 284 combat
encounters, 179 resolver-ready combat encounters, 174 quests with item/tool
blockers, 120 quests with combat blockers, and 105 statless combat rows.

This is a completed Family Crest stage-detail slice, not all-quest parity.
Continue the systematic source-backed quest pass after this commit, and do not
create `memory-bank/status-updates/` artifacts again until every quest in the
catalog has been updated to the required detail level.
