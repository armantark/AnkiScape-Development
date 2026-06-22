# Quest Combat Resolver Contract Source Audit - 2026-06-22

## Status

This slice moves quest combat from a display-only blocker to a save-safe
resolver contract. The global combat gate still defaults closed, but when
`player_data["quest_combat_config"]["resolver_enabled"]` is explicitly enabled,
only source-backed NPC stat rows can be resolved. Encounters without minimum
NPC stats remain blocked even with the resolver on.

This is not full combat parity. It is the first generic write path that future
combat work can replace or deepen without changing every quest row.

## Source Policy Used

- Player combat level formula:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/plugins/src/main/kotlin/gg/rsmod/plugins/api/ext/PlayerExt.kt`
  `calculateAndSetCombatLevel()`.
- NPC combat stat schema:
  `/Users/ArmanTarkhanian1/Downloads/game-main/game/src/main/kotlin/gg/rsmod/game/model/combat/NpcCombatDef.kt`.
- Stat-backed proof encounter:
  `quest_catalog_generated.py` row for Vampyre Slayer / Count Draynor, generated
  from historical RuneScape Wiki oldid `6326248` and enriched from local
  2011Scape Count Draynor NPC combat definition.

## Backend Changes

- `logic_pure.player_combat_level_pure()` implements the local 2011Scape combat
  level formula from Attack, Strength, Defence, Constitution, Prayer, Ranged,
  Magic, and Summoning levels.
- `quest_current_stage_blockers_pure()` now distinguishes:
  - `combat_locked`: global resolver disabled.
  - `combat_missing_stats`: resolver enabled but the encounter lacks minimum
    source-backed NPC stats.
  - `combat_underpowered`: resolver enabled and stats exist, but the player's
    calculated combat level is below the encounter's source combat level.
  - `combat_encounter`: resolver enabled, source stats exist, and the player is
    strong enough to resolve the battle.
- `apply_quest_combat_encounter_pure()` is the only runtime-facing pure helper
  added in this slice that writes completed encounter ids to
  `quest_combat_encounters`.
- `runtime_actions.handle_quest_answer()` resolves one current-stage
  `combat_encounter` blocker per successful Quest review, saves the encounter
  flag, and does not advance the quest stage on the same review.
- Normal quest progression still calls `apply_quest_progress_pure()` and remains
  blocked until the combat encounter id has been written.

## Frontend Changes

- The Quests tab still labels in-progress combat as `Blocked: Battle required`
  when the resolver is globally enabled and the player can resolve the battle.
- A quest with a resolver-ready combat blocker can be selected as the active
  Quest review target.
- Missing items, tools, actions, routes, missing combat stats, underpowered
  combat, and globally locked combat continue to disable selection.

## Explicit Remaining Gaps

- Only 15 combat encounter rows currently carry local 2011Scape NPC stats. The
  rest remain `combat_missing_stats` after the resolver is enabled and need
  source-backed stat enrichment before they can be fought.
- The resolver uses a deterministic combat-level gate, not a full pre-EOC hit
  chance, max-hit, prayer, equipment, style, food, special attack, multi-enemy,
  or death/resource simulation.
- Quantity rows still resolve as one grouped encounter flag. A later full combat
  model should decide whether multi-kill quest rows require one review per enemy
  or a grouped encounter battle.
- Quest-specific combat mechanics, immunities, safespots, required weapons,
  transformations, and companion mechanics still need quest-by-quest source
  audits.
- Existing save data can still contain already-completed encounter ids from
  earlier builds or manual test setup; runtime code now has a resolver write
  path, but save-file tamper proofing is outside this slice.

## Manual Anki Test Instructions

Use a throwaway Anki profile or back up the current AnkiScape save first.

1. Enable `player_data["quest_combat_config"]["resolver_enabled"] = True` only
   in the throwaway save.
2. Start Vampyre Slayer, set progress to stage 1, and provide Garlic, Coins, and
   Beer in inventory so only Count Draynor combat remains blocked.
3. Set combat stats to at least Attack 40, Strength 40, Defence 35,
   Constitution 40, and Prayer 20.
4. Open the Quests tab and confirm Vampyre Slayer shows
   `Blocked: Battle required: Count Draynor level 37` and can be selected.
5. Complete one successful review with Quests active. Confirm the save gains
   `quest_combat_encounters["vampyre_slayer"] =
   ["vampyre_slayer_count_draynor_37"]`, the quest stage does not advance on
   that same review, and no quest completion XP or points fire early.
6. Repeat with low combat stats and confirm the quest blocks as underpowered.
7. Repeat with a combat quest whose encounter lacks `npc_stats` and confirm it
   stays blocked as requiring combat stats.

## Verification

- `python3 -m unittest tests.test_logic tests.test_runtime_actions tests.test_integration_smoke`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_generated_combat_gate_as_stage_blocker tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_resolver_ready_combat_gate_selection`
- `python3 tools/audit_quest_stage_gate_coverage.py`
- `python3 run_tests.py` passed with 404 tests and 94 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`
  passed with 404 tests.
