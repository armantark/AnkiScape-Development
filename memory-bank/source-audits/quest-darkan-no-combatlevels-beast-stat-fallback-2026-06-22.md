# Quest Darkan no-combatLevels beast-stat fallback - 2026-06-22

## Scope

This slice extends the generated quest combat-stat enrichment path without hand-editing `quest_catalog_generated.py`.

Backend:
- `tools/build_pre_eoc_quest_catalog.py` now reads Darkan hitpoints/configs even when a combatdef omits `combatLevels`.
- Missing attack/defence/magic/ranged stats may be filled from Darkan `developer-information/beasts.txt` only when the NPC name plus combat level has one stat signature.
- Multi-id Darkan combatdefs are resolved per matched name/level, so dungeoneering-style files can contribute only the exact row needed by the generated quest encounter.

Frontend:
- No new UI contract was required. Existing Quest UI states continue to expose `blocked_at_stage` and enable Quest action buttons only when a resolver-ready current-stage combat blocker exists.

## Local source evidence

- `darkan-world-server/data/npcs/combatdefs/uncategorized/chaos_dwarf_hand_cannoneer (nostats).json`
  - names: `Chaos dwarf hand cannoneer`
  - hitpoints: `1220`
  - attackStyle: `RANGE`
  - maxHit: `110`
  - `combatLevels`: absent
  - Beast rows `8776` and `8777` share one usable signature for level 100: attack 37, defence 50, ranged 50.
- `darkan-world-server/data/npcs/combatdefs/uncategorized/caitlin (nostats) (noanims).json`
  - names: `Caitlin`
  - hitpoints: `20`
  - attackStyle: `MAGIC`
  - maxHit: `3`
  - Beast row `9626` supplies attack 1, defence 1, magic 1, ranged 1 for level 3.
- `darkan-world-server/data/npcs/combatdefs/uncategorized/pit_scabarite (nostats) (noanims).json`
  - names: `Pit scabarite`
  - hitpoints: `950`
  - attackStyle: `RANGE`
  - maxHit: `204`
  - Beast row `11565` supplies attack 1, defence 84, magic 1, ranged 84 for level 150.
- `darkan-world-server/data/npcs/combatdefs/uncategorized/forgotten_mage/dg_forgotten_mage.json`
  - ids cover multiple Forgotten mage levels.
  - The matched quest row is level 74, which maps to beast row `10588`: attack 1, defence 70, magic 70, ranged 1.
- `darkan-world-server/data/npcs/combatdefs/uncategorized/forgotten_ranger/dg_forgotten_ranger.json`
  - ids cover multiple Forgotten ranger levels.
  - The matched quest row is level 75, which maps to beast row `10348`: attack 1, defence 70, magic 1, ranged 70.

## Rows made resolver-ready

- `forgiveness_of_a_chaos_dwarf_chaos_dwarf_hand_cannoneer_100`
- `the_blood_pact_caitlin_3`
- `love_story_pit_scabarite_150`
- `salt_in_the_wound_forgotten_mage_74`
- `salt_in_the_wound_forgotten_ranger_75`

## Rows intentionally left blocked

- TokTz-Ket-Dill Fire monster remains statless: the Darkan combatdef says magic, but the matching beast row does not supply a positive magic stat.
- The Elder Kiln Lava monster remains statless: the combatdef says range, but the matching beast row does not supply a positive ranged stat.
- Love Story Pit iron dragon remains statless: two level-204 local beast candidates have conflicting stat signatures.

## Audit result

After regenerating the catalog:

```text
combat_encounter_rows: 285
combat_encounters_with_any_stats: 164
combat_encounters_with_resolver_stats: 164
statless_combat_encounters: 121
```

Remaining statless classifications:

```text
darkan_hitpoints_only_metadata: 51
darkan_missing_resolver_stats: 18
darkan_same_name_wrong_level: 9
no_local_source_match: 16
parser_or_variant_level: 27
```

## Manual Anki test instructions

1. Open Anki with this add-on enabled.
2. Use a test profile/save where `quest_combat_config.resolver_enabled` is true.
3. Start `Forgiveness of a Chaos Dwarf` and set it to stage 4, or load a fixture save with:
   - `quests["forgiveness_of_a_chaos_dwarf"] = {"started": true, "progress": 4, "completed": false}`
   - attack/strength/defence/constitution/prayer levels around 80.
4. Open the Quests tab and verify the quest shows `Blocked: Battle required: Chaos dwarf hand cannoneer level 100`.
5. Answer one eligible Quest review.
6. Verify the floating feedback says `Defeated Chaos dwarf hand cannoneer`.
7. Verify quest progress remains at stage 4 and the quest is not completed.
8. Verify `quest_combat_encounters["forgiveness_of_a_chaos_dwarf"]` contains `forgiveness_of_a_chaos_dwarf_chaos_dwarf_hand_cannoneer_100`.

## Tests

- `python3 -m unittest tests.test_quest_catalog.TestQuestCatalog.test_generated_catalog_stage_requirements_cover_items_and_combat`
- `python3 -m unittest tests.test_logic.TestLogic.test_no_combat_levels_beast_stat_fight_is_resolver_ready`
- `TestQuestCombatStatGapAudit.test_gap_classification_summary_matches_current_catalog_debt` in `tests/test_quest_combat_stat_gap_audit.py` (removed in bd5103f6, which replaced the pinned gap counts with a recorded source block per statless encounter)
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_no_combat_levels_beast_stat_gate_selection`
