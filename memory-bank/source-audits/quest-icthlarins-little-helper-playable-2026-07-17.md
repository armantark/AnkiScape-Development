# Icthlarin's Little Helper playable quest audit — 2026-07-17

## Scope

Backend: replaced the generated objective placeholders and statless Combat
rows with a playable eight-stage quest chain plus the existing completion
sentinel. The override models the Wanderer's hypnosis, canopic-jar custody,
Sphinx token, exactly one jar-bound guardian, the Sophanem ceremony, the
holy-to-unholy symbol transformation, the Possessed Priest, and exact ordinary
completion rewards.

Frontend: no new widget contract was needed. The existing Quests tab exposes
both Combat boundaries through the normal action surface and renders the
registered quest-item icons.

Assets: the canopic jar, Sphinx's token, ceremony supplies, quest symbols, and
Catspeak amulet use RuneScape Wiki file revisions dated before the
2012-11-20 cutoff. The historical fetcher now accepts `--before` and records
the selected file revision in `assets_provenance.json`.

Balance: ordinary completion awards two quest points, 4,500 Thieving XP,
4,000 Agility XP, 4,000 Woodcutting XP, one Catspeak amulet, and Sophanem
access through quest completion. Squeal of Fortune spins are outside the
current AnkiScape reward model.

## Historical evidence

- `Icthlarin's Little Helper`, oldid `6588923`, timestamp
  `2012-11-19T22:27:41Z`:
  <https://runescape.wiki/w/Icthlarin%27s_Little_Helper?oldid=6588923>.
  Literal wikitext supplies the ordered quest sequence, item custody, four
  possible guardians, ceremony supplies, Possessed Priest, and ordinary
  rewards.
- The quick guide has no revision at or before the cutoff. It is
  `source_blocked` for this implementation rather than silently substituted
  with a later guide.
- Item pages:
  `Canopic jar` oldid `6315491`,
  `Sphinx's token` oldid `6520569`,
  quest `Holy symbol` oldid `6352893`,
  quest `Unholy symbol` oldid `6315484`,
  `Linen` oldid `5787786`,
  `Bucket of sap` oldid `6288759`, and
  `Catspeak amulet` oldid `6357174`.
  These pages establish quest-item identity and custody.
- Guardian pages:
  `Apmeken apparition` oldid `5795222`,
  `Het apparition` oldid `6178412`,
  `Crondis apparition` oldid `6342246`, and
  `Scabaras apparition` oldid `6378180`.
  The four possibilities span level 75–81, 600–750 LP, approximate maximum
  hits 80–90, and melee and/or Magic.
- `Possessed Priest`, oldid `6032196`, timestamp
  `2012-08-03T20:48:03Z`: level 126, 800 LP, aggressive Magic using bolt
  spells, an approximate maximum hit of 140, guaranteed Bones, and exactly one
  random four-dose Attack, Strength, Defence, Magic, or Agility potion.
- OpenRS2 rev 742, dated `2012-11-07`, SHA-256
  `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`:
  item 4677 is `Catspeak amulet`; 4678–4681 are the four canopic-jar variants;
  4682 and 4683 are the quest holy and unholy symbols; 4684 is `Linen`; 4687
  is `Bucket of sap`; 4689 is `Pile of salt`; and 4691 is `Sphinx's token`.
- Darkan checkout
  `01b49925e5771b1dab478da3cf455670ce9d7e8a`,
  `IcthlarinsLittleHelper.kt`, corroborates the stage order, inventory
  exchanges, Sphinx answer, guardian branch, and quest completion lifecycle.
  Its Possessed Priest combat definition supplies Attack 90, Strength 90,
  Defence 40, Magic 60, and Ranged 1. The direct cutoff page wins for the
  period maximum hit.
- RuneScape Wiki file history supplies the selected original revisions:
  `Bucket of sap` from `2011-11-18T18:06:50Z`,
  `Canopic jar of Het` from `2012-01-03T21:35:11Z`,
  `Catspeak amulet` from `2009-09-04T21:57:16Z`,
  quest `Holy symbol` from `2011-11-22T22:46:08Z`,
  `Pile of salt` from `2011-11-27T01:35:05Z`,
  `Sphinx's token` from `2011-11-28T23:38:05Z`, and
  quest `Unholy symbol` from `2010-05-15T13:58:58Z`.

## Implemented model

1. Bring any following cat variant, surrender a Tinderbox and Waterskin (4) to
   the Wanderer, enter Sophanem under hypnosis, and recover one representative
   canopic jar.
2. Answer nine to the Sphinx's family riddle and receive her token before
   consulting the High Priest.
3. Consume the Sphinx's token at the High Priest authorization and the jar when
   it is placed in its matching burial chamber.
4. Defeat one `Canopic guardian` representing the one-of-four jar assignment.
   The victory action restores the assigned jar to the carried pack.
5. Return the restored jar, spend 30 coins for linen, and consume one willow
   log, one empty bucket, and either a pile or bag of salt. A knife gates
   evergreen sap collection; the ceremony then produces the quest holy symbol.
6. Transform the quest holy symbol into the quest unholy symbol during the
   memory.
7. Consume the unholy symbol while hiding it in the eastern sarcophagus.
8. Defeat the Possessed Priest, break Amascut's hypnosis, and report to the
   High Priest.
9. Enter the existing completion sentinel and award only the ordinary
   completion rewards.

Pyramid navigation, the sarcophagus puzzle, the Sphinx conversation, jar
matching, ceremony dialogue, memories, and the Carpenter's wait are named
`auto_actions`. Each line states what is happening without inventing map
state, a separate puzzle interface, or wall-clock delay.

## Explicit abstractions and source blocks

- The historical quest assigns exactly one of four canopic jars and guardians.
  AnkiScape flattens that hidden branch into one `Canopic guardian` line rather
  than presenting a fake player choice or requiring four fights.
- The token handoff and jar placement share one pre-combat review transaction.
  After the guardian dies, the jar is restored to the carried pack; the next
  review returns it to the High Priest with the ceremony supplies. The jar is
  not carried during Combat.
- The four guardian pages establish the visible range but the local Darkan
  implementation has placeholder combat definitions. The resolver uses the
  period upper bound—level 81, 750 LP, maximum hit 90—with an internally
  consistent level-81 combat-stat adapter. Those hidden stats are a labeled
  bounded abstraction, not a historical claim.
- The correct Sphinx answer is flattened into the stage line. Wrong-answer
  conversation loops do not create a materially different AnkiScape review
  outcome and are not presented as a separate action.
- `Linen` and `Bucket of sap` are represented by the sourced 30-coin purchase
  and evergreen collection inside the ceremony transaction rather than as
  pre-owned intermediate inventory items. The empty bucket is consumed and the
  Knife remains a required reusable tool.
- `Pile of salt` remains a historically accepted alternative, but its live
  acquisition route is not yet implemented. `Bag of salt` is reachable and
  prevents a quest soft-lock; the missing pile route is recorded dependency
  debt rather than silently removing a period-valid option.
- The Carpenter's original waiting interval is flattened into the review
  action. Gameplay never reads the wall clock.
- The Possessed Priest's guaranteed Bones and one random four-dose potion are
  sourced, but `QuestCombatEncounter` currently has no drop transaction
  schema. Exact potion selection probability is also `source_blocked`. The
  omission is recorded implementation debt; the quest does not invent a drop
  distribution.
- The current acquisition graph produces a `Kitten`. `Cat`, `Overgrown cat`,
  and `Hellcat` remain accepted historical alternatives but do not yet have
  independent acquisition routes in AnkiScape.
- Squeal of Fortune spins are not implemented as a reward currency and are
  omitted rather than converted into another reward.

## Verification mapping

- `tests.test_quest_catalog.TestQuestCatalog.test_icthlarins_little_helper_is_a_playable_source_backed_dependency`
  protects stage order, item flow, exact rewards, one-of-four flattening, and
  rev-742 item identities.
- `tests.test_logic.TestLogic.test_icthlarins_little_helper_stage_chain_resolves_guardian_ceremony_and_priest`
  runs the complete pure chain, both Combat boundaries, all transactions, and
  exact completion XP.
- `tests.test_integration_smoke.TestIntegrationSmoke.test_icthlarins_little_helper_review_flow_resolves_the_canopic_guardian`
  proves authorization consumes the jar and token before the guardian review,
  then a later review advances the ceremony transaction.
- `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_icthlarins_canopic_guardian_selection`
  protects the real offscreen Qt blocker and action surface.
- `tests.test_fetch_assets.TestFetchAssets.test_historical_lookup_requests_newest_revision_before_cutoff`
  protects the reusable historical file-revision query.
- `tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`
  protects all seven assets and their pre-cutoff provenance timestamps.
- The quest Combat debt audit falls from 98 to 97 statless encounters and from
  nine to eight `no_local_source_match` rows.
- Complete closure verification passes all 1,517 core methods with 1,310
  ordinary passes and 207 declared environment skips. Real offscreen Qt
  discovery passes all 1,517 methods without skips or failures. Test-quality,
  documentation, compilation, JSON, diff, quest-stage coverage, asset, and
  worktree-safety gates pass. Item reachability remains at its known 112 root
  and 178 cascade orphan inputs; this quest does not add a new live soft-lock.

## Manual Anki smoke

1. Start Icthlarin's Little Helper with a Kitten, Tinderbox, and Waterskin (4)
   in the carried pack.
2. Answer one eligible review and confirm a canopic jar appears with its icon;
   answer the next and confirm Sphinx's token appears.
3. Answer stage 3 and confirm the jar and token are consumed before Combat.
4. At stage 4, confirm the Quests tab shows one level-81 Canopic guardian, not
   four simultaneous enemies, and defeat it without carrying ceremony
   supplies. Confirm the restored jar returns afterward.
5. Carry 30 coins, one Willow logs item, one Bucket, one Knife, and either Pile
   of salt or Bag of salt. Answer another review and confirm the jar is
   returned, sap collection is named in the action, and the quest holy symbol
   is produced.
6. Transform the holy symbol, then answer the separate hiding review and
   confirm the unholy symbol leaves the pack before Combat.
7. Defeat the level-126 Possessed Priest, finish the quest, and confirm one
   Catspeak amulet plus exactly 4,500 Thieving, 4,000 Agility, and 4,000
   Woodcutting XP.
