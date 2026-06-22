# Merlin's Crystal Stage Detail Audit

Date: 2026-06-22

## Scope

Focused replacement for `merlins_crystal` stage gates. This is a proof slice for
minute-detail quest gating, not a claim that all 194 quests are complete at the
same detail level.

No direct edits were made to `quest_catalog_generated.py`. The replacement lives
in `quest_data.py`, with generated catalog data still supplying unrelated broad
quest metadata.

## Source Policy

Primary mechanics sources:

- Local Darkan/2012scape quest code under `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/merlinscrystal/`.
- Local Darkan NPC combat definition: `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/sir_mordred (noanims).json`.
- Local 2011Scape item identities and Catherby-area spawn evidence from `/Users/ArmanTarkhanian1/Downloads/game-main`.

Cross-check source:

- Historical RuneScape Wiki revision through the pre-EOC window: `https://runescape.wiki/w/Merlin's_Crystal?oldid=6569685`.

Asset-only source:

- New icon files were fetched from wiki image pages through `tools/fetch_assets.py` and recorded in `assets_provenance.json`. OSRS image pages are asset provenance only, not mechanics authority.

## Backend

`quest_data.py` now defines Merlin's Crystal as an 8-stage focused chain. Stage 8
is the completed marker, so the final playable gate is stage 7.

Stage map:

- Stage 1: round-table investigation with Sir Gawain, Sir Lucan, and Sir Lancelot.
- Stage 2: Catherby crate route into Keep Le Faye.
- Stage 3: Sir Mordred combat gate.
- Stage 4: Morgan questioning plus Bucket/Insect repellent beehive wax gate.
- Stage 5: Bucket of wax to Black candle exchange.
- Stage 6: Lady of the Lake test and Port Sarim beggar Bread hand-in, producing Excalibur.
- Stage 7: Bat bones, Black candle, Tinderbox, Excalibur, chaos altar inscription, Thrantax binding words, crystal smash, and King Arthur report.
- Stage 8: quest complete.

Item transitions:

- Bucket is consumed and Bucket of wax is produced at the beehive stage.
- Bucket of wax is consumed and Black candle is produced at the candle-maker stage.
- Bread is consumed and Excalibur is produced during the Lady/Beggar test.
- Bat bones and Black candle are consumed at the ritual stage.
- Excalibur is required as a tool for the crystal smash and remains in inventory.

Combat:

- Sir Mordred is represented as `merlins_crystal_sir_mordred_39` with Darkan stats:
  hitpoints 500, attack 33, strength 33, defence 33, magic 1, ranged 1, max hit
  57, melee/slash style.
- Thrantax is not represented as combat in this slice. Local Darkan binds him
  through ritual dialogue after the correct incantation, so AnkiScape gates that
  step as required actions instead of inventing a battle.

Save compatibility:

- The slice uses existing flat quest side-state keys:
  `quest_stage_actions`, `quest_route_states`, `quest_combat_config`,
  `quest_combat_encounters`, and `quest_combat_encounter_counts`.
- No save migration was required.
- Quest XP and rewards remain completion-only. Merlin's Crystal grants 6 quest
  points and no duplicate Excalibur reward after Excalibur is produced mid-quest.

## Frontend

The existing Quests tab consumes the backend blocker contract. This slice adds
offscreen Qt coverage for:

- A started Merlin's Crystal card blocked at the wax stage with compact
  player-facing text: `Needs Insect repellent x1`.
- A resolver-ready Sir Mordred stage showing `Battle required: Sir Mordred level
  39` and allowing the Quest review action to be selected.

## Assets

New quest item icons:

- `questitems/insect_repellent.png`
- `questitems/bucket_of_wax.png`
- `questitems/black_candle.png`
- `questitems/lit_black_candle.png`
- `questitems/excalibur.png`
- `questitems/bat_bones.png`

`tests/test_skill_and_item_registry.py` now asserts these resolve through
`QUEST_ITEM_IMAGES` and `ITEM_DEFINITIONS`.

## Verification

Targeted checks passed:

```bash
python3 -m unittest tests.test_quest_catalog.TestQuestCatalog.test_merlins_crystal_has_source_backed_stage_requirements tests.test_logic.TestLogic.test_merlins_crystal_stage_gates_items_route_combat_and_reward tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_resolves_merlins_crystal_mordred_before_stage_progress tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_blocks_merlins_crystal_wax_without_repellent
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_merlins_crystal_wax_stage_blocker tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_merlins_crystal_mordred_combat_gate_selection
python3 -m unittest tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons
python3 tools/audit_quest_stage_gate_coverage.py
python3 tools/audit_quest_combat_stat_gaps.py
```

Full-suite verification passed:

```bash
python3 run_tests.py
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests
```

Both suites ran 491 tests successfully.

## Manual Anki Test Instructions

1. Start Anki with this add-on enabled and open the AnkiScape menu.
2. Open Quests and start Merlin's Crystal.
3. Confirm the card shows as in progress but blocked until the round-table action exists.
4. Seed or perform the round-table action and Catherby crate route side states.
5. At stage 3, confirm combat is blocked while `quest_combat_config.resolver_enabled`
   is false.
6. Enable resolver support in player data, give the character at least combat
   level 39 through combat stats, answer one Quest review, and confirm the
   activity gain says `Defeated Sir Mordred` without advancing the quest stage.
7. Advance to the wax stage with only a Bucket and confirm the UI and review
   handler block on `Needs Insect repellent x1`, without consuming the Bucket.
8. Add Insect repellent and Morgan action state, then advance and confirm Bucket
   becomes 0 and Bucket of wax becomes 1.
9. Continue through candle, Bread/Excalibur, and ritual/final report gates; confirm
   Excalibur remains after completion and 6 quest points are awarded once.

## Deferred Gaps

- This slice does not complete minute-detail parity for every quest.
- Broad generated rows still need quest-by-quest source replacement where prose
  does not map cleanly to real per-stage gates.
- 108 combat rows remain statless and hard-blocked by the global combat config or
  resolver-stat checks.
- Full combat simulation remains out of scope; the current resolver writes
  source-backed encounter completion only when the global config is enabled and
  player/source stats pass the existing contract.
