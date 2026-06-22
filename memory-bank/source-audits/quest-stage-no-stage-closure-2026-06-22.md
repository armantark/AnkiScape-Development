# Quest Stage No-Stage Closure Source Audit - 2026-06-22

## Status

This follow-up closes the explicit no-stage gap left by the catalog-wide
stage-gate pass. `python3 tools/audit_quest_stage_gate_coverage.py` now reports
machine-readable stage requirements for all 194 pre-EOC quest rows.

This still is not final minute-detail quest parity. The newly closed rows use
source-backed blockers at the current AnkiScape stage granularity, and several
large quests still need deeper per-action/per-route script audits.

Coverage after this slice:

- 194 total pre-EOC quest rows.
- 194 quests with at least one machine-readable stage requirement.
- 382 runtime stage requirement rows.
- 171 quests with item, tool, or item-alternative blockers.
- 119 quests with combat blockers.
- 286 combat encounter rows.
- 15 combat encounter rows matched local 2011Scape NPC combat stats.
- 0 quests without stage requirements.

## Source Policy Used

- Local 2011Scape was used where it has quest implementation source:
  - `TheRestlessGhost.kt`
  - `RuneMysteries.kt`
  - `LostCity.kt`
- Local Darkan/2012scape was used as implementation evidence where local
  2011Scape is missing or where it clarifies stage constants:
  - `quests/restlessghost/RestlessGhost.java`
  - `quests/junglepotion/JunglePotion.java`
  - `quests/lostcity/LostCity.java`
  - `quests/wolfwhistle/WolfWhistle.java`
- Pinned historical RuneScape Wiki revisions through November 2012 were used for
  later quests and source cross-checks:
  - The Restless Ghost oldid `6355778`
  - Jungle Potion oldid `6555418`
  - Tai Bwo Wannai Trio oldid `6529797`
  - Swan Song oldid `6548264`
  - Kennith's Concerns oldid `6549837`
  - Deadliest Catch oldid `6295312`
  - Wolf Whistle oldid `6327531`
  - Song from the Depths oldid `6467675`
  - Carnillean Rising oldid `6534490`
  - Some Like It Cold oldid `6545099`
- OSRS sources were not used for this slice.

## Backend Changes

- `quest_data.py` now has focused stage requirement replacement/addition maps:
  - Replacement rows are used where generated stage data conflicted with
    stronger local evidence, notably Lost City and Tai Bwo Wannai Trio.
  - Addition rows are used where generated catalog fields had no item/combat
    row but source-backed stage actions exist.
- Generated rows remain the default. Hand overrides keep their own stage data
  where present, focused replacements can override bad generated rows, and
  focused additions can fill known gaps without hand-editing
  `quest_catalog_generated.py`.
- Lost City now uses the local/Darkan level 63 Tree spirit evidence instead of
  inheriting the generated level 101 current-wiki row.
- The Restless Ghost now blocks on the ghostspeak amulet path, the muddy skull
  return, and the level 11 skeleton warlock encounter.
- Rune Mysteries now blocks on its three source-backed delivery actions instead
  of auto-progressing through the delivery chain.
- Jungle Potion now blocks on the five clean herb hand-ins at the current
  four-stage generated granularity.
- Kennith's Concerns, Deadliest Catch, Wolf Whistle, Song from the Depths,
  Carnillean Rising, and Some Like It Cold now have required-action blockers
  from source-backed quest walkthrough stages.
- `logic_pure._has_quest_tool()` now treats a bound Woodcutting hatchet as
  satisfying a generic quest-stage `Hatchet` requirement, matching the existing
  pickaxe/toolbelt behavior.
- Required action and route blocker text now uses compact player-facing labels:
  `Action required: ...` and `Route required: ...`.

## Frontend Changes

- No new UI model was needed. The Quests tab already consumes backend
  `blocked_at_stage` reasons.
- A Qt/offscreen test now proves a formerly no-stage quest, The Restless Ghost,
  displays a required-action blocker and disables the quest action.

## Explicit Remaining Gaps

The no-stage list is closed, but the full active goal remains open.

Known remaining gaps:

- The generator still does not derive full per-stage action rows for every quest
  from historical walkthrough structure. Many rows still rely on conservative
  item/combat placement or focused manual additions.
- Jungle Potion should eventually get a six-stage override matching the Darkan
  stage constants exactly; this slice models all five herb hand-ins but keeps
  the generated four-stage shape.
- Wolf Whistle should eventually get a seven-stage override matching the Darkan
  stage constants exactly; this slice groups its required actions into the
  generated short-quest stage shape.
- Quest-specific item transformations and quest-item acquisition remain mostly
  represented as required actions, not real inventory production chains.
- Combat remains fail-closed. A future resolver must use real player combat
  stats and NPC stats, then write completed encounter ids before
  `quest_combat_config.resolver_enabled` is enabled globally.
- Many combat encounters still lack local 2011Scape NPC stat enrichment because
  the matching NPC definition was not found in this slice.
- Route flags, partner/follower state, companion state, puzzle state, and
  branching quest choices need further source-backed modeling.

## Manual Anki Test Instructions

Use a throwaway Anki profile or back up the current AnkiScape save first.

1. Open AnkiScape and go to the Quests tab.
2. Start The Restless Ghost and set progress to stage 1 in a test save. Confirm
   the card shows `Blocked: Action required: Receive the ghostspeak amulet from
   Father Urhney` and the quest action is disabled.
3. Add the action flag
   `quest_stage_actions["the_restless_ghost"] = ["Receive the ghostspeak amulet from Father Urhney"]`
   and confirm the quest can move past that blocker.
4. Start Lost City with Crafting 31 and Woodcutting 36. Confirm it starts but
   blocks on Shamus, then later blocks on the level 63 Tree spirit until the
   future combat resolver writes the completed encounter id.
5. Start Rune Mysteries in a test save and confirm delivery stages block unless
   their matching `quest_stage_actions` flags are present.
6. Do not enable `quest_combat_config.resolver_enabled` in a live save until a
   real combat resolver writes completed encounter ids from character-vs-NPC
   battle results.

## Verification

- `python3 -m unittest tests.test_quest_catalog tests.test_logic tests.test_runtime_actions tests.test_integration_smoke`
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_stage_blockers_without_hiding_started_quests tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_generated_combat_gate_as_stage_blocker tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_required_action_stage_blocker tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_lists_stage_items_before_knights_sword_start`
- `python3 tools/audit_quest_stage_gate_coverage.py`
