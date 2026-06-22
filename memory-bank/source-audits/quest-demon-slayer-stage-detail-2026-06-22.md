# Demon Slayer Source-Backed Stage Detail - 2026-06-22

This slice continues the all-quest stage-parity goal, but it does not complete
that goal. It replaces Demon Slayer's broad generated combat/item row with a
focused source-backed stage chain, proves the item transformations and Delrith
gate in tests, and leaves the remaining catalog debt explicit.

## Source Hierarchy

- Local 2011Scape was checked first. No Demon Slayer quest implementation was
  found in the local 2011Scape plugin tree, but `data/cfg/items.yml` identifies
  item ids 2399, 2400, and 2401 as `Silverlight key`, and item id 2402 as
  `Silverlight`.
- Darkan/2012scape supplied the quest mechanics:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/demonslayer/DemonSlayer.java`
  defines stages 0-9, lists bucket of water, 25 bones, 1 coin, and Delrith plus
  Dark wizard combat in the quest overview, washes the drain key with a bucket
  of water, and starts the final controller only at `SILVERLIGHT_OBTAINED_STAGE`
  when the player has or equips Silverlight.
- Darkan dialogue/controller files supplied concrete transitions:
  `SirPrysinDemonSlayerD.java` adds Silverlight and deletes the three key ids;
  `WizardTraibornDemonSlayerD.java` consumes 25 bones and adds one key;
  `CaptainRovinDemonSlayerD.java` adds one key; `EncantationOptionsD.java`
  stores the incantation order `Aber`, `Gabindo`, `Purchai`, `Camerinthum`,
  `Carlem`.
- Darkan combat files supplied the battle source:
  `DelrithBoss.java` blocks non-Silverlight damage, and
  `data/npcs/combatdefs/uncategorized/delrith (nostats).json` supplies Delrith
  stats: 70 hitpoints, max hit 30, melee style, attack 11, strength 10, defence
  5, magic 1, ranged 1.
- The Darkan final controller creates one level 7 Dark wizard and two level 20
  Dark wizards as supporting attackers, while the quest overview prose says
  three level 20 and two level 7 Dark wizards. The current AnkiScape combat
  contract models required encounter resolution, so the required stage blocker is
  Delrith. The supporting-wizard source detail is recorded in the Delrith
  encounter text and should become battle metadata when full combat simulation
  supports non-required supporting enemies.

## Implemented Model

Backend:

- `quest_data.py` now defines a focused Demon Slayer override with nine internal
  stages. Stage 9 is the completion marker so stage 8 can remain a real
  incantation blocker before completion.
- Stage 1 consumes `Coins x1`.
- Stage 3 consumes `Bucket of water x1`, produces `Bucket x1` and
  `Silverlight key x1`.
- Stage 4 consumes `Bones x25` and produces `Silverlight key x1`.
- Stage 5 produces `Silverlight key x1`.
- Stage 6 consumes `Silverlight key x3` and produces `Silverlight x1`.
- Stage 7 requires `Silverlight x1` as a tool and requires the Delrith combat
  encounter. Combat remains globally locked unless
  `player_data["quest_combat_config"]["resolver_enabled"]` is true.
- Stage 8 requires the incantation action
  `Recite Aber, Gabindo, Purchai, Camerinthum, Carlem`.
- Quest completion grants only 3 quest points. Silverlight is produced during
  the quest and is not duplicated as a completion reward.
- `constants.py` now registers `questitems/` icons for quest-stage item assets.

Frontend:

- The existing Quests tab state surface now covers Demon Slayer's current stage:
  stage 3 shows `Blocked: Needs Bucket of water x1`, and stage 7 shows Delrith as
  either globally combat-locked or resolver-ready depending on the save config
  and combat level.
- The existing `can_start`, `in_progress`, `blocked_at_stage`, `completed`, and
  `locked` states are preserved; these Demon Slayer items are not start locks.

Assets:

- Added `questitems/silverlight.png` and `questitems/silverlight_key.png`, with
  provenance recorded in `assets_provenance.json`.
- The asset source is an OSRS wiki visual fallback. Mechanics remain sourced from
  local 2011Scape item identity and Darkan quest/combat code.

## Audit Numbers

`python3 tools/audit_quest_stage_gate_coverage.py` after this slice:

- 194/194 quests have at least one machine-readable stage requirement.
- 401 stage requirement rows.
- 174 quests have item/tool/option blockers.
- 119 quests have combat blockers.
- 283 combat encounter rows.
- 175 combat encounters are resolver-ready.
- Produced-inventory rows increased to 14.

`python3 tools/audit_quest_combat_stat_gaps.py` still reports 108 statless combat
encounters. This slice does not claim all-quest parity.

## Targeted Verification

- `python3 -m unittest tests.test_quest_catalog tests.test_logic tests.test_runtime_actions tests.test_integration_smoke`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget tests.test_skill_and_item_registry`

Full required verification:

- `python3 run_tests.py` passed with 465 tests (108 skipped).
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
  passed with 465 tests.

## Manual Anki Smoke Checklist

1. Restart Anki with the updated add-on.
2. Open AnkiScape, go to Quests, and start Demon Slayer.
3. At stage 3 with no bucket of water, confirm the card remains visible and says
   `Blocked: Needs Bucket of water x1`; Hide unable to start must not hide it.
4. Add `Bucket of water x1`, answer the quest review, and confirm `Bucket x1`
   plus one `Silverlight key` are produced.
5. At stage 4 without 25 bones, confirm `Blocked: Needs Bones x25`.
6. Add 25 regular `Bones`, answer through stages 4-6, and confirm three keys are
   converted into exactly one `Silverlight`.
7. At stage 7 with combat support disabled, confirm the blocker says combat is
   locked for Delrith level 27.
8. Enable `quest_combat_config.resolver_enabled`, set combat stats high enough,
   and answer the quest review. Confirm Delrith is recorded in
   `quest_combat_encounters` without marking Demon Slayer complete.
9. Answer the normal progress review to reach stage 8 and confirm the incantation
   action is required.
10. Mark the incantation action complete, answer the quest review, and confirm
    Demon Slayer completes with 3 quest points and no duplicate Silverlight.

## Deferred Gaps

- Demon Slayer supporting Dark wizards are recorded as source detail, but not as
  required kill gates because the current combat contract only models required
  encounter resolution. Full battle metadata should handle supporting attackers
  once combat simulation exists.
- 321 generated stage rows remain in the catalog and need the same source-backed
  replacement treatment before all-quest minute-detail parity can be claimed.
- 108 combat rows remain statless and blocked behind the global combat support
  switch.
