# Heroes' Quest stage detail audit - 2026-06-22

## Scope

Backend: replaced the generated start-heavy Heroes' Quest row with a focused
stage model in `quest_data.py`. The override keeps startability strict while
moving quest-use inventory, transformations, route state, and combat into the
current-stage blocker layer.

Frontend: no UI contract changes were needed. The existing Quests tab
`blocked_at_stage` display is covered by a new offscreen Qt test for the Black
Arm disguise blocker.

Assets: new Heroes' Quest quest-item icons were fetched into `questitems/` and
recorded in `assets_provenance.json`.

Balance: Darkan's completion XP remains source-backed base XP. Implemented
skills receive XP immediately, while Attack, Defence, Strength, Constitution,
Ranged, and Herblore remain structured pending rewards until those skills exist.

## Source Evidence

- Local Darkan `heroesquest/HeroesQuest.java`: quest handler, 56 quest points,
  Shield of Arrav, Lost City, Dragon Slayer, Merlin's Crystal, Druidic Ritual,
  Cooking 53, Fishing 53, Herblore 25, Defence 25, Mining 50, Blamish-oil rod
  transformation, Fire feather Ice-gloves pickup check, final item consumption,
  and the 12-skill XP reward table.
- Local Darkan `dialogues/AchiettiesHeroesQuestD.java`: Achietties starts the
  quest and requires the cooked Lava eel, Thieves' armband, and Fire feather at
  completion.
- Local Darkan `world/areas/port_sarim/PortSarim.java`: Gerrant grants Blamish
  snail slime during the quest and names the Taverley Dungeon/Lava Maze lava eel
  route.
- Local Darkan Herblore/Fishing/Cooking sources: Blamish oil is
  `Harralander potion (unf)` plus `Blamish snail slime`; lava eel fishing uses
  `Oily fishing rod` plus `Fishing bait`; raw Lava eel cooks into Lava eel at
  Cooking 53.
- Local Darkan `icequeenlair/IceQueenDungeon.java` and `ice_queen.json`:
  the Ice Queen route needs a pickaxe/Mining 50 rockslide and the Ice Queen
  combat stats are resolver-ready.
- Local Darkan Brimhaven dialogues and handlers: Katrine/Straven assign route
  missions, Trobert gives Id papers, the mansion door consumes Id papers for
  Black Arm and 1,000 coins for Phoenix, the candlestick chest produces Pete's
  candlestick, and Katrine/Straven trade it for the Thieves' armband.
- Local 2011Scape `data/cfg/items.yml`: canonical item names for
  `Blamish snail slime`, `Blamish oil`, `Oily fishing rod`, `Raw lava eel`,
  `Lava eel`, `Fire feather`, `Id papers`, `Pete's candlestick`, and
  `Thieves' armband`.
- Pinned historical RuneScape Wiki revision
  `https://runescape.wiki/w/Heroes'_Quest?oldid=6534275`: cross-check for
  release metadata, historical quest details, Grip, partner route note, and
  Ice Queen/Fire Bird combat text.

## Implemented Stage Model

- Stage 1: accept Achietties' three proof item challenge.
- Stage 2: ask Gerrant and produce Blamish snail slime.
- Stage 3: consume Blamish snail slime plus `Harralander potion (unf)` and
  produce Blamish oil.
- Stage 4: consume Blamish oil plus Fishing rod and produce Oily fishing rod.
- Stage 5: route-gated lava eel fishing consumes Fishing bait and produces Raw
  lava eel.
- Stage 6: cook Raw lava eel into Lava eel.
- Stage 7: Ice Queen lair route, Pickaxe, rockslide action, and resolver-ready
  Ice Queen combat produce Ice gloves.
- Stage 8: Entrana route, Ice gloves, and resolver-ready Entranan Fire Bird
  combat produce Fire feather.
- Stage 9: route variants split Phoenix and Black Arm gang setup.
- Stage 10: Black Arm consumes Id papers and requires black armour; Phoenix
  consumes 1,000 coins, requires partner coordination, and carries Grip combat.
  Both produce Pete's candlestick.
- Stage 11: route variants exchange Pete's candlestick for Thieves' armband.
- Stage 12: Achietties consumes Lava eel, Thieves' armband, and Fire feather.
- Stage 13: completed state.

The Ice Queen lair access does not force the Jailer/Dusty key route as a hard
item/combat gate. It is represented as a route-state blocker that covers the
Dusty key or Agility shortcut path; making Jailer mandatory would incorrectly
collapse an alternate route into a required kill.

## Manual Anki Smoke

1. Start Anki with this add-on, open the AnkiScape main menu, and switch to the
   Quests tab.
2. Confirm Heroes' Quest is locked before start because it needs 56 quest
   points, required quests, and unimplemented Defence/Herblore gates.
3. In a test save, mark Heroes' Quest started at progress 2 with current quest
   `heroes_quest`, add the stage action `Ask Gerrant how to catch lava eels`,
   answer one eligible card, and confirm Blamish snail slime appears while
   progress moves to 3.
4. In a test save, mark Heroes' Quest started at progress 10 on the Black Arm
   route with Id papers, black full helm, and black platebody but no black
   platelegs. Confirm the Quests tab shows `Blocked: Needs Black platelegs` and
   the quest action button is disabled.
5. In a test save, mark Heroes' Quest started at progress 12 with Lava eel and
   Thieves' armband but no Fire feather. Answering a quest card should show a
   Quest blocked error, preserve both items, and not award quest points or XP.

## Verification

Focused tests added:

- `tests.test_quest_catalog.TestQuestCatalog.test_heroes_quest_has_source_backed_stage_requirements`
- `tests.test_logic.TestLogic.test_heroes_quest_real_stage_emitters_complete_both_routes`
- `tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_blocks_heroes_final_without_fire_feather`
- `tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_progresses_heroes_gerrant_slime_gate`
- `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_heroes_black_arm_disguise_blocker`
- `tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`

This is a completed Heroes' Quest stage-detail slice, not all-quest parity.
Continue the systematic release-order/generated-row pass after this commit.
