# Fight Arena Stage Detail Audit - 2026-06-22

## Scope

Focused backend/frontend slice for Fight Arena. The goal was to replace the
generated start/prose-like requirements with source-backed current-stage gates
without claiming full all-quest parity.

This is not an all-quest completion marker. The all-quest goal still has
generated-row cleanup, route/puzzle state, quest-item transformations, combat
simulation, and combat-stat enrichment gaps.

## Source Tiers Used

- Local 2011Scape item identity: `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` confirms the Khazard disguise, Khali brew, and cell-key item identities used by this slice.
- Local 2011Scape quest implementation: no complete Fight Arena quest mechanics were found in the local 2011Scape checkout, so it was not used for stage ordering.
- Darkan/2012scape quest implementation: `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/fightarena/FightArena.java`.
- Darkan cutscene and dialogues: `FightArenaFightCutsceneController.java`, `LadyServilFightArenaD.java`, `JeremyServilFightArenaD.java`, `LazyGuardFightArenaD.java`, and `AngorFightArenaD.java` under the same `fightarena` package.
- Darkan combat definitions: `data/npcs/combatdefs/uncategorized/bouncer/bouncer_(137).json`, `khazard_ogre (nostats).json`, and `khazard_scorpion (nostats) (noanims).json`.
- Pinned historical wiki row: `https://runescape.wiki/w/Fight_Arena?oldid=6516173` is retained for catalog metadata and human-readable cross-checking. It is not treated as hidden combat-stat evidence.

## Implemented Data Model

- Fight Arena is now a 12-stage focused override in `quest_data.py`.
- The quest remains startable without Khazard disguise items, Khali brew, or cell keys. Those are current-stage gates, not start locks.
- Stage 1 produces `Khazard helmet` and `Khazard armour` from the disguise step.
- Stage 2 requires those disguise items as tools, so worn-equipment support can satisfy the jail-entry gate.
- Stage 3 requires the Jeremy action that identifies the key-holding guard.
- Stage 4 consumes `Coins x5` and produces `Khali brew`.
- Stage 5 consumes `Khali brew` when it is given to the lazy guard.
- Stage 6 requires the key-stealing action and produces `Khazard cell keys`.
- Stage 7 requires the keys and the cell-use action before the arena cutscene.
- Stage 8 gates the Khazard ogre. Darkan supplies hitpoints and max-hit metadata only, so the resolver blocks it as `combat_missing_stats` when combat is enabled.
- Stage 9 gates the Khazard scorpion. It also remains `combat_missing_stats` because Darkan supplies hitpoints and max-hit metadata only.
- Stage 10 gates Bouncer with resolver-ready Darkan melee stats.
- Stage 11 requires returning to Lady Servil before completion.
- General Khazard is intentionally not a mandatory gate; Darkan and the historical quest flow make that fight optional after Bouncer.
- Completion keeps the sourced `2` quest points and `Coins x1000` reward. The `12,175 Attack XP` and `2,175 Thieving XP` rewards are stored in `pending_skill_exp_rewards` because Attack and Thieving are not implemented skills yet.

## Frontend And Assets

- Existing Quests-tab state handling is reused: started Fight Arena can surface `blocked_at_stage` without becoming a start lock.
- A Qt/offscreen test now verifies the stage 8 Khazard ogre row remains disabled with a compact missing-stats blocker.
- A second Qt/offscreen test verifies the later Bouncer stage is selectable/resolvable once the earlier arena fights are already marked complete and the player has enough combat level.
- Quest item icons were fetched into `questitems/` and recorded in `assets_provenance.json` for `Khazard helmet`, `Khazard armour`, `Khali brew`, and `Khazard cell keys`. OSRS wiki sprites are used only as visual assets through the existing provenance flow; mechanics come from the local 2011Scape/Darkan sources and the pinned historical wiki cross-check.

## Verification Snapshot

- Targeted pure/catalog/registry/integration tests passed:
  `python3 -m unittest tests.test_quest_catalog tests.test_logic.TestLogic.test_fight_arena_stage_gates_items_combat_and_reward tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_blocks_fight_arena_statless_combat`.
- Targeted Qt tests passed:
  `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_keeps_historical_metadata_only_combat_rows_blocked tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_fight_arena_bouncer_gate_selection`.
- Combat audit passed:
  `python3 -m unittest tests.test_quest_combat_stat_gap_audit tests.test_quest_historical_wiki_combat_stats`.
- Required full suites passed:
  `python3 run_tests.py` ran 481 tests with 113 expected Qt skips, and
  `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
  ran 481 tests.
- Post-slice stage audit: 194/194 quests with stage requirements, 449 stage requirement rows, 174 quests with item/tool blockers, 120 quests with combat blockers, 285 combat rows, and 177 resolver-ready combat rows.
- `tools/audit_quest_combat_stat_gaps.py` still reports 108 statless combat rows. Fight Arena's ogre and scorpion remain in that debt intentionally because the available source data is not enough for resolver-ready hidden combat stats.

## Manual Anki Test Instructions

1. Start Anki with this add-on checkout active and open AnkiScape -> Quests.
2. Start Fight Arena from the Quests tab. Confirm it can start without Khazard disguise items, Khali brew, or Khazard cell keys.
3. Answer one Quest review. Confirm the quest advances to the disguise stage, Bank inventory gains `Khazard helmet x1` and `Khazard armour x1`, and no quest points or quest XP are awarded.
4. At progress 2, remove or unequip either disguise item. Confirm the quest shows a `Needs Khazard helmet` or `Needs Khazard armour` blocker. Restore both items and answer a Quest review to advance.
5. Add the stage action `Talk to Jeremy about the key holder` in the current debug/manual state model, then answer a Quest review to reach the Khali brew purchase stage.
6. Provide `Coins x5`, answer a Quest review, and confirm the coins are consumed and `Khali brew x1` is produced.
7. Answer the next Quest review and confirm `Khali brew` is consumed when given to the lazy guard.
8. Add the stage actions `Steal the Khazard cell keys from the lazy guard` and `Use the Khazard cell keys on Jeremy's cell`, then confirm stage 6 produces `Khazard cell keys x1` and stage 7 requires those keys before the arena sequence.
9. At stage 8 with `quest_combat_config.resolver_enabled = False`, confirm the Khazard ogre blocker says battle support is globally locked.
10. Enable the resolver and set high player combat stats. Confirm the Khazard ogre now says combat stats are required and cannot advance or award XP.
11. To simulate future battle completion, add the ogre and scorpion encounter ids to `quest_combat_encounters["fight_arena"]`, then reach stage 10. Confirm Bouncer resolves through the combat resolver and the next Quest review moves to the Lady Servil return stage.
12. Add the stage action `Return to Lady Servil for the reward`, answer one Quest review, and confirm the quest completes with 2 quest points, `Coins x1000`, and pending XP entries for `attack_exp: 12175.0` and `thieving_exp: 2175.0`.
13. Answer another Quest review after completion and confirm the reward does not duplicate.

## Remaining Gaps

- Full all-quest parity is still open. This slice proves one more focused quest replacement, not the entire catalog.
- Khazard ogre and Khazard scorpion lack complete source-backed resolver stats and remain blocked with clear data until a better pre-EOC source is found or combat simulation gains another safe path.
- The current action blockers use the existing `quest_stage_actions` save model. There is still no player-facing UI for recording arbitrary dialogue/action flags.
- General Khazard optional combat is not modeled as a completion gate.
- Real combat simulation, route/location state beyond current precedents, puzzle state, and broad generated-row cleanup remain future work.
