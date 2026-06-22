# Quest Stage Detail Audit: Holy Grail and Tree Gnome Village

Date: 2026-06-22

## Scope

This slice replaces generated broad stage rows for Holy Grail and Tree Gnome
Village with focused source-backed stage requirements in `quest_data.py`. It
does not edit `quest_catalog_generated.py`.

## Sources

- Holy Grail quest handler and item handlers:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/holygrail/HolyGrail.java`
- Holy Grail dialogue stages:
  `KingArthurHolyGrailD.java`, `MerlinHolyGrailD.java`,
  `EntranaHighPriestHolyGrailD.java`, `SirGalahadHolyGrailD.java`,
  `TheFisherKingHolyGrailD.java`, and `SirPercivalHolyGrailD.java` under the
  same Darkan quest package.
- Black Knight Titan behavior and stats:
  `holygrail/BlackKnightTitan.java` and
  `data/npcs/combatdefs/uncategorized/black_knight_titan.json`.
- Tree Gnome Village quest handler and dialogues:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/treegnomevillage/TreeGnomeVillage.java`,
  `KingBolrenTreeGnomeVillageD.java`, `CommanderMontaiTreeGnomeVillageD.java`,
  and `Tracker1/2/3TreeGnomeVillageD.java`.
- Tree Gnome combat stats:
  `data/npcs/combatdefs/uncategorized/khazard_commander (noanims).json` and
  `data/npcs/combatdefs/uncategorized/khazard_warlord (noanims).json`.
- Item identity:
  `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`.
- Historical cross-checks:
  `https://runescape.wiki/w/Holy_Grail?oldid=6393193` and
  `https://runescape.wiki/w/Tree_Gnome_Village?oldid=6541699`.

## Implemented Decisions

- Holy Grail now has an 11-stage internal model so the final source stage can
  be represented as separate AnkiScape item transitions: Magic whistle access,
  Black Knight Titan with Excalibur, Grail bell, Magic gold feather, restored
  realm Holy grail pickup, and King Arthur hand-in.
- The generated false `Brimhaven` inventory requirement is removed. Excalibur
  remains a current-stage tool requirement for the Titan, not a start item lock.
- Black Knight Titan is represented as level 120 with Darkan combat stats. The
  Darkan quest handler text says level 28, but the sourced NPC combat definition
  and the historical quest guide row identify the encounter as level 120.
- Tree Gnome Village now consumes six normal logs at Commander Montai, tracks
  three tracker-coordinate actions, gates the first orb behind two Khazard
  commander combat completions, consumes the first Orb of protection at King
  Bolren, resolves the Khazard warlord for the remaining orbs, and consumes
  `Orbs of protection` at the final hand-in.
- Tree Gnome Village item rewards are narrowed to `Gnome amulet x1`; spirit tree
  access stays an unlock, not a bank item.
- Combat resolution now fails closed when noncombat blockers still exist, even
  if a caller passes a combat encounter id explicitly. This prevents resolving
  the Black Knight Titan before Excalibur, and protects future quest stages with
  route/action/tool prerequisites.

## Assets

Fetched OSRS wiki icon fallbacks for unchanged quest item art:

- `questitems/holy_table_napkin.png`
- `questitems/magic_whistle.png`
- `questitems/grail_bell.png`
- `questitems/magic_gold_feather.png`
- `questitems/holy_grail.png`
- `questitems/orb_of_protection.png`
- `questitems/orbs_of_protection.png`
- `questitems/gnome_amulet.png`

The fetch helper recorded provenance in `assets_provenance.json`. OSRS is used
only as practical sprite art fallback; mechanics and stage gates are backed by
local Darkan/2011Scape evidence above.

## Verification

Targeted checks passed:

- `python3 -m unittest tests.test_quest_catalog.TestQuestCatalog.test_holy_grail_has_source_backed_stage_requirements tests.test_quest_catalog.TestQuestCatalog.test_tree_gnome_village_has_source_backed_stage_requirements tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`
- `python3 -m unittest tests.test_logic.TestLogic.test_holy_grail_stage_gates_excalibur_titan_and_holy_grail_handin tests.test_logic.TestLogic.test_tree_gnome_village_requires_two_commanders_and_warlord_before_completion`
- `python3 -m unittest tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_blocks_holy_grail_titan_stage_without_excalibur tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_completes_holy_grail_final_handoff_and_consumes_grail`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_holy_grail_excalibur_stage_blocker`

Post-slice audit:

- `python3 tools/audit_quest_stage_gate_coverage.py`: 577 stage rows, 104
  produced-inventory rows, 286 combat encounter rows, 181 resolver-ready combat
  rows.
- `python3 tools/audit_quest_combat_stat_gaps.py`: 105 statless combat rows
  remain.

## Still Open

This is not all-quest minute-detail parity. Many catalog rows still rely on
generated broad item/combat rows. Continue the release-order/local-source pass,
replacing generated rows with focused `quest_data.py` replacements when local
Darkan/2011Scape quest handlers provide finer stage evidence.
