# Dragon Slayer Source-Backed Stage Detail - 2026-06-22

This slice continues the all-quest stage-parity goal, but it does not complete
that goal. It replaces Dragon Slayer's generated quest-wide blocker row with a
focused source-backed stage chain covering Oziach, the Guildmaster briefing,
anti-dragon shield acquisition, Crandor map-piece collection, Lady Lumbridge
repair, Ned's route, Elvarg combat, and the final Oziach report.

## Source Hierarchy

- Local 2011Scape was checked first. It does not implement Dragon Slayer quest
  progression, but it supplies item identity through
  `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` and local
  NPC stat definitions for Melzar's Maze ghosts, skeletons, zombies, and the
  lesser demon.
- Darkan/2012scape supplies the quest mechanics through:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/dragonslayer/DragonSlayer.java`,
  `GuildMasterDragonSlayerD.java`, `OziachDragonSlayerD.java`,
  `OracleDragonSlayerD.java`, `MelzarsMaze.java`,
  `WormBrainDragonSlayerMob.java`, `KlarenseDragonSlayerD.java`,
  `NedDragonSlayerD.java`, `CaptainNedDragonSlayerD.java`,
  `DragonSlayer_BoatScene.java`, and `ElvargBoss.java`.
- Darkan/2012scape combat definitions supply stats for zombie rats, Melzar the
  Mad, and Elvarg. Local 2011Scape combat plugins supply stats for the maze
  ghost, skeleton, zombie, and lesser demon.
- The historical RuneScape Wiki Dragon Slayer old revision
  `https://runescape.wiki/w/Dragon_Slayer?oldid=6461164` was used as
  cross-check/source prose only. It did not override stronger local
  2011Scape/Darkan mechanics.
- Quest item visuals were fetched with `tools/fetch_assets.py` using `uv run
  --with pillow`. The `Map part` storage key uses `File:Map part (Melzar).png`
  as a representative icon because AnkiScape intentionally stores Lozar,
  Thalzar, and Melzar map pieces under one canonical `Map part` key. Asset
  provenance is in `assets_provenance.json`; mechanics remain sourced from local
  item/quest code, not icon pages.

## Implemented Model

Backend:

- `quest_data.py` now defines Dragon Slayer as a 16-stage focused override with
  a 32 quest point start lock. Stage 1 remains blocker-free so starting the quest
  is not flattened into a mid-quest item lock.
- Stage 2 requires accepting Oziach's dragon-slaying challenge.
- Stage 3 requires the Guildmaster's Crandor briefing and produces `Maze key`.
- Stage 4 requires asking Duke Horacio for the anti-dragon shield and produces
  `Anti-dragon shield`.
- Stage 5 requires `Maze key`, blocks on the full Melzar's Maze combat chain
  (zombie rat, ghost, skeleton, zombie, Melzar the Mad, lesser demon), and
  produces one `Map part`.
- Stage 6 models the deterministic Wormbrain payment route: consume
  `Coins x10000` and produce one `Map part`. The combat route exists in source
  but remains deferred until branch/alternative route state can model either
  paying or killing Wormbrain honestly.
- Stage 7 requires asking the Oracle about Thalzar's map piece.
- Stage 8 consumes `Wizard's mind bomb`, `Silk`, `Bowl (unfired)`, and one of
  `Crayfish cage` or `Lobster pot`, then produces one `Map part`.
- Stage 9 consumes three `Map part` items and produces `Crandor map`.
- Stage 10 consumes `Coins x2000` to buy the Lady Lumbridge.
- Stage 11 consumes `Plank x3` and `Steel nails x90`, with `Hammer` as a
  required tool.
- Stage 12 consumes `Crandor map` when Ned is recruited as captain.
- Stage 13 requires sailing to Crandor with Captain Ned.
- Stage 14 requires `Anti-dragon shield`, blocks on Elvarg level 83 combat, and
  produces `Elvarg's head` when the resolved combat stage advances.
- Stage 15 requires `Elvarg's head` plus the Oziach report action before the
  stage 16 completion marker.
- Completion grants exactly 2 quest points plus 18,650 Strength XP and 18,650
  Defence XP. Combat XP remains parked in `pending_skill_exp_rewards` while
  combat skills are not implemented.

Frontend:

- No production frontend change was needed. The existing Quest tab blocker
  surface already renders item-option blockers and resolver-ready combat
  blockers from the shared backend contract.
- Added offscreen Qt coverage for Dragon Slayer's Oracle item option blocker:
  `Blocked: Needs Crayfish cage x1 or Lobster pot x1`.
- Added offscreen Qt coverage for the Elvarg resolver-ready stage:
  `Blocked: Battle required: Elvarg level 83`.

Assets:

- Added quest item icons for `Maze key`, `Anti-dragon shield`, `Map part`,
  `Crandor map`, `Wizard's mind bomb`, `Silk`, `Crayfish cage`, `Lobster pot`,
  `Plank`, `Hammer`, and `Elvarg's head`.
- The asset registry test now asserts each of those item names resolves through
  `QUEST_ITEM_IMAGES` and `ITEM_DEFINITIONS`.

## Audit Numbers

`python3 tools/audit_quest_stage_gate_coverage.py` after this slice:

- 194/194 quests have at least one machine-readable stage requirement.
- 424 stage requirement rows.
- 174 quests have item/tool/option blockers.
- 119 quests have combat blockers.
- 283 combat encounter rows.
- 175 combat encounters are resolver-ready.
- Produced-inventory rows increased to 26.

`python3 tools/audit_quest_combat_stat_gaps.py` still reports 108 statless combat
encounters. This slice does not claim all-quest parity.

## Targeted Verification

- `python3 -m unittest tests.test_quest_catalog.TestQuestCatalog.test_generated_catalog_stage_requirements_cover_items_and_combat`
- `python3 -m unittest tests.test_logic.TestLogic.test_dragon_slayer_real_stage_emitters_complete_and_reward_once`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_dragon_slayer_oracle_item_option_blocker tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_dragon_slayer_elvarg_combat_gate_selection`
- `python3 -m unittest tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`

Full required verification:

- `python3 run_tests.py` passed with 471 tests (111 skipped).
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
  passed with 471 tests.

## Manual Anki Smoke Checklist

1. Restart Anki with the updated add-on.
2. Open AnkiScape, go to Quests, and ensure Dragon Slayer is locked before 32
   quest points.
3. Set 32 quest points, start Dragon Slayer, and confirm it advances to the
   Oziach challenge without requiring the quest-use items at start.
4. At stage 8 with `Wizard's mind bomb`, `Silk`, and `Bowl (unfired)` but no
   cage/pot, confirm the card says
   `Blocked: Needs Crayfish cage x1 or Lobster pot x1`.
5. Add one `Lobster pot`, answer the quest review, and confirm the fixed items
   plus the pot are consumed and one `Map part` is produced.
6. At stage 11 without planks, nails, or hammer, confirm the Lady Lumbridge
   repair blocker lists the missing materials/tool instead of completing.
7. At stage 14 with combat support disabled, confirm Elvarg is globally locked.
8. Enable `quest_combat_config.resolver_enabled`, set combat stats high enough,
   keep `Anti-dragon shield` in inventory, and answer the Quest review. Confirm
   `dragon_slayer_elvarg_83` is recorded without completing the quest on that
   same review.
9. Answer the normal progress review and confirm `Elvarg's head` is produced
   and stage 15 requires reporting to Oziach.
10. Mark the Oziach report action complete, answer the quest review, and confirm
    Dragon Slayer completes with exactly 2 quest points and the Strength/Defence
    XP reward only once.

## Deferred Gaps

- Wormbrain's kill route is not modeled as a branch alternative yet. The current
  slice uses the sourced 10,000 coin payment path so the quest is deterministic
  and does not require both money and combat.
- Full all-quest minute-detail parity remains open. Generated rows still need
  per-stage extraction/replacement, route flags, branch state, puzzle state,
  quest-specific item transformations, and combat stat enrichment.
- 108 combat rows remain statless and blocked behind the global combat support
  switch.
