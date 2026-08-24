# Quest Stage Detail Audit: Plague City and Waterfall Quest

Date: 2026-06-22

## Scope

Backend-focused source-backed replacement rows for Plague City and Waterfall
Quest. This replaces generated/broad requirement rows with local Darkan-backed
stage chains that keep startability separate from finishability.

Frontend change is limited to offscreen Qt coverage of the existing Quests tab
blocked-at-stage display for Plague City's hangover-cure step. No UI behavior
was redesigned in this slice.

No status-update HTML was created for this batch because the active user
instruction is to stop status artifacts until the all-quest update is complete.

## Sources

- Local 2011Scape: `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`
  for item identity cross-checks.
- Local Darkan Plague City:
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/plague_city/PlagueCity.kt`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/plague_city/utils/PlagueCityConstants.kt`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/plague_city/utils/PlagueCityUtils.kt`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/plague_city/cutscene/PlagueCityCutscene.kt`
  - Darkan NPC/object dialogues for Edmond, Alrena, Jethick, Ted/Martha/Milli
    Rehnison, the Clerk, Bravek, prison doors, Elena's prison door, and Elena.
- Local Darkan Waterfall Quest:
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/waterfallquest/WaterfallQuest.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/waterfallquest/AlmeraD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/waterfallquest/HudonD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/waterfallquest/GolrieD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/waterfallquest/books/BookOnBaxtorian.java`
- Asset practical fallback: OSRS wiki item images for unchanged legacy quest
  item sprites. `Book on Baxtorian` and `A key` use RuneScape Wiki images where
  the RS3 title is the only resolving canonical art source.

## Captured Rows

### Plague City

| Stage | Gate | Inventory/tool mutation |
| --- | --- | --- |
| 1 | Bring dwellberries to Alrena. | Consumes `Dwellberries x1`; produces `Gas mask x1`. |
| 2 | Talk to Edmond with the gas mask. | Requires `Gas mask x1`. |
| 3 | Soften Edmond's mud patch. | Consumes `Bucket of water x4`; produces `Bucket x4`. |
| 4 | Dig through the softened mud patch. | Requires tool `Spade`. |
| 5 | Pull the sewer grill and ask Edmond for help. | Required actions only. |
| 6 | Tie rope to the sewer grill. | Consumes `Rope x1`. |
| 7 | Ask Edmond to pull the rope. | Required action only. |
| 8 | Enter West Ardougne through the sewer and speak to Jethick. | Requires `Gas mask x1`; requires the sewer-pipe route. |
| 9 | Show Jethick Elena's picture and agree to return his book. | Requires `Picture of Elena x1`; produces `Turnip growing for beginners x1`. |
| 10 | Return Jethick's book to Ted Rehnison. | Consumes `Turnip growing for beginners x1`. |
| 11 | Ask Martha Rehnison about Elena. | Required action only. |
| 12 | Ask Milli Rehnison and the mourners. | Required actions only. |
| 13 | Convince the Clerk and ask Bravek for the cure recipe. | Produces `Scruffy note x1`. |
| 14 | Mix the hangover cure. | Consumes `Chocolate dust x1`, `Bucket of milk x1`, and `Snape grass x1`; requires tool `Pestle and mortar`; produces `Hangover cure x1`. |
| 15 | Give Bravek the cure and ask for a warrant. | Consumes `Hangover cure x1`; produces `Warrant x1`. |
| 16 | Enter the prison house, search the barrel, unlock the cell, free Elena, and report to Edmond. | Requires `Warrant x1`; produces `A small key x1`; completion grants `A magic scroll x1`. |

Generated Plague City item rewards previously included the gas mask as a final
reward. This replacement keeps the source-shaped gas mask as a mid-quest item
and limits final item rewards to `A magic scroll x1`.

### Waterfall Quest

| Stage | Gate | Inventory/tool mutation |
| --- | --- | --- |
| 1 | Speak to Hudon by the waterfall. | Required action only. |
| 2 | Search for and read the Book on Baxtorian. | Produces `Book on Baxtorian x1`. |
| 3 | Search the Tree Gnome Village crate and free Golrie. | Requires the Golrie route; produces `Old key x1` and `Glarial's pebble x1`. |
| 4 | Enter Glarial's tomb and recover the amulet and urn. | Requires `Glarial's pebble x1`; requires tool `Rope`; produces `Large old key x1`, `Glarial's amulet x1`, and `Glarial's urn x1`. |
| 5 | Place the runes and amulet, then use the urn on the chalice. | Requires `Glarial's urn x1`; consumes `Water rune x6`, `Air rune x6`, `Earth rune x6`, and `Glarial's amulet x1`; requires tool `Rope`. |

`Glarial's urn` is retained after completion because the Darkan completion path
does not delete it. Waterfall Quest awards 13,750 Attack XP and 13,750 Strength
XP as pending future-skill rewards because those skills are not implemented yet.

Darkan has two item IDs named `A key` in this quest. They are disambiguated in
AnkiScape as `Old key` and `Large old key`, with both asset entries pointing at
the historical `A key` art title.

## Assets

Fetched or wired quest item icons into `questitems/` with provenance entries:

- `dwellberries.png`
- `gas_mask.png`
- `picture_of_elena.png`
- `turnip_growing_for_beginners.png`
- `scruffy_note.png`
- `chocolate_dust.png`
- `bucket.png`
- `snape_grass.png`
- `pestle_and_mortar.png`
- `spade.png`
- `hangover_cure.png`
- `warrant.png`
- `a_small_key.png`
- `a_magic_scroll.png`
- `book_on_baxtorian.png`
- `old_key.png`
- `large_old_key.png`
- `glarial_s_pebble.png`
- `glarial_s_amulet.png`
- `glarial_s_urn.png`

## Verification

Targeted tests added or updated:

- `tests.test_quest_catalog.TestQuestCatalog.test_local_source_batch_quest_stage_replacements_are_structured`
- `tests.test_logic.TestLogic.test_plague_city_real_stage_emitters_complete_and_reward_once`
- `tests.test_logic.TestLogic.test_waterfall_quest_real_stage_emitters_complete_and_reward_once`
- `tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_progresses_waterfall_book_gate`
- `tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_progresses_waterfall_book_gate`
- `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_plague_city_hangover_cure_blocker`
- `tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`

Audit after this slice:

- quests: 194
- quests_with_stage_requirements: 194
- stage_requirement_rows: 519
- quests_with_item_or_tool_blockers: 174
- quests_with_combat_blockers: 120
- combat_encounter_rows: 285
- combat_encounters_with_any_stats: 183
- combat_encounters_with_resolver_stats: 180
- produced_inventory rows: 68
- statless_combat_encounters: 105

## Remaining Quest-Parity Gap

This slice updates Plague City and Waterfall Quest only. The all-quest goal
remains active: 166 quests still lack explicit source-backed
`QUEST_STAGE_REQUIREMENT_REPLACEMENTS_BY_ID` rows and continue to rely on
generated catalog blockers or focused combat additions until audited.
