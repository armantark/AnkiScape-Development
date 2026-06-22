# Quest Local Noncombat Stage Batch

Date: 2026-06-22

## Scope

Backend-only source-backed replacement rows for six local Darkan quest handlers:

- Fishing Contest
- Gertrude's Cat
- Clock Tower
- Monk's Friend
- Tribal Totem
- Scorpion Catcher

No status-update HTML was created for this batch because the active user
instruction is to stop status artifacts until the all-quest update is complete.

## Source Hierarchy Used

- 2011Scape local source was checked first, but these six quest handlers were
  not available there.
- Darkan/2012scape quest handlers and NPC combatdefs supplied the stage
  transitions, item transformations, and Scorpion Catcher jailer stats.
- Historical RuneScape Wiki revision `https://runescape.wiki/w/Fishing_Contest?oldid=6326002`
  was retained as the cross-check for Fishing Contest bait/red-vine-worm
  semantics because Darkan's generic fishing spot evidence is looser than the
  quest-specific guide requirement.

## Captured Rows

### Fishing Contest

- Source files:
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/fishingcontest/FishingContest.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/fishingcontest/DwarfBrothersFishingContestD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/fishingcontest/BonzoFishingContestD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/fishingcontest/GrandpaJackFishingContestD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/fishing/Fishing.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/fishing/Fish.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/fishing/FishingSpot.java`
- Stages now produce the fishing pass, consume the 5-coin entry fee, consume
  garlic at the stranger's pipe, require a fishing rod and one bait option for
  the giant carp, transform raw giant carp into fishing trophy, and consume the
  trophy at completion.
- Era note: quest-specific prose points at red vine worms, while Darkan's
  generic fishing spot path exposes bait. The stage model permits either red
  vine worm or fishing bait and still requires the explicit catch action.

### Gertrude's Cat

- Source files:
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/gertrudescat/GertrudesCat.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/gertrudescat/GertrudeD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/gertrudescat/ShilopWiloughD.java`
- Stages now capture the Shilop/Wilough interaction, 100-coin payment, Lumber
  Yard route, milk-to-bucket transform, raw sardine plus doogle leaves into
  doogle sardine, kittens search, kitten return, and Gertrude completion.

### Clock Tower

- Source files:
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/clocktower/ClockTower.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/clocktower/ClockTowerDungeon.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/clocktower/BrotherKojoClockTowerD.java`
- Stages now produce rat poison before the blocked-door stage consumes it,
  produce all four cogs before the spindle stage consumes them, require bucket
  of water or ice gloves for cog handling, and require reporting the repair to
  Brother Kojo.

### Monk's Friend

- Source files:
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/monksfriend/MonksFriend.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/monksfriend/dialogues/BrotherOmadMonksFriendD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/monksfriend/dialogues/BrotherCedricMonksFriendD.java`
- Stages now produce the child's blanket before Brother Omad's hand-in consumes
  it, then consume the jug of water and logs at the points where the local
  handlers advance quest state. Optional thieves remain prose, not hard combat
  blockers.

### Tribal Totem

- Source files:
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/tribaltotem/TribalTotem.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/tribaltotem/KangaiMauTribalTotemD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/tribaltotem/WizardCrompertyTribalTotemD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/tribaltotem/RPDTEmployeeTribalTotemD.java`
- Stages now model Wizard Cromperty, RPDT depot route, address-label transform,
  mansion infiltration actions, totem production, and Kangai Mau completion.
- Era note: Darkan's completion method has an item-comment conflict around the
  reward. This batch preserves the generated/catalog `Swordfish` reward because
  the quest source reward text and catalog agree on swordfish.

### Scorpion Catcher

- Source files:
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/scorpioncatcher/ScorpionCatcher.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/scorpioncatcher/ThormacScorpionCatcherD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/scorpioncatcher/SeerScorpionCatcherD.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/scorpioncatcher/KhazScorp.java`
  - `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/npcs/combatdefs/uncategorized/jailer.json`
- Stages now produce and later consume the scorpion cage, require Seer
  location knowledge, route-gate each scorpion, and put the Taverley Dungeon
  jailer behind the global quest-combat lock with resolver-ready local stats.

## Assets

Fetched quest item icons into `questitems/` with provenance entries:

- Fishing pass, red vine worm, raw giant carp, fishing trophy, garlic, fishing
  rod
- Bucket of milk, doogle leaves, doogle sardine, three little kittens, pet
  kitten
- White/black/blue/red cogs, rat poison, ice gloves
- Child's blanket, jug of water
- Address label, totem, scorpion cage

`Pet kitten` uses the RuneScape Wiki file title `Pet kitten (white) pet.png` as
a generic kitten icon because there is no generic `Pet kitten.png` file.

## Quest-Only Item Follow-Up

A later same-day correction tightened this batch against the "quest-only item"
bug class: if an item is obtained inside the same quest, the stage graph must
produce it before a later stage can require or consume it. Clock Tower now
produces rat poison and all four cogs before consuming them. Monk's Friend now
produces the child's blanket before consuming it. This keeps those blockers as
quest-route progression, not impossible bank requirements.

## Verification

Targeted tests run after this batch:

```bash
python3 -m unittest \
  tests.test_quest_catalog.TestQuestCatalog.test_local_source_batch_quest_stage_replacements_are_structured \
  tests.test_logic.TestLogic.test_fishing_contest_stage_gates_pass_garlic_catch_and_trophy \
  tests.test_logic.TestLogic.test_scorpion_catcher_stage_exposes_source_backed_jailer_combat_gate \
  tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_blocks_and_progresses_fishing_contest_pass_gate \
  tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_progresses_fishing_contest_pass_gate \
  tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons
```

```bash
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_shows_fishing_contest_current_stage_blocker
```

Required full-suite verification after this batch:

```text
python3 run_tests.py
Ran 504 tests in 8.157s
OK (skipped=117)
```

```text
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests
Ran 504 tests in 106.025s
OK
```

Audit snapshots immediately after the batch:

```text
python3 tools/audit_quest_stage_gate_coverage.py
quests: 194
quests_with_stage_requirements: 194
stage_requirement_rows: 499
quests_with_item_or_tool_blockers: 174
quests_with_combat_blockers: 120
combat_encounter_rows: 285
combat_encounters_with_any_stats: 183
combat_encounters_with_resolver_stats: 180
```

```text
python3 tools/audit_quest_combat_stat_gaps.py
statless_combat_encounters: 105
```

## Remaining Quest-Parity Gaps

- The six quests above are source-backed at current AnkiScape stage granularity,
  but all-quest parity is not complete.
- Remaining work still includes exact per-stage replacement for quests currently
  backed by broad detail-page rows, puzzle/follower/branch state, route/location
  state, remaining quest item transformations, 105 non-resolver-ready combat
  rows, and the eventual real combat surface.
