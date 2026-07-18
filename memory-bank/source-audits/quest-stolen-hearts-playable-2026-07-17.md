# Stolen Hearts playable quest audit — 2026-07-17

## Scope

Backend: replaced the five generated `Complete Stolen Hearts stage N
objective` blockers with a playable five-stage chain. The override models the
Skulls infiltration, Khnum pursuit, three mercenary fights, ransom-note and
history-book custody, rooftop/treasury sequence, Het scales, Kharid-ib, and
Osman handoff. It also corrects the generated rewards and registers the two
persistent temporary quest items.

Frontend: no new quest widget contract was required. The existing Quests tab
now exposes the resolver-ready mercenary stage through its normal battle
blockers and enabled quest action.

Assets: `Ransom note` and `History of the Kharid-ib` use the named RuneScape
Wiki files from their original pre-cutoff uploads, normalized to the existing
48-pixel quest-item contract and recorded in `assets_provenance.json`.

Balance: Stolen Hearts has no skill or prerequisite-quest start gate. The
cutoff rewards are three quest points, 2,500 coins, direct 250 Constitution XP,
and one 250-XP lamp each for Combat, Agility, and Thieving.

## Historical evidence

- `Stolen Hearts`, oldid `6579723`, timestamp
  `2012-11-19T02:43:30Z`:
  <https://runescape.wiki/w/Stolen_Hearts?oldid=6579723>. Literal wikitext
  supplies the Skulls/Khnum sequence, Lady Keli confrontation, Mercenary Joe
  and two Skulls mercenaries, ransom note, Al Kharid rooftop route, treasury
  history book, Het scales, Kharid-ib handoff, and exact reward family.
- `Stolen Hearts/Quick guide`, oldid `6315136`, timestamp
  `2012-09-28T18:42:52Z`:
  <https://runescape.wiki/w/Stolen_Hearts%2FQuick_guide?oldid=6315136>.
  Literal wikitext corroborates the ordered interaction and item-custody
  checkpoints used to flatten the route into review-native stages.
- OpenRS2 rev 742, dated `2012-11-07`, SHA-256
  `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`:
  item 25127 is `Ransom note` with `Read`/`Destroy`; item 25128 is `History
  of the Kharid-ib` with `Read`/`Destroy`; items 25117 and 25130 are
  `Kharid-ib` with `Destroy`. The cache establishes client identity and
  options, not server quest behavior.
- RuneScape Wiki file history supplies the original `Ransom note.png` upload
  from `2012-09-30T01:20:33Z` (file-history SHA-1
  `d6424184152685fd3d24d98a0b8bbfd81e83fcd1`) and the original
  `History of the Kharid-ib.png` upload from `2012-09-26T17:23:30Z`
  (`c8bfeaf310e6c7edaaf6ade281c12082b3c0905e`). The later 2016 uploads have
  different hashes and are deliberately not used.
- Darkan checkout `22d27c71c3eaa81449eeb2f5afeb7eee5352e9ba`,
  `developer-information/itemList.txt`: rows 28221–28224 corroborate the
  cutoff item IDs.
- The same checkout, `developer-information/beasts.txt`: rows 4959–4961
  identify Mercenary Joe as level 2 with 500 LP and Attack/Defence/Magic/Ranged
  1, and both Skulls mercenaries as level 2 with 400 LP and the same stated
  stats. Rev-742 NPC definitions independently corroborate IDs 15897–15899,
  names, level 2, and Attack/Defence/Magic/Ranged 1.

## Implemented model

1. Join the Skulls and earn Khnum's trust.
2. Tail Khnum to Draynor jail and uncover the kidnapping plot.
3. Confront Lady Keli; defeat Mercenary Joe and two Skulls mercenaries; obtain
   the ransom note.
4. Carry the note to Al Kharid, cross the rooftops, enter the treasury, and
   obtain/read the History of the Kharid-ib.
5. Consume the two custody items at the final boundary, solve Het's scales,
   take the Kharid-ib, and identify the player to Osman with Leela's
   passphrase.
6. Enter the existing completion sentinel and award the exact structured
   rewards.

The rooftop traversal, treasury entry, two-weighing puzzle, brief Kharid-ib
custody, and dialogue beats are `auto_actions`. This is the established
AnkiScape flattening: each review records the named source event without
creating a map, movement minigame, inventory puzzle, or wall-clock timer.

## Explicit abstraction and conflict resolution

- Darkan's exported beast rows omit Strength. AnkiScape's melee resolver
  requires a positive Strength value, so both mercenary definitions use
  Strength 1: the smallest possible adapter, matching the four stated level-1
  combat stats. It is an AnkiScape resolver abstraction, not a claimed
  historical Strength value.
- The generated catalog incorrectly emitted `Khnum` as a reward item. Khnum is
  an NPC/title involved in the quest, not an inventory reward; the override
  removes it.
- The generated catalog double-counted the lamp categories as direct XP.
  Direct XP is now Constitution 250 only. The existing three 250-XP structured
  lamps remain the Combat, Agility, and Thieving choices.
- The Kharid-ib is handled inside the final automatic action rather than being
  persisted. Unlike the ransom note and history book, no intervening stage can
  inspect or consume it, so a durable inventory row would add state without a
  gameplay consequence.

No source-backed Stolen Hearts mechanic remains blocked by this slice. Diamond
in the Rough and the other Smoking Kills prerequisites remain separate quest
definitions.

## Verification mapping

- `tests.test_quest_catalog.TestQuestCatalog.test_stolen_hearts_is_a_playable_source_backed_dependency`
  protects rewards, stage ordering, combat quantities, item flow, IDs, and the
  absence of generated placeholder actions.
- `tests.test_logic.TestLogic.test_stolen_hearts_stage_chain_resolves_combat_items_and_exact_rewards`
  runs the complete pure stage/combat/reward chain.
- `tests.test_integration_smoke.TestIntegrationSmoke.test_stolen_hearts_review_flow_resolves_the_real_mercenary_stage`
  proves three Combat reviews followed by the quest review produce the ransom
  note through the live add-on dispatch.
- `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_stolen_hearts_mercenary_stage_selection`
  proves the real offscreen Qt surface shows both blockers, enables the action,
  and contains no placeholder objective.
- `tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`
  protects both quest-item assets through the canonical registry.
- `tests.test_quest_combat_stat_gap_audit.TestQuestCombatStatGapAudit.test_gap_classification_summary_matches_current_catalog_debt`
  records the debt reduction from 103 to 102 statless encounters.

## Manual Anki smoke

1. Start Anki with only the canonical AnkiScape checkout enabled.
2. In a test save, start Stolen Hearts and set its progress to stage 3 with
   quest Combat enabled and suitable Combat stats.
3. Open Quests and confirm the stage lists Mercenary Joe plus two Skulls
   mercenaries and contains no `Complete Stolen Hearts stage` text.
4. Answer three eligible quest reviews and confirm the three enemies resolve in
   order without advancing the quest.
5. Answer one more eligible review and confirm progress advances and a Ransom
   note appears with its icon.
6. Continue through completion and confirm the two temporary items are gone,
   2,500 coins and 250 Constitution XP are awarded, and three 250-XP claims are
   available for Combat, Agility, and Thieving.
