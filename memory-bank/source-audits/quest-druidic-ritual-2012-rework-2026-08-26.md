# Druidic Ritual 2012 rework — 2026-08-26

## Scope and cutoff

This audit replaces AnkiScape's retired raw-meat and Cauldron of Thunder route with the Druidic Ritual rework released on 31 January 2012. The target is the live game immediately before EOC on 20 November 2012.

The implemented contract covers the quest's requirements, ordered ingredients, item transformations, rewards, Herblore relationship, and a forward-only migration for saves that started the retired version. It does not add a general Druidic Ritual gate to Herblore. Jungle Potion keeps its separate Druidic Ritual plus level-3 Herblore entry requirements.

## Pinned period pages

| Page | Revision | Timestamp (UTC) | Claims used |
|---|---:|---|---|
| `Druidic Ritual` | `6488185` | `2012-10-28T13:54:25Z` | 31 January 2012 rework, requirements, ingredient route, four quest points, 250 Herblore XP, 15 noted grimy guam, 15 noted eyes of newt, and removal of the old Herblore training gate |
| `Druidic Ritual/Quick guide` | `6168973` | `2012-08-31T04:57:38Z` | Ordered Kaqemeex/Sanfew route; Living water; Wandering wyrmwood; coin-baited Stone fish; Chisel to Stone scales; Ointment of imbalance hand-in |
| `Living water` | `5871546` | `2012-07-02T00:40:07Z` | Vial requirement, cave source, and non-tradeable/non-stackable state |
| `Wandering wyrmwood (item)` | `5987356` | `2012-07-25T01:53:38Z` | Quest ingredient identity; location in south Taverley, just north of Nora T. Hagg's house; and non-tradeable/non-stackable state |
| `Stone fish` | `5907958` | `2012-07-08T12:21:10Z` | Coin-and-rod catch, retained Stone fish when Chiselled, repeatable scale gathering, and non-tradeable/non-stackable state |
| `Stone scales` | `5236531` | `2012-02-09T20:26:58Z` | Chiselling a Stone fish produces the non-tradeable/non-stackable scales |
| `Ointment of imbalance` | `5236532` | `2012-02-09T20:27:01Z` | Sanfew combines the three ingredients; Kaqemeex receives the non-tradeable/non-stackable ointment |
| `Herblore` | `6569702` | `2012-11-17T23:17:35Z` | Druidic Ritual was no longer required to train ordinary Herblore after the rework |
| `Dungeoneering/Herblore` | `6555616` | `2012-11-14T20:45:41Z` | Daemonheim's separately scoped Druidic Ritual and complexity-5 gates remain period rules |
| `Herbs` | `6555201` | `2012-11-14T12:01:40Z` | Pre-cutoff clean-herb level column |
| `Grimy guam` | `6560041` | `2012-11-15T20:35:14Z` | Guam cleaning requires Herblore 1 and awards 2.5 XP |

Stable URLs use the form `https://runescape.wiki/w/<page>?oldid=<revision>`. Literal revision text, including the quest-details, walkthrough, rewards, and historical gate statements, was inspected rather than relying on the current rendered pages.

## Cache evidence

The closest local pre-cutoff cache is OpenRS2 build 742, dated 7 November 2012:

- archive `runescape-742-2012-11-07-openrs2-544-disk.zip`;
- SHA-256 `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`;
- items `23096` through `23100`: `Living water`, `Wandering wyrmwood`, `Stone fish`, `Stone scales`, and `Ointment of imbalance`; all five are non-stackable and non-exchangeable;
- item `23098`, `Stone fish`, has `Gather-scales` and `Destroy` options; and
- object `67687`, `Sparkling Fishing Spot`, has the `Bait` option.

The cache directly corroborates the reworked client identities and interactions. It does not independently prove server-side quest ordering or rewards.

Darkan's committed `developer-information/itemList.txt` also retains the contiguous rework identities at supplying commit `c6fbe036b1743f4dd6067ec178332c69c3708856`:

- `23096` — Living water;
- `23097` — Wandering wyrmwood;
- `23098` — Stone fish;
- `23099` — Stone scales; and
- `23100` — Ointment of imbalance.

## Darkan reconstruction provenance and conflict

The inspected reconstruction is:

- checkout `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server`;
- inspected HEAD `6277992980582f7b3da3a48e722e96cfa5b0a57d`;
- source directory `src/main/java/com/rs/game/content/quests/druidic_ritual/`;
- principal files `DruidicRitual.kt`, `dialogues/npcs/KaqemeexD.kt`, `dialogues/npcs/SanfewD.kt`, `utils/DruidicRitualConstants.kt`, and `utils/DruidicRitualUtils.kt`; and
- supplying quest refactor commit `2d4c76a83d7385ce087b766f443e57685f7fa980` (`2024-06-03T20:44:49+01:00`). Later path commits are `91556c21eb7b3ff779d94c4281fc2a829399f72b` and `459ed03f0f9830824ef6b5bd458bcef235f623d6`.

The conflicting game-main evidence is an unversioned local snapshot at `/Users/ArmanTarkhanian1/Downloads/game-main`; neither that directory nor its parent retains Git metadata. The inspected files are `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/quests/impl/DruidicRitual.kt`, `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/areas/taverley/sanfew.plugin.kts`, and `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/objs/cauldron_of_thunder.plugin.kts`.

Darkan and game-main conflict with the live-period record: both current implementations still model the historical raw bear/rat/beef/chicken and Cauldron of Thunder quest. Darkan is therefore reconstruction-class evidence for the Kaqemeex/Sanfew quest shell and reward application, not the authority for the post-January ingredient route. The pinned post-rework pages supply that route, and rev-742 independently confirms its Stone fish and Sparkling Fishing Spot identities. No meat or Cauldron action survives in live AnkiScape quest data.

## Implemented quest contract

1. Kaqemeex sends the player to Sanfew.
2. Sanfew requests Living water, Wandering wyrmwood, and Stone scales; AnkiScape grants one Vial under the named one-ledger abstraction below.
3. The Vial is consumed to collect Living water.
4. The player collects Wandering wyrmwood in south Taverley, just north of Nora T. Hagg's house.
5. One coin is consumed while a Fishing rod is retained to catch a Stone fish at the Sparkling Fishing Spot.
6. A Chisel and the Stone fish are retained while Stone scales are gathered.
7. Sanfew consumes the three ingredients and produces Ointment of imbalance.
8. Kaqemeex consumes the ointment and completes the quest.

Completion awards four quest points, 250 Herblore XP, 15 Grimy guam, and 15 Eye of newt. The period's two Squeal of Fortune spins remain outside AnkiScape because that system is not modeled. Noted reward state is represented by the existing bank quantity ledger, which does not distinguish noted from unnoted bank stacks.

The ordinary overworld Herblore catalog has no quest prerequisite. `clean_guam` is pinned to level 1 and 2.5 XP from `Grimy guam` oldid `6560041`; the remaining ordinary clean-herb levels already matched the complete pre-cutoff table in `Herbs` oldid `6555201`. Jungle Potion separately keeps its Druidic Ritual plus Herblore 3 entry gate. Daemonheim also keeps its period-specific Druidic Ritual gate from `Dungeoneering/Herblore` oldid `6555616`; the general-skill gate removal does not supersede that separately scoped ruleset.

## Save migration contract

Schema v119 runs once for saves with `config_version < 119`:

| Retired progress | Reworked progress | Treatment |
|---:|---:|---|
| 0 | 0 | Preserve the accepted-but-unadvanced state |
| 1 | 1 | Preserve the Kaqemeex-to-Sanfew boundary |
| 2 | 2 | Continue at the first reworked ingredient stage and seed the quest-supplied Vial |
| 3 | 6 | Move forward to Sanfew's ingredient hand-in and seed Living water, Wandering wyrmwood, and Stone scales |
| completed / 4+ | completed / 8 | Preserve completion at the new final progress |

Any enchanted bear meat, rat meat, beef, or chicken is converted back to the matching raw meat in the bank. Existing raw meat remains untouched. Only the three retired Druidic action flags are removed. Current and future schema saves are not remapped, so the conversion is forward-only and idempotent.

## Review-native abstractions and unresolved values

**One-ledger Vial grant.** The period quest gives a Vial only when the player does not already have one. AnkiScape's static quest-stage projection and single bank ledger do not model that conditional dialogue grant, so advancing Sanfew's request adds one Vial unconditionally. This named abstraction creates no separate quest inventory and is the only non-exact item transform in the route.

AnkiScape represents travel, dialogue, gathering, fishing, and item-use interactions as deterministic review advances. It does not model walking time, object respawn, fishing animation timing, or a hidden success roll for these quest steps. No unsupported rate, timer, or probability was introduced. Apart from the named Vial grant, the source-backed item requirements and transformations remain exact despite that presentation abstraction.

## Enforcement

- `tests/test_logic.py` walks the complete reworked route, proves the named Vial grant, proves the Vial and coin are consumed while the tools and Stone fish are retained, checks quest-item transforms in order, rejects retired actions, and pins exact rewards.
- `tests/test_quest_catalog.py` pins the ordered reworked actions, stage transforms, rewards, and five quest-item identities.
- `tests/test_runtime_actions.py` proves a level-1 player without Druidic Ritual can clean guam through the live Herblore handler for 2.5 XP.
- `tests/test_herblore_data.py` pins the full ordinary clean-herb level column and the row-specific guam oldid.
- `tests/test_dungeoneering_logic.py` rejects the Daemonheim Herblore chain below complexity 5 and without Druidic Ritual.
- `tests/test_storage_pure.py` covers every old progress mapping, completed saves, ingredient seeding, meat return, action retirement, one-time execution, and current-schema non-migration.
