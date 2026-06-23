# Quest Choice Branch Context - 2026-06-23

## Scope

Backend and frontend slice for branch/co-op quest choices after the all-catalog
stage-gate pass. The goal was not to turn multiplayer quests into requirement
micromanagement; it was to record the player's single-player path and let
contextual contacts cover the historical co-op pieces.

## Source Tiers Used

- Local 2011Scape item/NPC identity evidence:
  `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml` and
  `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/npcs.yml`.
- Local Darkan/2012scape quest evidence:
  `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/shieldofarrav/`,
  `heroesquest/`, and `templeofikov/`.
- Pinned historical RuneScape Wiki rows already present in generated/focused
  quest data:
  `Shield_of_Arrav?oldid=6326184`,
  `Heroes'_Quest?oldid=6534275`,
  `Temple_of_Ikov?oldid=6538747`,
  `Hazeel_Cult?oldid=6579784`, and
  `The_Void_Stares_Back/Quick_guide?oldid=6549181`.

## Implemented Corrections

- Added structured quest choices to `QuestDefinition`: prompt, stage, options,
  route ids, and source. `quests_as_dict()` serializes this as machine-readable
  catalog data.
- Added pure route-choice helpers:
  `quest_current_stage_choices_pure()` exposes unresolved choices, and
  `apply_quest_route_choice_pure()` validates and stores the selected route in
  flat `quest_route_states`.
- Current-stage blockers now return a `quest_choice` blocker for started quests
  whose stage needs a side/path decision. Review actions cannot progress such a
  stage until the choice is made.
- Shield of Arrav:
  - Stage 4 is a real Phoenix/Black Arm choice rather than two raw route
    blockers.
  - Black Arm weapon-store access is contextual. It no longer requires manual
    Phoenix-partner key handoff actions or a pre-owned `Weapon store key`.
  - The certificate merge consumes only the player's own duplicate half; the
    opposite half comes from the contextual contact.
- Heroes' Quest:
  - The Scarface Pete mansion route inherits the Shield of Arrav gang route
    when available.
  - If no Shield route exists in old saves, stage 9 exposes a fallback
    Phoenix/Black Arm choice.
  - Phoenix mansion setup no longer asks the player to coordinate a Black Arm
    partner as a manual stage action.
- Temple of Ikov exposes the Guardians/Lucien branch as a stage 9 choice rather
  than raw route blockers.
- Hazeel Cult exposes the Ceril/Hazeel side choice at stage 1 before start, and
  final item rewards no longer grant both branch artifacts unconditionally.
- The Void Stares Back exposes the Korasi/Jessika sacrifice choice at stage 5.
- The Quests tab renders compact choice buttons inside the existing quest card,
  disables the quest action until the path is chosen, and persists choices
  through an Anki-side save callback. No review-interrupting modal is used.

## Remaining Gaps

- Hazeel Cult and The Void Stares Back now have player choice state, but their
  remaining generated stage rows still need a later focused minute-detail
  replacement if exact per-side prose/items should differ stage by stage.
- Shield of Arrav and Heroes' Quest use contextual contacts rather than a trade
  UI. That is deliberate for single-player AnkiScape; a future multiplayer or
  explicit partner system should layer on top of the same route state.
- Combat remains governed by the existing quest combat resolver contract:
  source-backed encounters can resolve when enabled and stat-ready; unsupported
  encounters stay blocked instead of silently completing.

## Verification Snapshot

- Targeted pure/catalog/runtime tests:
  `python3 -m unittest tests.test_logic tests.test_quest_catalog tests.test_runtime_actions`
  passed 179 tests.
- Targeted Qt quest/UI tests:
  `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget`
  passed 126 tests.
- Catalog audit:
  `python3 tools/audit_quest_stage_gate_coverage.py` reports 194/194 quests with
  stage requirements, 1,120 stage rows, 121 produced-inventory rows, 288 combat
  encounter rows, and 185/288 resolver-ready combat rows.
- Required full non-Qt command:
  `python3 run_tests.py` passed 550 tests, with the Qt file skipped in the
  non-Qt interpreter.
- Required full Qt/offscreen command:
  `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
  passed 550 tests.

## Manual Anki Smoke

1. Open the AnkiScape menu and go to Quests.
2. Seed or use a save with Shield of Arrav started at stage 4 and no
   `quest_route_states["shield_of_arrav"]`. Confirm the card says
   `Blocked: Choose path: Phoenix Gang or Black Arm Gang`, shows both buttons,
   and the quest action is disabled.
3. Choose Black Arm Gang. Confirm the choice persists after closing/reopening
   the menu.
4. At Shield of Arrav stage 5 on the Black Arm route, confirm there is no
   `Weapon store key` missing-item blocker and no Phoenix partner action text;
   the current blocker is the Weaponsmaster combat gate.
5. Open Hazeel Cult before starting it. Confirm the card asks for
   `Ceril Carnillean` or `Hazeel's cult`, does not list top-level missing
   quest-specific side artifacts, and saves the selected side without starting
   the quest automatically.
