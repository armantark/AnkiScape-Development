# Placeholder register recovery audit

Date: 2026-08-13. Cutoff: RuneScape immediately before EOC, 2012-11-20.
Starting point: commit `2cfac317254e392f176919c5e168062bbb3a3bda`, with 178 registered rows.
Current register: `memory-bank/placeholder-values.md`, with 172 rows.

## Result

```text
178 original rows
  = 172 current unresolved historical values
  + 2 direct recovery claims
  + 1 derived identity recovery
  + 3 reclassified AnkiScape adaptations
```

Tooling-blocked rows: **0**.

The three retired recovery rows are:

- `goblin_raids.raided_material_tables`: direct recovery of each site's candidate item set. Tip.It's guide, last updated 2012-10-24 and preserved in Wayback capture `20121228205432`, names farm Potato/Marigold/Barley seeds, forest Logs/Oak logs, and mine Clay/Copper/Tin ore. It does **not** state a Raider's per-shout selector, quantity, or relative rate. AnkiScape's deterministic cycle is a modelling choice, not period evidence. The broad original identifier is therefore only partly closed even though its marker and row retired; the sourced membership is exact and the adjacent runtime selection is a disclosed adaptation boundary.
- `dominion_tower.reward_item_ids`: direct recovery of the represented reward identities from rev-727 and rev-742 item definitions, corroborated by Darkan's rev-727 `developer-information/itemList.txt` from commit `c6fbe036b1743f4dd6067ec178332c69c3708856`. Variant families use the first represented live row because AnkiScape does not model colour, charge, dose, marker-stage, or journal-page variants; that representation is not a claim that every historical variant is modelled.
- `dominion_tower.tarn_ghost_npc_id`: rev-727 Dominion struct 2798 directly selects attackable level-69 Mutant tarn `14429`. Its contiguous attackable partner `14430` is the tower ghost identity by pairing and context. Thus the mutant ID is directly attested and the ghost ID is a derived identity recovery, not a second direct assertion. The earlier `6477` was Redeyes; the same-name `5421/5420` pair belongs to the ordinary Lair encounter.

The three rows removed as non-period adaptations are:

- `conquest.simulated_opponent_rating`: AnkiScape has no live matchmaking queue, so the ±100 simulated band is a review simulation choice.
- `goblin_raids.raid_active_reviews`: the fifteen-review window translates a raid lifecycle into AnkiScape's review clock; no period source states a fifteen-review or equivalent solo duration.
- `tears_of_guthix.green_tear_chance`: `0.055` translates movement and fast stream rotation into one hidden review roll; the period game did not store that review probability.

No verified row was already historically resolved in production at the starting commit. The three recovery streams changed zero/incorrect/incomplete production data rather than merely deleting stale markers.

## Priority and method

Rows were assessed by stable identifier, never by ordinal or line number. Player-visible damage, XP, item quantities, reward identities, rates, timers, and drops were checked first because incorrect values there change normal play most directly. Search followed the project evidence order:

1. Darkan, with supplying-commit history checked where it supplied a value.
2. Rev-727 cache and client scripts.
3. Game-main / 2011Scape rev 667.
4. Other dated OpenRS2 caches, especially independent near-cutoff rev 742.
5. Pinned pre-cutoff wiki revisions and dated Wayback captures.

Cache evidence was used for client-shipped identities, names, params, options, interfaces, enums, and structs. It was not promoted into server rolls, XP formulas, drop rates, timers, selectors, or reward equations. Negative probes required a positive control, multiplicity checks, and an explicit statement of the fields the tool actually renders.

## Structural taxonomy

This high-level value-kind classification covers all 178 original stable identifiers:

```text
Activity simulation                    102
Quest/catalog/combat metadata           41
Skill/resource mechanics                29
Combat/loot mechanics                    6
Total                                  178
```

The categories describe the function of the missing value, not the family that owns it. Activity simulation dominates because broad minigame implementations need server selectors, cadence, reward equations, rosters, and state transitions that client caches rarely contain.

## Reproducible disposition map

The original register is reproducible from:

```bash
git show 2cfac317:memory-bank/placeholder-values.md
```

Its SHA-256 is `e5ee5241bac251d41da647b88d75f98426959ee2d8d503c5f69c6036ecada217`.

Disposition is defined mechanically:

- the three recovery identifiers listed above are retired historical claims;
- the three adaptation identifiers listed above are removed non-period rows;
- every other stable identifier in the original file appears in the current 172-row register and remains unresolved.

The current unresolved family partition is:

```text
achievement_diaries     33    dominion_tower          24
conquest                16    temple_trekking         14
dungeoneering            9    mage_training_arena      7
crucible                  6    mobilising_armies        6
cooking                   6    gnome_restaurant         5
managing_miscellania      5    skeletal_horror          4
goblin_raids              4    troll_invasion           4
farming                    3    hunter                    3
woodcutting                3    lair_of_tarn_razorlor     3
dagannoth_kings            3    daily_challenges          2
chaos_elemental            2    crystal_chest             1
mining                     1    thieving                  1
great_orb_project          1    treasure_trails           1
shattered_heart            1    ranging_guild              1
hunt_for_surok             1    brawling_gloves            1
fishing                    1
```

Achievement Diaries has 33 rows: 32 regional lamp floors plus `achievement_diaries.misc_coin_reward`. The earlier source audit's count of 31 omitted `achievement_diaries.lumbridge.beginner.lamp_minimum_level`; this was a recount error, not a source discovery.

## Evidence searched for the unresolved families

The current register records the row-specific evidence and exact evidence that would settle each identifier. This family summary records the completed search breadth without replacing those stable-ID rows.

| Family | Rows | Evidence searched and remaining boundary |
| --- | ---: | --- |
| Achievement Diaries | 33 | Pinned achievement prose; rev-727 interface 917, CS2 and dialogue-term searches. No regional lamp-floor table or coin-award curve appeared. |
| Dominion Tower | 24 | Pinned tower/reward/boss revisions; Darkan tower controller and combat definitions; rev-727/742 NPC, item, struct, interface and script data. Remaining rows are server factor equations, handicap magnitudes, combat blocks/forms, power-ups and reward selectors. |
| Conquest | 16 | Pinned rules and worked rating example; rev-727 squad/command/diplomacy/rating interfaces, scripts and NPC params; map/client searches. Remaining values are battlefield/server setup, command economy, matching, timeout and reward formulas. |
| Temple Trekking | 14 | Pinned activity/event/reward revisions; rev-727 companion thresholds and definitions; Darkan/current restoration history. Remaining values are route selection, follower growth/combat, event resolution and token/reward selectors. |
| Dungeoneering | 9 | Darkan restoration and history; rev-727/742 interfaces, CS2/configs and cache shop data; pinned Dungeoneering rules. Remaining values are server XP/modifier formulas, skill-door failure, replay direction, boss scaling/definitions, sellback and guardian drops. |
| Mage Training Arena | 7 | Pinned room/reward pages, dated player observations and guide fragments; Darkan and client interface/script searches. Remaining values are room throughput, hazards, rune selectors, maze distribution and Alchemy cadence. |
| Crucible | 6 | Launch/cutoff article and talk history; rev-727 interfaces/scripts; Darkan controller history. Remaining values are server rank points, ordinary kill awards, risk/fee curves and target matching. |
| Mobilising Armies | 6 | Pinned scenario, objective, unit, reward and rank descriptions; emulator and cache searches. Sources state targets and qualitative rules, not action rates, combat resolution, reward curve, costs, exploration distribution or review-clock translation. |
| Cooking | 6 | Pinned recipe/item revisions; Darkan Cooking actions and supplying history; game-main rows. Remaining values are hidden burn/success/maturity rolls. For Dwarven stout, Darkan commit `c6fbe036b1743f4dd6067ec178332c69c3708856` uses `random(100) <= 10/75`; core 2.0.5 draws 0–99, making the executable routine 11%/76%, not exact 10%/75. |
| Gnome Restaurant | 5 | Pinned delivery, dish, customer, token and tip pages; emulator searches. Remaining values are cooking endpoints and server request/tip/speed selectors. |
| Managing Miscellania | 5 | Pinned collection tables and stated ranges/totals; emulator and cache searches. Remaining values are hidden item identities, weights and within-range composition. |
| Skeletal Horror | 4 | Rev-727/742 NPC identities plus Darkan definitions and history. All four phase definitions are `nostats`; no authentic core-stat blocks were recovered. |
| Goblin Raids | 4 | Release/cutoff pages and histories; dated Tip.It Wayback guide; rev-741/742 settings/items; Darkan absence. Remaining rows cover Yodri's within-set selector, conflicting intimidation threshold, cower drop chance and Stinkears' max hit. Raider candidate-set membership is recovered; its per-shout deterministic cycle is an adaptation boundary. |
| Troll Invasion | 4 | Pinned wave, job, repair and reward descriptions; emulator/client searches. Exact rosters, pressure/repair values, dynamite trigger and partial-reward semantics remain server-owned. |
| Farming | 3 | Pinned Habitat/crop pages; Darkan Farming disease/regrowth code and history; game-main and cache states. Hidden disease, regrowth and yield values remain unresolved. |
| Hunter | 3 | Pinned creature/tool/setup/output pages; Darkan/game-main Hunter tables. No qualified catch curves were recovered. |
| Woodcutting | 3 | Pinned tree/root pages; Darkan/game-main tree definitions and history. Success, depletion and respawn rolls remain reconstructions. |
| Lair of Tarn Razorlor | 3 | Pinned miniquest/Tarn pages; Darkan Tarn definitions; rev-727/742 NPC identities. The mutant stat block and missing catalog labels remain unresolved. |
| Dagannoth Kings | 3 | Pinned king pages; Darkan combat/drop definitions and history. Prime/Rex speed, respawn interval and Dragon hatchet rate lack independent period qualification. |
| Daily Challenges | 2 | Cutoff challenge pages; rev-741/742 structs, items and decoded interface 1343; talk history. Sources settle equal eligible-skill weighting but not within-skill weights or XP payout. |
| Chaos Elemental | 2 | Cutoff boss/glove pages; Darkan attack and drop tables plus history. Special-attack weights and per-glove drop rate remain emulator reconstructions. |
| Crystal Chest | 1 | Pinned chest and Ring of wealth prose; emulator/cache searches. The improvement magnitude and selector remain server-owned. |
| Mining | 1 | Pinned Living rock remains/Caverns pages; Darkan/game-main Mining rows. Sources conflict on visible range and do not settle success or distribution. |
| Thieving | 1 | Pinned Master Farmer/Fellstalk pages; game-main/Darkan pickpocket tables. The Fellstalk relative weight remains unrecorded. |
| Great Orb Project | 1 | Pinned robe/activity and talk records; client and emulator searches. The robe-piece XP magnitude remains unresolved. |
| Treasure Trails | 1 | Pinned easy-trail length range; Darkan trail code. The 1–5 distribution is unstated, and Darkan's candidate cannot reach five. |
| Shattered Heart | 1 | Pinned strange-rock rules; Darkan/cache searches. No authentic per-action/per-skill rate table was recovered. |
| Ranging Guild | 1 | Pinned competition outcome/XP pages; Darkan and client searches. Hit-quality probabilities remain server-owned. |
| Hunt for Surok | 1 | Pinned miniquest/catalog pages and generated catalog fields. No sourced word-label mapping for the numeric difficulty grade was recovered. |
| Brawling gloves | 1 | Cutoff glove duration and ore estimate; emulator/cache searches. AnkiScape's action count translates wall-clock use and is not an authentic counter. |
| Fishing | 1 | Pinned Cave eel page; game-main rev-667 unbound row and emulator searches. The hidden catch roll remains unqualified. |

## Register-justification defects found

- `dominion_tower.reward_item_ids` falsely said the rev-742 dump had no display-name rows. Direct rev-727 and rev-742 queries recover the represented item IDs.
- `dominion_tower.tarn_ghost_npc_id` treated name/level matching as sufficient and did not distinguish two same-name pairs. Dominion struct membership identifies `14429`; `14430` is derived from the contiguous attackable tower pair.
- `goblin_raids.raided_material_tables` bundled membership with selection/rate. The dated guide closes the candidate sets only. The deterministic Raider cycle remains a modelling choice.
- `cooking.dwarven_stout_mature_chance` cited the wrong supplying commit and read threshold literals as exact percentages. The actual commit is `c6fbe036b1743f4dd6067ec178332c69c3708856`, and `<=` against an exclusive 0–99 draw executes as 11%/76%.
- `dominion_tower.koschei_combat_level` and `dominion_tower.solus_dellagar_combat_level` described client evidence too loosely. Rev-727 explicitly stores zero; zero is an unset client definition, while the live 110/27 values are positive class-minimum balancing proxies needed by the factor formula.
- The OpenRS2 interface audit promoted a one-off reflective experiment into a checked-in reader capability. The experiment proves the fifteen archives are coherent `0x03` period interfaces and unrelated to the audited rows; `OpenRs2InterfaceQuery` still skips them.

The recurring error shape is evidence leakage across adjacent values: a sourced wiki row can make a back-derived XP number look sourced; threshold literals can look like rates; a sourced candidate set can lend credibility to an unsourced selector; and a successful experiment can be mistaken for shipped tool support. Each claim must be checked at the exact field, namespace, and execution boundary it purports to settle.

## Interface completeness and tooling-blocked result

The checked-in `OpenRs2InterfaceQuery` rejects a component whose first byte is not `0xFF`, catches the resulting `if1` label in `find`, prints a skip warning, and continues. It therefore still skips fifteen archives in revisions 736, 741 and 742:

```text
548, 628, 629, 633, 634, 635, 691, 976,
1253, 1311, 1316, 1358, 1360, 1361, 1368
```

A one-off reflective experiment bypassed the guard and invoked the library's package-private decoder. It decoded all 1,376 affected components into coherent period interfaces, including Squeal of Fortune and Avatar Customisation surfaces. None related to Achievement Diary interface 917, Conquest, or Daily Challenges interface 1343. Reproducing that complete search requires either a guard fix or a byte-level parser; neither exists in the repository today.

Therefore the tooling-blocked partition is **zero**, but the reason is the experiment's decoded content, not completeness of the shipped reader. A clean `find` result from the current reader is not a complete negative search. Interface ID 976 also exposed a namespace-collision hazard: equality with an item, NPC, object, enum, or struct integer does not transfer identity across namespaces.

## Verification

The three behavior/data recoveries were tested through production gameplay paths and mutation-proved:

- Removing recovered Goblin farm members made the real raid-spoils test fail, then restoring them made it pass. This proves the candidate membership is load-bearing; it does not authenticate the deterministic selector.
- Changing Mutant tarn `14429` back to `6477` let combat run but made the real encounter identity assertion fail.
- Changing Dreadnip's item ID from `22370` to `0` let the named claim run but made the recovered identity assertion fail.

Item reachability is unchanged by this audit and its behavior/data retirements:

```text
Before: 1,568 actions / 2,509 reachable items / 97 orphan inputs / 100 blocked actions
After:  1,568 actions / 2,509 reachable items / 97 orphan inputs / 100 blocked actions
```

The full lane results recorded before the final documentation correction were:

```text
Plain: Ran 4096 tests in 213.108s — OK (skipped=498)
Qt:    Ran 4096 tests in 562.580s — OK (skipped=3)
```

Fresh full lanes after this document and the final wording corrections are the commit gate and are recorded in the closure commit/report, not backfilled here before they run.
