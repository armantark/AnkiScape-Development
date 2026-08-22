# Diamond in the Rough playable quest audit — 2026-07-17

## Scope

Backend: replaced four generated objective placeholders and one mis-grouped
statless encounter row with a playable four-stage completion chain. The
override models the Heavy weight, six-enemy sundial ambush, Sundial gnomon,
quicksand/Kalphite nursery recovery, three retained gems, ordered Apep/Heru
finale, Prince Ali rescue, and exact ordinary completion rewards.

Frontend: no new widget contract was needed. The existing Quests tab exposes
the two ordered Combat blocks through the normal action surface and renders
the period quest-item icons from the canonical registry.

Assets: `Heavy weight` and `Sundial gnomon` use original pre-cutoff RuneScape
Wiki file revisions, normalized to the 48-pixel quest-item contract and
recorded in `assets_provenance.json`.

Balance: the ordinary completion awards one quest point; 250 Agility,
Constitution, and Thieving XP; one 250-XP Combat lamp; and the sapphire,
emerald, and ruby necessarily recovered while finding the Kharid-ib. The two
optional level-80 hidden rewards are separate postquest claims: mining the
Scabaras tomb fissure grants 20,000 Mining XP, a Scabaras mask, and a Was;
climbing into the Apmeken tomb fissure grants 20,000 Agility XP, an Apmeken
mask, and an Ankh. Neither action is completion XP.

## Historical evidence

- `Diamond in the Rough`, oldid `6563227`, timestamp
  `2012-11-16T05:41:37Z`:
  <https://runescape.wiki/w/Diamond_in_the_Rough?oldid=6563227>. Literal
  wikitext supplies the ordered story, item custody, bandit and bodyguard
  fights, retained gems, ordinary rewards, and the two optional 20,000-XP
  level-80 fissure rewards.
- `Apmeken mask`, oldid `6474568`, timestamp `2012-10-26T04:06:22Z`,
  and `Ankh`, oldid `6540894`, timestamp `2012-11-07T08:39:12Z`, state that
  the post-Diamond tomb requires boostable level 80 Agility, grants 20,000
  Agility XP on first entry, and contains both items.
- `Scabaras mask`, oldid `6320571`, timestamp `2012-09-30T04:27:43Z`, and
  `Was`, oldid `6320596`, timestamp `2012-09-30T04:30:36Z`, state that the
  post-Diamond crack requires boostable level 80 Mining and contains both
  items. The quest page supplies the base 20,000 Mining XP value.
- `Diamond in the Rough/Quick guide`, oldid `6319548`, timestamp
  `2012-09-29T16:36:16Z`:
  <https://runescape.wiki/w/Diamond_in_the_Rough%2FQuick_guide?oldid=6319548>.
  Literal wikitext corroborates six level-2 bandit-side opponents, two level-5
  bodyguards, gnomon custody, the sparkling Dung-kalphite gem sequence, and
  finale order.
- `Bandit (Diamond in the Rough)`, oldid `6343462`, timestamp
  `2012-10-04T11:45:04Z`: level 2, 200 LP, melee, and guaranteed Bones.
- `Bandit king`, oldid `6538856`, timestamp `2012-11-06T12:44:27Z`: level 3,
  300 LP, melee, and guaranteed Bones.
- `Apep`, oldid `6488383`, timestamp `2012-10-28T14:47:43Z`: level 5,
  Whirling Dervish knockback, and his position before Heru.
- `Heru`, oldid `6471439`, timestamp `2012-10-25T18:38:49Z`: level 5, delayed
  engagement until Apep falls, and blinding-shield interruption.
- `Dung kalphite`, oldid `6535734`, timestamp `2012-11-05T06:16:20Z`:
  confirms the Slice-open interaction and sparkling rare-loot tell.
- `Heavy weight`, oldid `6320315`, timestamp `2012-09-30T02:11:48Z`, and
  `Sundial gnomon`, oldid `6360192`, timestamp `2012-10-06T22:40:37Z`:
  both are nontradeable, nonstackable quest items.
- OpenRS2 rev 742, dated `2012-11-07`, SHA-256
  `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`:
  item 25116 is `Heavy weight` with `Destroy`; item 25118 is `Sundial
  gnomon` with `Destroy`. Attackable NPCs are Bandit king 15823, five Bandits
  15824–15828, Apep 15829, and Heru 15830/15831. Object 75775 is `Crack`
  with `Mine`; object 75776 is `Fissure` with `Climb into`; items 25122–25125
  are Apmeken mask, Ankh, Scabaras mask, and Was. The same six definitions
  exist in revs 736 and 741 and are absent from pre-release rev 727.
- Darkan checkout `3b47cfdfae8b95d543edc2c360aaad5086047804`,
  `developer-information/itemList.txt`: rows 25122–25125 preserve the four
  hidden-reward item identities. A repository search found no Diamond hidden-
  reward handler or XP/level implementation; Darkan supplies identity, not the
  action values.
- Darkan checkout `22d27c71c3eaa81449eeb2f5afeb7eee5352e9ba`,
  `developer-information/beasts.txt`: row 4952 supplies Bandit king
  Attack/Defence/Magic/Ranged 5; rows 4953–4957 supply the same four stats for
  the five Bandits; row 4958 supplies Apep's 500 LP, Attack 5, Defence 5,
  Magic 1, and Ranged 1. The exported Heru row 4949 has no resolver stats.
- RuneScape Wiki file history supplies the original `Heavy weight.png`
  revision from `2012-09-30T02:11:29Z` (file-history SHA-1
  `92bc9d17ffb60d0f42c99c6e134ee357c0a62a07`) and `Sundial gnomon.png`
  from `2012-09-29T00:17:11Z`
  (`e6347df56507a21194cf0296483c9ed2b795c294`). Later 2016 uploads have
  different hashes and are not used.

## Implemented model

1. Accept Osman's mission, collect the Heavy weight containing the Kharid-ib,
   and leave Al Kharid with Ozan.
2. Receive Shantay's four waterskins, align Het's sundial, defeat five Bandits
   plus the Bandit king, and recover the Sundial gnomon.
3. Consume both quest items at their source boundary, resolve the quicksand
   and cavern sequence, and recover one sapphire, emerald, ruby, and the
   transient Kharid-ib.
4. Defeat Apep before Heru, rescue Prince Ali, and return to Osman.
5. Enter the existing completion sentinel and award only the ordinary
   completion rewards.
6. After completion and at Mining 80, expose a one-time Scabaras tomb claim
   that grants 20,000 Mining XP, a Scabaras mask, and a Was.
7. After completion and at Agility 80, expose a one-time Apmeken tomb claim
   that grants 20,000 Agility XP, an Apmeken mask, and an Ankh.

Rooftop travel, sundial interfaces, quicksand dialogue, tunnel loops, dung
slicing, Kharid-ib cutscene custody, and the two bodyguard telegraphs are named
`auto_actions`. Each line preserves what happens without introducing map state,
an inventory puzzle, a camera-facing minigame, or wall-clock delay.

## Explicit abstractions and conflicts

- The quick guide's six level-2 bandits are reconciled against the rev-742
  attackable set as five ordinary Bandits plus their level-3 Bandit king: six
  opponents in the ambush, then two level-5 bodyguards in the finale.
- The period Wiki states 200 LP for a Bandit and 300 LP for the king; Darkan's
  exported rows instead say 100 and 200. The direct cutoff pages win for LP,
  while Darkan supplies the four available resolver stats.
- Darkan omits Strength for Bandits, the king, and Apep. Strength 1 is the
  smallest positive AnkiScape resolver adapter and is not claimed as a period
  stat.
- Heru's period page and rev-742 cache prove level, order, identity, and
  shield behavior, but no local source supplies his resolver stats. The
  implementation explicitly mirrors equal-level companion Apep at 500 LP with
  the same available low stat shape, plus the minimum Strength adapter. This is
  a bounded AnkiScape completion adapter, not historical stat parity.
- Whirling Dervish and the blinding shield are represented by one named line
  in the finale. No unsupported damage, stun duration, facing system, or extra
  RNG is invented.
- The generated catalog incorrectly auto-awarded 20,000 Mining XP and an
  additional 20,000 Agility XP. Both are now one-time postquest claims gated at
  level 80 rather than completion rewards.
- The period text permits temporary boosts, and the Mining action names outfit,
  pendant, and amulet XP modifiers. AnkiScape has no non-combat temporary-level
  state or those XP-modifier systems; the claims implement the source-ready
  level-80 and base-20,000-XP contract without inventing either subsystem.
- Each tomb's two item pickups are folded into its one-time claim because
  AnkiScape does not model tomb map state or separate floor-item interactions.
- Common Bandit/Dung-kalphite incidental drop probabilities are not stated in
  exact period evidence and are not invented inside the quest resolver.

## Verification mapping

- `tests.test_quest_catalog.TestQuestCatalog.test_diamond_in_the_rough_is_a_playable_source_backed_dependency`
  protects stage ordering, quantities, item flow, corrected rewards, and item
  IDs.
- `tests.test_logic.TestLogic.test_diamond_in_the_rough_stage_chain_resolves_two_fights_and_exact_rewards`
  runs the complete pure chain, proves both claims stay optional at completion,
  proves the level-79/80 boundary, and claims both exact XP-and-item payouts.
- `tests.test_integration_smoke.TestIntegrationSmoke.test_diamond_in_the_rough_review_flow_resolves_the_sundial_ambush`
  proves six Combat reviews followed by one quest review produce the gnomon
  and four waterskins through live add-on dispatch.
- `tests.test_main_menu_widget.MainMenuWidgetTest.test_quests_tab_allows_diamond_in_the_rough_ambush_selection`
  protects the real offscreen Qt blockers and action.
- `tests.test_skill_and_item_registry.TestSkillAndItemRegistry.test_quest_stage_items_resolve_icons`
  protects both period assets and their pre-cutoff provenance timestamps.
- The quest Combat debt audit falls from 102 to 98 statless encounters.

## Manual Anki smoke

1. Complete Stolen Hearts in a test save and start Diamond in the Rough.
2. After the first quest review, confirm a Heavy weight appears with its icon.
3. At stage 2, confirm the Quests tab lists five level-2 Bandits and one
   level-3 Bandit king.
4. Answer six eligible reviews and confirm the quest remains on stage 2 until
   every enemy is defeated.
5. Answer one more review and confirm one Sundial gnomon plus four Waterskin
   (4) items are present.
6. Continue through the cavern and confirm the two quest items are consumed,
   while one sapphire, emerald, and ruby remain.
7. Defeat Apep then Heru, complete the quest, and confirm only 250 Agility,
   Constitution, and Thieving XP are granted directly; the Combat lamp remains
   a separate claim and no 20,000-XP hidden reward is auto-awarded.
8. At Mining 79 and Agility 79, confirm neither tomb claim is shown in Bank
   Claims. Raise each skill to 80 and confirm both claims appear.
9. Claim the Scabaras row and confirm 20,000 Mining XP, one Scabaras mask, and
   one Was. Claim the Apmeken row and confirm 20,000 Agility XP, one Apmeken
   mask, and one Ankh.
