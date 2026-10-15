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

On 2026-10-13, candidate `b6a7789398df5ae6c18888743528160b42a297c7` corrects the mansion order to KURT, stair investigation/ascent, then chest search. It also uses the existing repeatable-stage helper to replace one missing Address label at stage 3 or Totem at stage 5. Recovery takes one review and keeps the same stage; the next review consumes the item. An owned item is never replaced during hand-in, and completed quests refuse recovery. Period quest oldid `6326240` (2012-09-30) identifies Totem as a quest item and permits repeat chest pickup before hand-in. Address label oldid `6430778` (2012-10-16) establishes its crate acquisition and quest-item status. Darkan `67615a3fde1e8141c9e0c916dd87ac2589a63b29` corroborates missing-item replacement in the relevant quest phases. Quest items remain outside the carried subset under the existing owner policy.

Both existing icons match the normalized pixels of the recorded period originals: Address label SHA-1 `97a65d17ae0846332e2ca6c5eb3c873e24470097`, revision `2011-11-17T05:28:41Z`; Totem SHA-1 `43bd72adce660ffb6b33a30cf0b6fb8590e27d07`, revision `2011-11-30T01:10:54Z`. Source hashes differ from normalized PNG hashes as expected; no icon changed. The bounded source packet is [the retained manifest](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/goal-resume-2026-10-06/reset-70/tribal-totem-recovery-2026-10-13/source/retention-manifest.json>). The original regression failed on unchanged quest data for both lost items and genuine review recovery. The repaired candidate passed 41 focused Qt checks with no skips; Opus approved without findings. These checks use the real quest/review kernel with fake Anki adapters. Full promotion checks and native/visual acceptance remain separate requirements; this candidate is not landed.

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
  tests.test_logic.TestLogic.test_fishing_contest_real_stage_emitters_complete_and_reward_once \
  tests.test_logic.TestLogic.test_scorpion_catcher_real_stage_emitters_preserve_jailer_gate_and_complete \
  tests.test_runtime_actions.TestRuntimeActions.test_quest_answer_progresses_fishing_contest_pass_emitter \
  tests.test_integration_smoke.TestIntegrationSmoke.test_quest_answer_progresses_fishing_contest_pass_emitter \
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

## Tribal native integration acceptance — 2026-10-15

Root normally merged preserved9928e121 recovery into landed mainf2 in the reused clean Familiarisation checkout, preserving prior branch refs and original source/full9 receipts. Frozen651971f63e78e8c3b7df908894141e1bd358baba has5292 installed files and zero mismatches; handler bytes match9928 and UI matches mainf2. The declared shipped20-note fixture grants only Thieving21/5018XP, with product migration of empty saved containers and no quest progress, proof, item or live-state grants. Ordinary answers earned the complete six-stage quest, both repeated real Bank Discard/recovery paths, later hand-ins and rewards. Six review Undos, two direct-action Undos, five replay pairs and six normal reopen pairs passed complete value/scheduling comparisons;10 Good rows remain. Completion paid1 quest point,1775.0 Thieving XP and5 Swordfish once; the completed button is disabled and a control answer paid nothing further. Actual KURT/stair/chest order remains source-backed because the unchanged UI combines that stage; native proves earned Totem and proof membership. Derived encoded byte order false and raw final LIVE representation false are retained, while actual whole-value save/Undo criteria pass. All eight app launches exited0; final owner guard0 unchangedtrue changes{}, pgrep1 empty. Root-only GUI is released. Complete raw evidence: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/manual-tribal-canonical-native-2026-10-15/report.md`. Independent final merged acceptance, exact full9 and official land remain pending; original41Qt/source-review/source-full9 receipts were not replayed.
