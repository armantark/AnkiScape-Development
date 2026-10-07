# Quest-fight placeholder source decisions, 2026-10-02

2026-10-07: Root copied the accepted source and tests from `52748d16cb5e0ff581b31a70e538deb03eccf07e` onto `20b73e984c5d1b83ebbc1703f2bb1afa76e8678f`. Its base includes landed carried integration `7c7651e993236127c73ceae8cd98eab2e1dd4e92`. All four product files retain the accepted Git blobs. The historical full gate remains source proof. The new candidate needs native acceptance and its own full gate before landing.

Scope: the 85 source-blocked rows in `tools/combat/quest_stat_sources.json` at `60d7bd83`. Cutoff: before `2012-11-20`. Five rows are admitted; the other 80 retain their source blocks, including research row 14, Juvinate, which the source review returned to `source_blocked`. The period record supplies displayed level and, where listed below, LP, style and maximum hit. The retained Darkan values are registered placeholders, not independently verified period combat stats.

No admitted row carries a `payload` in the registry. `tools/combat/quest_stat_sources.py:26` hands any `payload` it finds to `tools/build_pre_eoc_quest_catalog.py:1963`, which writes those stats into the generated catalog with no marker, so a payload on a placeholder row would become an unmarked reconstruction at the next regeneration. Read against the current `generated/quest_catalog_generated.py`, none of the five admitted encounter rows carries `npc_stats` there, so inside this repository the marked replacement in `data/quest/combat_replacements.py` is the only tracked file that holds these values. That is a statement about this repository, not about every copy of the underlying Darkan numbers.

The cited Darkan combatdef files are keyed by NPC name. Each one establishes only the combat payload recorded under that name at commit `df98a8d17c625de69e36a2bd1a7974829f0aa068`. No retained cache output ties any admitted row to an NPC id, so this record makes no NPC-id claim except for Solus Dellagar, where Darkan `WantedState.kt:15` declares `WantedIds.SOLUS_ATTACK = 2780` and `Wanted.kt:284-294` spawns that id for the player's Solus fight.

Research receipts:

- [/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-02/statsrc1-evidence/results.json](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-02/statsrc1-evidence/results.json>) and its adjacent `report.md`.
- [/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-02/statsrc2-evidence/results.json](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/.orchestrator/tasks-2026-10-02/statsrc2-evidence/results.json>) and its adjacent `report.md`.

The complete row decisions and original evidence are retained in [/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-fight-placeholders-2026-10-02/reconciliation.json](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-fight-placeholders-2026-10-02/reconciliation.json>). Darkan product definitions were read at `df98a8d17c625de69e36a2bd1a7974829f0aa068`. Neither this record nor the registry retains exact rev-742 cache output for an admitted row, unlike the `sourced` rows, which carry a `cache` block; no NPC identity is claimed from that cache here, and in no case does it supply hidden levels. Different-era or different-variant bestiary candidates excluded by the research do not override an exact definition. An explicit recorded stat conflict stays blocked.

## Admitted rows

### underground_pass, stage 6: Othanian

Displayed level `91`. Encounter ID, stage, quantity and quest restrictions remain intact. Qualified literal values: `{"level": "91", "hitpoints": "900", "attack_style": "melee", "max_hit": "93"}`.

[https://runescape.wiki/w/Othainian?oldid=6110941](https://runescape.wiki/w/Othainian?oldid=6110941), revision UTC `2012-08-19T02:29:27Z`:
> |level = 91
> |attack style = melee
> |max hit = 93
> |LP = 900

[https://runescape.wiki/w/Othainian?oldid=5373309](https://runescape.wiki/w/Othainian?oldid=5373309), revision UTC `2012-03-13T11:20:40Z`:
> |level = 91
> |attack style = melee
> |max hit = 93
> |LP = 900

Placeholder source: [/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/othainian (noanims).json](</Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/othainian (noanims).json>), name key `Othainian`. Retained fields: `attack=76`, `strength=78`, `defence=77`, `magic=1`, `ranged=1`. Each field has its own `quests.<quest>.<encounter>.<field>` marker and register row.

### recruitment_drive, stage 4: Sir Leye

Displayed level `20`. Encounter ID, stage, quantity and quest restrictions remain intact. Qualified literal values: `{"level": "20", "hitpoints": "210", "attack_style": "Melee", "max_hit": "20 (approx)"}`.

[https://runescape.wiki/w/Sir_Leye?oldid=6430968](https://runescape.wiki/w/Sir_Leye?oldid=6430968), revision UTC `2012-10-17T00:42:51Z`:
> |level = 20
> |LP = 210
> |attack style = Melee
> |max hit = 20 (approx)

[https://runescape.wiki/w/Sir_Leye?oldid=5380553](https://runescape.wiki/w/Sir_Leye?oldid=5380553), revision UTC `2012-03-14T09:13:05Z`:
> |level = 20
> |LP = 210
> |attack style = Melee
> |max hit = 20 (approx)

Placeholder source: [/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/sir_leye (nostats) (noanims).json](</Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/sir_leye (nostats) (noanims).json>), name key `Sir Leye`. Retained fields: `attack=0`, `strength=0`, `defence=0`, `magic=0`, `ranged=0`. Each field has its own `quests.<quest>.<encounter>.<field>` marker and register row.

### the_fremennik_isles, stage 5: Ice troll

Displayed level `82`. Encounter ID, stage, quantity and quest restrictions remain intact. Qualified literal values: `{"hitpoints": "800", "attack_style": "Melee", "max_hit": "177", "client_combat_level": "82", "level": "82"}`.

The generic Ice troll article is a different variant and supplies nothing here. Its retained receipt, [https://runescape.wiki/w/Ice_troll?oldid=6288823](https://runescape.wiki/w/Ice_troll?oldid=6288823), revision UTC `2012-09-24T06:18:16Z`, states:
> |level = 120 to 124
> |LP = 1000
> |max hit = 250 (approx)

That page carries no level-82 row, and Darkan holds only level `120`, `121`, `123` and `124` Ice troll definitions. This fight is the level-82 Ice troll male.

[https://runescape.wiki/w/Ice_troll_male?oldid=6288801](https://runescape.wiki/w/Ice_troll_male?oldid=6288801), revision UTC `2012-09-24T06:07:25Z`:
> |level = 82
> |LP = 800
> |attack style = Melee
> |max hit = 177

[https://runescape.wiki/w/Ice_troll_male?oldid=5669851](https://runescape.wiki/w/Ice_troll_male?oldid=5669851), revision UTC `2012-05-28T15:34:11Z`:
> |level = 82
> |LP = 800
> |attack style = Melee
> |max hit = 177

Placeholder source: [/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/ice_troll_male (noanims).json](</Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/ice_troll_male (noanims).json>), name key `Ice troll male`. Retained fields: `attack=80`, `strength=80`, `defence=40`, `magic=1`, `ranged=1`. Each field has its own `quests.<quest>.<encounter>.<field>` marker and register row.

### dream_mentor, stage 4: The Illusive

Displayed level `108`. Encounter ID, stage, quantity and quest restrictions remain intact. Qualified literal values: `{"hitpoints": "1400", "attack_style": "Melee", "max_hit": "85", "level": "108"}`.

[https://runescape.wiki/w/The_Illusive?oldid=5908075](https://runescape.wiki/w/The_Illusive?oldid=5908075), revision UTC `2012-07-08T12:25:23Z`:
> |level = 108
> |LP = 1400
> |attack style = Melee
> |max hit = 85

[https://runescape.wiki/w/The_Illusive?oldid=5668876](https://runescape.wiki/w/The_Illusive?oldid=5668876), revision UTC `2012-05-28T02:15:35Z`:
> |level = 108
> |LP = 1400
> |attack style = Melee
> |max hit = 85

Placeholder source: [/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/the_illusive (nostats) (noanims).json](</Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/the_illusive (nostats) (noanims).json>), name key `The Illusive`. Retained fields: `attack=0`, `strength=0`, `defence=0`, `magic=0`, `ranged=0`. Each field has its own `quests.<quest>.<encounter>.<field>` marker and register row.

### wanted, stage 5: Solus Dellagar

The fight has no displayed combat level; the catalog keeps `level=0` and the saved encounter ID `wanted_solus_dellagar_2`. Darkan `WantedState.kt:15` declares `WantedIds.SOLUS_ATTACK = 2780` and `Wanted.kt:284-294` spawns that id for the player's Solus fight. Those two lines together are the only NPC-id claim in this record that rests on retained evidence; line 15 alone declares a constant and binds it to no fight. Qualified literal values: `{"level": "no specific combat level", "hitpoints": "540", "attack_style": "only uses melee due to being weakened", "max_hit": "40 for the battle against players"}`.

[https://runescape.wiki/w/Wanted%21?oldid=6510622](https://runescape.wiki/w/Wanted%21?oldid=6510622), revision UTC `2012-10-31T12:24:35Z`:
> is fairly easy, with no specific combat level, 540 life points, and only uses melee due to being weakened. Once he is

The Wanted! passage ends the rangers’ cutscene and tells the player to finish off the weakened Solus. The catalog’s stage 5 encounter `wanted_solus_dellagar_2` uses this quest source. `Wanted.kt:284-294` (`startSolusFight`) spawns NPC `2780` with `hitpoints = 540` at `Wanted.kt:289` and the player as combat target, which corroborates the quest page's 540 life points from a second retained source. Darkan's own stage constants are not this catalog's stage numbers: `Wanted.kt` gates that spawn on the Darkan constant `FINAL_CLUE` and then sets `SOLUS_FIGHT`. The generic infobox’s 400 LP and mixed styles do not replace the quest-specific 540 LP and weakened melee.

[https://runescape.wiki/w/Solus_Dellagar?oldid=5587768](https://runescape.wiki/w/Solus_Dellagar?oldid=5587768), revision UTC `2012-05-10T00:31:36Z`, and [https://runescape.wiki/w/Solus_Dellagar?oldid=6342730](https://runescape.wiki/w/Solus_Dellagar?oldid=6342730), revision UTC `2012-10-03T22:11:11Z`, both state:
> |max hit = 960 (approx) (40 for the battle against players)

Both articles distinguish the 960-LP spell from the final battle in their body text. Revision `6342730` states:
> He was also capable of greatly increasing the damage that is dealt by the [[Flames of Zamorak]] spell, allowing him to deal up to 960 life points in one spell, crippling even the strongest players (This can never kill players, however, and Solus also does not hit anywhere near as high during the final battle).

This is the player battle that stage 5 runs. The qualified maximum hit is therefore `40`; the cutscene maximum `960` is excluded. Maximum hit is not a placeholder, and the registry row no longer registers one: the earlier `quests.wanted.solus_dellagar_2.max_hit` entry of `1` is removed, and both dated revisions are cited in the admission.

Placeholder source: [/Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/solus_dellagar (nostats) (noanims).json](</Users/ArmanTarkhanian1/Documents/CodexWorktrees/darkan-master-integration/data/npcs/combatdefs/uncategorized/solus_dellagar (nostats) (noanims).json>), name key `Solus Dellagar`. Retained fields: `attack=0`, `strength=0`, `defence=0`, `magic=0`, `ranged=0`. Each field has its own register row.

## Historical receipt cache

The fixed audit uses `tools.build_pre_eoc_quest_catalog.slug_key`, which collapses distinct titles to lowercase keys. The seed utility groups receipts with that same function, puts the latest monster-infobox receipt at the bare audit key, and preserves every other title with a lossless UTF-8 hex suffix. Missing pages and redirects cannot overwrite a monster receipt. The audit and its keys are unchanged.

Reproducibility limit. `tools/combat/seed_quest_stat_research_cache.py` is a restore utility, not a fetcher. It reads only the archive directories named on its command line, and `_period_pages` drops three classes of page: a page absent from those archives, a payload that records more than one revision, and a revision timestamped at or after `EOC_CUTOFF_TIMESTAMP`. `_restore_receipts` only writes, so it never removes a stale file it did not write. The two named archives are the `statsrc1-evidence` and `statsrc2-evidence` directories listed under Research receipts above.

A page the archives record as missing is not dropped. `_period_pages` reads an absent revision list as the empty timestamp, which sorts below the cutoff, so the seed does restore negative receipts, and the archives hold API-shaped negative payloads for many `(monster)` titles, among them `statsrc2-evidence/part3-evidence/wiki-single-9.json` for "Armoured zombie (monster)".

Live-fetch-only receipts. The audit writes a live API response verbatim at `tools/audit_quest_historical_wiki_combat_stats.py:258`, which keeps the response's `batchcomplete` key; the seed writes `{"query": {"pages": [page]}}` and never writes that key, so `batchcomplete` marks a live write. The source review of 2026-10-03 counted 293 `*.json` files in the literal cache, 39 with the `--<hex>` suffix and 4 holding `batchcomplete`; those three counts are its measurements and are not re-measured here. The four named files were re-read directly for this repair, and each holds `batchcomplete` with one `"missing": true` page and no revision:

| Literal cache file | Title |
| --- | --- |
| `assassin_monster.json` | `Assassin (monster)` |
| `vanstrom_klause_monster.json` | `Vanstrom Klause (monster)` |
| `lava_monster_monster.json` | `Lava monster (monster)` |
| `lava_monster_elder_kiln_monster.json` | `Lava monster (Elder Kiln) (monster)` |

Those four titles appear in the archives only inside the research records `statsrc1-evidence/input.json`, `statsrc2-evidence/input_rows.json` and `statsrc2-evidence/part3-input.json`, as `{"query": "pre_cutoff", "title": ..., "status": "no_period_revision"}`. There `query` is a string, not the API object `_period_pages` requires, so the seed skips those payloads.

The distinction that matters: the fact that each of those four titles has no pre-cutoff revision is reconstructible from the retained archives, while the exact cache bytes are not reproducible from the seed as written. A clean checkout seeded from the two archives leaves those four cache keys absent, and `fetch_historical_revision` then issues one live request for each. Closing that gap needs either negative receipts written for those four titles or a seed that reads the research records; this slice does neither. `batchcomplete` on its own never proves that the archives lack a title's data, and the four files above are named from the retained bytes without any new seed run or network harvest.

The recorded seed run restored 286 title receipts across 36 collision groups, and the recorded historical audit after it checked 79 gaps. Every number in this paragraph is a historic measurement from the earlier run and is not re-measured here.

Distinct historical runs. The earlier audit before the receipt repair checked 79 gaps and recorded `historical_wiki_metadata_only: 60` and `historical_wiki_no_monster_metadata: 19` in [/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-fight-placeholders-2026-10-02/historical-wiki.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-fight-placeholders-2026-10-02/historical-wiki.log>). The review-resolution run recorded on 2026-10-03, after the seed restored the collision-safe receipts, also checked 79 gaps and recorded `historical_wiki_metadata_only: 64` and `historical_wiki_no_monster_metadata: 15` in [/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-fight-placeholders-2026-10-02/review-historical-wiki.log](</Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.git/ankiscape-promotion-evidence/goal-quest-fight-placeholders-2026-10-02/review-historical-wiki.log>). These are two separate retained command logs, also bound separately in `memory-bank/progress.md`; neither is current execution. The source review repeated the later run's 64 and 15 figures. The Juvinate return to `source_blocked` raises the gap count, so the live counts must come from the next recorded run. Haakon `6288820`, Balance Elemental `6534303`, and Pest Queen `6492869` retain their monster pages. After this repair 25 borrowed combat fields remain registered, each with a marker in `data/quest/combat_replacements.py`, a row in `memory-bank/placeholder-values.md`, and a field entry in the registry.

## Rows kept source-blocked

A definition with no `combatLevels` does not supply hidden levels. No display-level reconstruction or bestiary substitution is made. The Dream transaction remains reserved; Dream Mentor quest encounter data uses the ordinary quest combat path.

### The three retained Juvinate revisions

Research row 14 stays blocked because three distinct retained revisions describe candidate Juvinates and none of them states a level-50 fight. Each one is quoted here from its own retained bytes, and no revision's values may be attached to another.

`Juvinate` oldid `6146624`, the literal receipt `tools/.cache/quest_historical_wiki_combat_stats/literal/juvinate.json` at `revid 6146624`:
> |level = 59 (Route 1),
> 90 (Route 2),
> 119 (Route 3)
> |LP =500 (Level 59),
> 900 (Level 90),
> 1500 (Level 119)
> |max hit =Level 59: 64,
> Level 90: 64,
> Level 119: 90

Its lowest route is level 59, and `64` is that route's maximum hit. The registry `wiki` block for this row records `hitpoints 500` and `max_hit "59"`, which the audit parser took from those multi-route fields; the `59` there is the route label inside `|max hit =Level 59: 64,`, not a maximum hit. The earlier reading of this revision as "500 LP and maximum hit 59 at level 54" was wrong on both the level and the maximum hit, and it is corrected here and in the registry row.

`Vampyre Juvinate` oldid `6097148`, a `{{beta}}` page for a Burgh de Rott Woods monster that the article itself calls "very similar to [[Vampyre juvinate]]s". The retained text `archives/statsrc1-evidence/leaf1/wiki-2012-11-19-6097148.txt` and the literal receipt `literal/vampyre_juvinate--56616d70797265204a7576696e617465.json` at `revid 6097148` agree on these three fields:
> |level = 54
> |LP = 850
> |max hit = 54/63/72/81/90

`Vampyre juvinate` oldid `6552297`, a different and later revision under the lowercase title, the literal receipt `literal/vampyre_juvinate.json` at `revid 6552297`:
> |level = 54 / 112
> |LP = 850 / 1200
> |max hit = 54 / 104

Those last two are the trap this record names once: the two titles collapse to the same slug key, so the bare cache key `vampyre_juvinate.json` holds `6552297` and the hex-suffixed key holds `6097148`. Reading the bare key as the alias revision attaches `6552297`'s `112`, `1200` and `104` to `6097148`, which states none of them. The hex suffix from the receipt repair is what keeps the two apart.

The Darkan level-50 file `vampyre_juvinate_(50) (noanims).json` carries ids `3520` and `3538`, `1100` LP, maximum hit `60`, attack `50`, strength `37` and defence `30`. These revisions are variant and era records for other Juvinates, so none of them establishes that level-50 block, and none of them creates a conflict between two readings of one page. Returning the row to `source_blocked` drops the registry field entries, the marked replacement and the register rows the earlier pass added for this fight. It does not touch the pre-existing generated catalog row, which is recorded under Verification boundary as second level.

| Research row | Quest / stage | Encounter / input level | Reason retained |
| --- | --- | --- | --- |
| 1 | `fight_arena` / 8 | Khazard ogre / 63 | Recorded LP and maximum-hit conflicts. |
| 2 | `fight_arena` / 9 | Khazard scorpion / 44 | Recorded LP conflict. |
| 3 | `underground_pass` / 6 | Sir Harry / 62 | Darkan omits combatLevels; no values to retain. |
| 5 | `monkey_madness` / 8 | Jungle demon / 195 | Rejected accuracy calibration and maximum-hit conflict. |
| 6 | `in_search_of_the_myreque` / 2 | Skeleton Hellhound / 97 | Darkan omits combatLevels; no values to retain. |
| 7 | `one_small_favour` / 6 | Dwarven gang member / 0 | Input-level0 aggregate has three distinct NPC definitions; no unique mapping. |
| 8 | `between_a_rock` / 4 | Arzinian Avatar / 75 | Style/variant selection unresolved; maximum-hit conflict. |
| 10 | `wanted` / 5 | Black Knight / 34 | Requested level34 conflicts with dated level32/33 identities. |
| 12 | `recipe_for_disaster_freeing_sir_amik_varze` / 3 | Evil Chicken (Recipe for Disaster) / 159 | Magic-only period style conflicts with MELEE combatdef and maximum hit. |
| 13 | `recipe_for_disaster_freeing_king_awowogei` / 5 | Zombie Monkey / 82 | Recorded level82 maximum-hit conflict. |
| 14 | `in_aid_of_the_myreque` / 6 | Juvinate / 50 | Returned to `source_blocked` by the source review. Quest revision 6555220 gives only level 50 and the count of four. No retained revision states a level-50 Juvinate fight, so every combat value would be an unverified placeholder. See "The three retained Juvinate revisions" above. |
| 15 | `rag_and_bone_man` / 4 | Goblin / 0 | Recorded LP and same-ID hidden-level conflicts. |
| 16 | `rag_and_bone_man` / 4 | Big frog / 0 | Recorded combatdef/bestiary hidden-level conflict. |
| 17 | `rag_and_bone_man` / 4 | Monkey / 0 | Recorded maximum-hit conflict. |
| 18 | `the_eyes_of_glouphrie` / 4 | Evil creature / 0 | Recorded maximum-hit conflict. |
| 21 | `the_path_of_glouphrie` / 6 | Warped terrorbird / 143 | Darkan omits combatLevels and maximum hit conflicts by variant. |
| 22 | `the_path_of_glouphrie` / 6 | Evil creature / 1 | Recorded maximum-hit and displayed-level mapping conflict. |
| 23 | `back_to_my_roots` / 3 | Wild jade vine / 167 | Darkan omits combatLevels and only supplies one of the qualified mixed styles. |
| 24 | `land_of_the_goblins` / 6 | Snothead / 35 | Darkan omits combatLevels; no values to retain. |
| 25 | `land_of_the_goblins` / 6 | Snailfeet / 45 | Recorded quest-table/monster attack-style conflict. |
| 26 | `land_of_the_goblins` / 6 | Mosschin / 55 | Darkan omits combatLevels; no values to retain. |
| 27 | `land_of_the_goblins` / 6 | Redeyes / 65 | Darkan omits combatLevels; no values to retain. |
| 28 | `land_of_the_goblins` / 6 | Strongbones / 75 | Darkan omits combatLevels; no values to retain. |
| 29 | `dealing_with_scabaras` / 6 | Skeletons / 0 | No exact admissible encounter values; multiple NPC variants. |
| 30 | `legacy_of_seergaze` / 6 | Fistandantilus / 80 | Recorded quest/monster outgoing-style conflict; Darkan omits combatLevels. |
| 31 | `legacy_of_seergaze` / 6 | Zaromark Sliver / 80 | Recorded quest/monster outgoing-style conflict; Darkan omits combatLevels. |
| 32 | `toktz_ket_dill` / 6 | TokTz-Ket-Dill / 100 | Frozen bounded-beta source ceiling and absent combatLevels. |
| 33 | `toktz_ket_dill` / 6 | Fire monster / 47 | Recorded pre-beta/cutoff maximum-hit conflict. |
| 34 | `rocking_out` / 6 | Customs officer (Prison) / 35 | Frozen combat LP/max-hit source boundary and absent combatLevels. |
| 35 | `defender_of_varrock` / 4 | Armoured zombie / 85 | Missing combatLevels and incomplete mixed-style mapping. |
| 36 | `while_guthix_sleeps` / 6 | Assassin (While Guthix Sleeps) / 38 | Recorded LP/attack-style conflicts. |
| 37 | `while_guthix_sleeps` / 6 | Mercenary Mage / 48 | Darkan omits combatLevels; no values to retain. |
| 38 | `while_guthix_sleeps` / 6 | Mercenary axeman / 88 | Darkan omits combatLevels; no values to retain. |
| 39 | `while_guthix_sleeps` / 6 | Elite Black Knight / 138 | Recorded LP and maximum-hit conflicts. |
| 40 | `while_guthix_sleeps` / 6 | Balance Elemental / 454 | Absent combatLevels and incomplete mixed-style mapping. |
| 41 | `the_chosen_commander` / 6 | Goblin statue / 50 | Darkan omits combatLevels; no values to retain. |
| 42 | `the_chosen_commander` / 6 | Ork statue / 63 | Darkan omits combatLevels; no values to retain. |
| 43 | `the_chosen_commander` / 6 | Ogre statue / 75 | Recorded same-level LP conflict; absent combatLevels. |
| 44 | `the_chosen_commander` / 6 | Merchant / 50 | Research recorded conflicts: Period revision has {{beta}}. Its quoted metadata is a partial historical observation, not independent closure of the live pre-EOC variant; hidden levels remain absent.; Darkan h.a.m._agent_walton (nostats) (noanims).json supplies LP 1, maxHit 1 and MELEE; statless/zero-placeholder payload or period mismatch prevents using it to complete this fight.; Current Darkan bestiary same-name candidate displayed levels  do not establish this exact input level 50; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 45 | `the_chosen_commander` / 6 | Zanik / 75 | Research recorded conflicts: Darkan zanik (nostats) (noanims).json supplies LP 1, maxHit 1 and MELEE; statless/zero-placeholder payload or period mismatch prevents using it to complete this fight.; Current Darkan bestiary same-name candidate displayed levels 65 do not establish this exact input level 75; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 46 | `the_chosen_commander` / 6 | Bandos avatar / 125 | Research recorded conflicts: Period revision has {{beta}}. Its quoted metadata is a partial historical observation, not independent closure of the live pre-EOC variant; hidden levels remain absent.; Current Darkan bestiary same-name candidate displayed levels 77 do not establish this exact input level 125; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 47 | `glorious_memories` / 4 | Nial Swiftfling / 156 | Research recorded conflicts: Period revision has {{beta}}. Its quoted metadata is a partial historical observation, not independent closure of the live pre-EOC variant; hidden levels remain absent.; Current Darkan bestiary same-name candidate displayed levels 81 do not establish this exact input level 156; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 48 | `missing_my_mummy` / 4 | Skeleton looter / 41 | Research recorded conflicts: Period revision has {{beta}}. Its quoted metadata is a partial historical observation, not independent closure of the live pre-EOC variant; hidden levels remain absent.; Darkan skeleton_looter (nostats) (noanims).json supplies LP 1, maxHit 1 and MELEE; statless/zero-placeholder payload or period mismatch prevents using it to complete this fight.; Current Darkan bestiary same-name candidate displayed levels 42 do not establish this exact input level 41; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 49 | `missing_my_mummy` / 4 | Golem Guard / 47 | Research recorded conflicts: Period revision has {{beta}}. Its quoted metadata is a partial historical observation, not independent closure of the live pre-EOC variant; hidden levels remain absent.; Current Darkan bestiary same-name candidate displayed levels 37 do not establish this exact input level 47; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 50 | `missing_my_mummy` / 4 | Tumeken's shadow / 41 | Research recorded conflicts: Period revision has {{beta}}. Its quoted metadata is a partial historical observation, not independent closure of the live pre-EOC variant; hidden levels remain absent.; Current Darkan bestiary same-name candidate displayed levels 42 do not establish this exact input level 41; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 51 | `the_curse_of_arrav` / 4 | Arrav / 180 | Research recorded conflicts: Darkan arrav_(180) (nostats) (noanims).json supplies LP 1, maxHit 1 and MELEE; statless/zero-placeholder payload or period mismatch prevents using it to complete this fight.; Current Darkan bestiary same-name candidate displayed levels 1 do not establish this exact input level 180; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 52 | `fur_n_seek` / 3 | Fenris wolf / 64 | Research recorded conflicts: Period revision has {{beta}}. Its quoted metadata is a partial historical observation, not independent closure of the live pre-EOC variant; hidden levels remain absent.; Current Darkan bestiary same-name candidate displayed levels 49 do not establish this exact input level 64; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 53 | `blood_runs_deep` / 6 | Dagannoth Sentinel / 193 | Research recorded conflicts: Period revision has {{beta}}. Its quoted metadata is a partial historical observation, not independent closure of the live pre-EOC variant; hidden levels remain absent.; Darkan dagannoth_sentinel (nostats) (noanims).json supplies LP 2, maxHit 150 and MELEE; statless/zero-placeholder payload or period mismatch prevents using it to complete this fight.; Current Darkan bestiary same-name candidate displayed levels 98 do not establish this exact input level 193; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 54 | `nomads_requiem` / 4 | Decaying avatar / 525 | Research recorded conflicts: Period revision has {{beta}}. Its quoted metadata is a partial historical observation, not independent closure of the live pre-EOC variant; hidden levels remain absent.; Darkan decaying_avatar (nostats) (noanims).json supplies LP 10, maxHit 460 and MELEE; statless/zero-placeholder payload or period mismatch prevents using it to complete this fight.; Current Darkan bestiary same-name candidate displayed levels 98 do not establish this exact input level 525; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 55 | `the_blood_pact` / 2 | Kayle / 3 | Research recorded conflicts: Period revision has {{beta}}. Its quoted metadata is a partial historical observation, not independent closure of the live pre-EOC variant; hidden levels remain absent.; Darkan kayle (nostats) (noanims).json supplies LP 1, maxHit 1 and MELEE; statless/zero-placeholder payload or period mismatch prevents using it to complete this fight.; Current Darkan bestiary same-name candidate displayed levels 1 do not establish this exact input level 3; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 56 | `the_blood_pact` / 2 | Reese / 3 | Research recorded conflicts: Period revision has {{beta}}. Its quoted metadata is a partial historical observation, not independent closure of the live pre-EOC variant; hidden levels remain absent.; Current Darkan bestiary same-name candidate displayed levels 1 do not establish this exact input level 3; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength.; Current bestiary Reese is level1, LP750, includes EOC abilities, and attack/defence1 with no strength. The existing owner-reviewed reason is preserved; no strength1 is manufactured. |
| 57 | `a_fairy_tale_iii_battle_at_orks_rift` / 4 | Ork warrior / 56 | Research recorded conflicts: Historical monster oldid6264757 states level 54, not the quest level 56. Its LP 1100, Melee and max hit 44 are candidate metadata only, excluded from values_found for this variant.; Darkan ork_warrior (nostats) (noanims).json supplies LP 1, maxHit 1 and MELEE; statless/zero-placeholder payload or period mismatch prevents using it to complete this fight.; Current Darkan bestiary same-name candidate displayed levels 79 do not establish this exact input level 56; candidate hidden numbers are excluded. The file is not an independent implementation and lacks strength. |
| 58 | `a_fairy_tale_iii_battle_at_orks_rift` / 4 | General Gromblod / 150 | Research recorded conflicts: The visible metadata citation carries {{beta}}; the checked earlier unmarked revisions do not independently provide this full monster block. This remains partial evidence.; Darkan matching combatdef is a 1-LP/1-maxHit stub; absent or zero combat levels are not evidence values. |
| 59 | `a_fairy_tale_iii_battle_at_orks_rift` / 4 | Fairy Godfather / 138 | Research recorded conflicts: The visible metadata citation carries {{beta}}; the checked earlier unmarked revisions do not independently provide this full monster block. This remains partial evidence.; Darkan matching combatdef is a 1-LP/1-maxHit stub; absent or zero combat levels are not evidence values. |
| 60 | `quiet_before_the_swarm` / 4 | Torcher / 45 | Research recorded conflicts: Period generic Torcher page lists levels 33,49,67,79,91,92; none is quest level45. Darkan supplied variants are not transferable. The generic species magic style is a candidate only. |
| 61 | `love_story` / 5 | Zenevivia / 246 | Research recorded conflicts: Darkan matching combatdef is a 1-LP/1-maxHit stub; absent or zero combat levels are not evidence values. |
| 62 | `love_story` / 5 | Pit iron dragon / 204 | Research recorded conflicts: Period LP1550 versus Darkan1650; period max hit250(Melee)/550(Dragonfire) versus Darkan203 and RANGE. General MetalDragonCombat has different max-hit/dragonfire behavior and no missing hidden levels. |
| 63 | `love_story` / 5 | Pit rock protector / 120 | Research recorded conflicts: Period LP1500 versus Darkan2000; Darkan maxHit120 has no period corroboration in the checked page history. |
| 64 | `love_story` / 5 | Pit ogre / 62 | Darkan omits combatLevels; no hidden values to retain. |
| 65 | `love_story` / 5 | Pit dog / 52 | Darkan omits combatLevels; no hidden values to retain. |
| 66 | `a_void_dance` / 4 | Black Knight guardian / 110 | Research recorded conflicts: Historical visible metadata differs between 6010042 and unmarked 5624501: {'displayed_level': '110', 'life_points': '750', 'attack_style': 'Melee', 'max_hit': '370'}; Cutoff wiki distinguishes ordinary114 and special370; the pre-beta page/Darkan370 does not establish an ordinary370 max hit. |
| 67 | `gunnars_ground` / 2 | Haakon the Champion / 0 | Research recorded conflicts: Hidden attack/strength conflict: Darkan23/23 versus independent game-main22/22. Defence25 agrees between explicit combatdefs but Darkan bestiary says23. Historical wiki does not settle the hidden stats; no override of recorded source_stats_conflict or quest level alias. |
| 68 | `the_void_stares_back` / 4 | Pest Queen / 599 | Research recorded conflicts: Darkan combatdef maxHit520 conflates special with ordinary214; PestQueen attack classes instead return200 and explicitly leave accurate combat rolls TODO. Hidden stats remain unavailable. |
| 69 | `do_no_evil` / 8 | Leeuni / 165 | Darkan omits combatLevels; no hidden values to retain. |
| 70 | `do_no_evil` / 8 | Ayuni / 170 | Research recorded conflicts: Darkan hitpoints3 versus period3,000; preserve the source unit/parsing conflict. Range max hit is explicitly unknown. |
| 71 | `do_no_evil` / 8 | Eruni / 180 | Research recorded conflicts: Historical visible metadata differs between 6487478 and unmarked 5657165: {'displayed_level': '180', 'life_points': '5,000', 'attack_style': '[[Melee]], [[Magic]], [[Ranged]]', 'max_hit': '170 (melee), 250+ (magic), 220+ (Ranged)'}; Darkan hitpoints5 versus period5,000; current page excludes melee whereas unmarked older revision lists Melee/Magic/Ranged with melee170. A resolver cannot silently choose a style or the first numeric max hit. |
| 72 | `king_of_the_dwarves` / 4 | Colonel Grimsson / 160 | Research recorded conflicts: Darkan LP1/max1/combatLevels all0 are stubs. Bestiary has later level84/LP15000 and no strength; not admitted. |
| 73 | `salt_in_the_wound` / 4 | Risen knight / 0 | Research recorded conflicts: No selected unique variant for input level0. Bestiary level60/LP2150 conflicts with period level47/54/63 and LP420/560/610; no strength. |
| 74 | `salt_in_the_wound` / 4 | Brute / 63 | Research recorded conflicts: Dungeoneering generic combatdef has LP200/max1 and no combatLevels; not a verified level63 Salt in the Wound stat block. |
| 75 | `the_branches_of_darkmeyer` / 6 | Harold / 161 | Research recorded conflicts: Darkan LP1/max1/zero levels are stubs. Bestiary level98/LP10000 differs historical level161/LP1600 and omits strength. |
| 76 | `the_branches_of_darkmeyer` / 6 | Vanstrom Klause / 332 | Research recorded conflicts: Level332 combatdef DEFENSE180/MAGE180 versus bestiary defence70/magic70, with zero ATTACK/STRENGTH. Darkan max190 versus historical level332 max254. Reclassifying as magic does not resolve melee phase or 180-versus-70 conflict. |
| 77 | `ritual_of_the_mahjarrat` / 8 | Armoured zombie / 85 | Research recorded conflicts: Bestiary NPC8149 level86/LP6200 conflicts with period/cache level85/LP850. No strength in bestiary or combatdef. |
| 78 | `ritual_of_the_mahjarrat` / 8 | Enhanced ice titan / 275 | Research recorded conflicts: Bestiary level98/LP21000 differs period level275/LP15000. Combatdef omits hidden levels. |
| 79 | `ritual_of_the_mahjarrat` / 8 | Armoured zombie / 135 | Research recorded conflicts: Historical Armoured zombie oldid6542754 is level85, never evidence for level135. Cache proves NPC14278 level135 only. The LP850/max86 level135 combatdef has no corroborated target LP or hidden levels. |
| 80 | `the_firemakers_curse` / 6 | Char / 501 | Research recorded conflicts: Darkan LP1/max1 are stubs; no combatLevels. Historical damage mechanism depends on fires rather than a recovered attack/strength/defence block. |
| 81 | `the_elder_kiln` / 5 | TzHaar-Ket-Yit'tal / 313 | Research recorded conflicts: Historical max334 conflicts with Darkan max480. Both historical and Darkan LP3000, but no hidden levels. Bestiary level105/LP7500 is a later variant. |
| 82 | `the_elder_kiln` / 5 | Lava monster (Elder Kiln) / 198 | Research recorded conflicts: Historical LP500/Magic/max354 versus Darkan LP260/RANGE/max80 and zeros. Bestiary level103/LP3700/magic74/defence74/ranged0 is later data; cannot recover period ranged level. NPC7772 level47 is a different quest and never substitutes for NPC15188. No magic reclassification can close the conflict. |
| 83 | `the_elder_kiln` / 5 | TokTz-Ket-Dill / 100 | Research recorded conflicts: Historical melee max146 (Ranged only during TokTz-Ket-Dill) conflicts with generic combatdef max80. Bestiary level64/100 and LP10000 are not period LP2060. Restoration contract explicitly treats beta infobox values as bounded anchors and armour formulas as inference. |
| 84 | `the_elder_kiln` / 5 | TokHaar-Ket Champion / 357 | Research recorded conflicts: Exact title/capitalization/hyphen monster-page probes have no pre-cutoff revision. Normal TokHaar-Ket oldid6033307 is level180/LP1500, not champion357; cannot substitute. Darkan LP1/max1 is a stub. |
| 85 | `whats_mine_is_yours` / 2 | Living rock brawler / 2 | Research recorded conflicts: Bestiary NPC6514 level1 differs period/cache level2. LP60 agrees, but bestiary omits strength, historical max hit is blank, and there is no exact combatdef. |

## Statements corrected against retained bytes

The source review of 2026-10-03 was resolved against a read-only evidence packet of retained originals. Reviewer prose is not source authority, so each finding was checked against the bytes. These statements did not survive that check.

| Statement | Where it came from | What the retained bytes say |
| --- | --- | --- |
| Juvinate `6146624` "states `level 54`" and maximum hit `59` | this record and the registry row, repeated in part by the review | `literal/juvinate.json` at `revid 6146624` states routes at level `59`, `90` and `119`, with LP `500`, `900`, `1500` and maximum hits `64`, `64`, `90`. |
| Alias `6097148` states `level = 54 / 112`, `LP = 850 / 1200`, `max hit = 54 / 104` | the review's finding 3 | those values belong to the later revision `6552297`, which the bare cache key `literal/vampyre_juvinate.json` holds. Revision `6097148` sits under the hex-suffixed key and states `level = 54`, `LP = 850` and `max hit = 54/63/72/81/90`. |
| "the archives cannot restore them", inferred from `batchcomplete` | the review's finding 5 | `batchcomplete` proves only a live write. `_period_pages` does restore negative receipts, and the archives hold API-shaped negative payloads for many `(monster)` titles. The four named receipts are unrestorable because no API-shaped archive payload names those four titles, not because negative receipts cannot be restored. |
| "One range is wrong" about `Wanted.kt:284-294` against `Wanted.kt:288-291` | the review's finding 7 | both spans are real and describe different things: `284-294` is `startSolusFight`, and `288-291` is the spawn block inside it. The two records now cite the same span. |
| Five Darkan files "key on `names`, not `ids`" and so supply no identity | the review's finding 4, as a complete account | correct about the five files, and this record claims no id from them. It is incomplete for Solus Dellagar, where the identity comes from `WantedState.kt:15` with `Wanted.kt:284-294`, not from the combatdef. |

Citations re-read. Every wiki quote in the five admitted rows was re-read against its own retained bytes: Othainian `6110941` and `5373309`; Sir Leye `6430968` and `5380553`; Ice troll male `6288801` and `5669851`; The Illusive `5908075` and `5668876`; Solus Dellagar `5587768` and `6342730`. Every Darkan field line number in the registry, the register and this record was re-read against the six retained combat definitions and matches: Othainian at lines 18 to 22, Ice troll male at lines 18 to 22, and Sir Leye, The Illusive and Solus Dellagar each at lines 17 to 21, in the field order attack, ranged, strength, defence, magic. No field value or line number changed in this repair.

## Verification boundary

The Othanian behavior test drives `handle_quest_answer` with seeded review RNG, resumes a stage with prior fights recorded, checks LP decreases across reviews, and requires a recorded win. It uses the real combat resolver.

Failure mode the Othanian test cannot reach. Solus Dellagar has hidden levels all `0`, as do Sir Leye and The Illusive, so it depends on two rules that the Othanian fight never touches. First, `logic_pure/logic_pure_quest.py:495-501` admits an all-zero stat block only when the encounter also carries a positive maximum hit; Othanian passes the ordinary branch at line 491 instead. Second, `logic_pure/logic_pure_quest.py:583-585` raises those zeros to `1` when it builds the enemy spec. If maximum hit were absent or `0`, the stage would report "This fight is not modelled yet (combat stats missing)" and leave Wanted! stage 5 unfinishable. A positive maximum hit `1` still admits the encounter and reduces incoming enemy damage; it does not reduce player damage or prevent a win. The win test proves that the encounter is resolvable and can record a win. The exact source-qualified maximum hit `40` is a separate static source/data binding.

`tests/combat/test_quest_combat_placeholders.py` therefore adds `test_solus_with_zero_hidden_levels_resolves_to_a_recorded_win`: it asserts the stage offers the Solus encounter as a resolvable fight, drives `handle_quest_answer` with a seeded review RNG until the win is recorded, and requires the recorded win, the "Defeated Solus Dellagar" activity line, the preserved Black Knight record and no errors. The same module adds `test_a_placeholder_row_cannot_feed_the_catalog_builder`, which fails if any row carrying a `placeholder_admission` regains a `payload` and so reopens the unmarked-stats path described above. It keys on the admission rather than on the `registered_placeholder` status string, so renaming a row's status cannot carry a payload past it, and it first asserts that at least one admission row exists, so an empty registry cannot pass it vacuously.

Second level, not fixed: `generated/quest_catalog_generated.py:16140-16156` already carries `in_aid_of_the_myreque_vampyre_juvinate_50` with full unmarked stats `hitpoints=1100`, `attack=50`, `strength=37`, `defence=30`, `magic=1`, `ranged=1` and `max_hit=60`, from `vampyre_juvinate_(50) (noanims).json`. That is a different encounter from blocked research row 14: it is display name "Vampyre Juvinate" at quantity 2 with source text "2 Vampyre Juvinates (level 50 and 54)", while row 14 is display name "Juvinate" at input level 50 for the count of four. The generated row predates this slice, because the catalog builder matched the Darkan name directly, so no `PLACEHOLDER(...)` marker exists and the placeholder register cannot see it. It carries the same unverified Darkan payload this review refused for row 14. Returning row 14 to `source_blocked` leaves this generated row exactly as it stands on main; this slice repairs neither it nor the name-matching path that produced it.

Existing tests, audit code, reachability pins, the owner-reserved combat-magic branch and Dream transaction code are unchanged. Remote results and final counts belong in `memory-bank/progress.md`; raw output belongs in the slice evidence folder.
