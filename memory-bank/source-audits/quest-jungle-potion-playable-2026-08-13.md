# Jungle Potion playable quest closure — 2026-08-13

## Scope and result

`Jungle Potion` is now a complete review-native quest rather than generated objective buttons plus unavailable herb hand-ins. The live path preserves the Druidic Ritual and level-3 Herblore gates, strict five-herb order, search locations, grimy/clean identities, cleaning actions, one-at-a-time Trufitus turn-ins, 775 Herblore XP, one quest point, and the Shilo Village prerequisite edge.

No unsupported search probability or node respawn timer was introduced. Search and dialogue are deterministic review-native stages, so this slice adds no placeholder value.

## Evidence hierarchy

Primary restoration evidence was read from committed Darkan content:

- repository commit `3fb3671b04558b360ad3422af48ad6ae4add00e2` (`Restore Jungle Potion's ordered herb route`);
- `src/main/java/com/rs/game/content/quests/junglepotion/JunglePotion.java`;
- `src/main/java/com/rs/game/content/quests/TrufitusDialog.kt`;
- `src/main/java/com/rs/game/content/skills/herblore/HerbCleaning.java`; and
- `developer-information/itemList.txt`.

Period cache evidence:

- OpenRS2 cache build `727`, dated `2012-07-24`, archive ID `309`;
- SHA-256 `ba79072542d1bda4d8140be38839b540133e79bc40c80665ef1772be178b29f8`;
- committed extraction record `memory-bank/audit/evidence/static/openrs2-cache-727-jungle-potion.json` in restoration commit `1fa41fe735f27a14924842eac53288aa8ee4b0a2`.

Pinned period page:

- RuneScape Wiki `Jungle Potion`, oldid `6555418`, timestamp `2012-11-14T16:30:32Z`.

## Source-to-value map

| Live value | Evidence |
|---|---|
| Start at Trufitus near Tai Bwo Wannai | Darkan quest annotation; wiki oldid `6555418` |
| Requires Druidic Ritual and Herblore 3 | Darkan start dialogue/quest eligibility; wiki oldid `6555418` quest details |
| Firemaking 33 and Slayer 33 are not entry requirements | Wiki oldid `6555418` lists both only inside the optional recommended lit bug lantern bullet |
| Five sequential objectives | Darkan stages `FIND_SNAKE_WEED` through `FIND_ROGUES_PURSE`; Trufitus dialogue; wiki walkthrough |
| Snake weed: vine 2575/2576, items 1525/1526 | Darkan quest source; rev-727 cache; committed item list |
| Ardrigal: palm 2577/2578, items 1527/1528 | Darkan quest source; rev-727 cache; committed item list |
| Sito foil: scorched earth 2579/2580, items 1529/1530 | Darkan quest source; rev-727 cache; committed item list |
| Volencia moss: rock 2581/2582, items 1531/1532 | Darkan quest source; rev-727 cache; committed item list |
| Rogue's purse: cavern wall 32106/32107, items 1533/1534 | Darkan quest source; rev-727 cache; committed item list |
| Every herb cleans at level 3 for 2.5 Herblore XP | Darkan `HerbCleaning.java` rows |
| Every clean herb is deleted before stage advance | Darkan `turnInHerb` and Trufitus stage dialogue |
| Reward: 775 Herblore XP and one quest point | Darkan quest annotation/completion method; wiki oldid `6555418`; rev-727 quest record |
| No mandatory combat | Darkan quest annotation; wiki distinguishes environmental dangers from requirements |
| Tai Bwo Wannai Cleanup, Rionasta parcel service, Calquat gardener, Shilo eligibility | Wiki oldid `6555418` rewards and quest-requirement sections |

## Period icon revisions

The five clean-herb icons use exact pre-EOC RuneScape Wiki file revisions rather than the current files:

| Asset | Timestamp | SHA-1 |
|---|---|---|
| `clean_snake_weed.png` | `2011-11-19T07:13:54Z` | `a3944f8d0b26c3141abe884ade09894b6236a70a` |
| `clean_ardrigal.png` | `2011-11-19T06:44:52Z` | `478c5c99327a08df07c8f4e2301af36da6ce1208` |
| `clean_sito_foil.png` | `2011-11-19T07:13:44Z` | `2b9deea326a58dd7d0d0e1dbf30e47a60e615ccd` |
| `clean_volencia_moss.png` | `2011-11-19T07:24:04Z` | `2b9deea326a58dd7d0d0e1dbf30e47a60e615ccd` |
| `clean_rogue_s_purse.png` | `2011-11-19T07:09:36Z` | `2b9deea326a58dd7d0d0e1dbf30e47a60e615ccd` |

`assets_provenance.json` records each archived image URL, revision timestamp, SHA-1, and byte size. Each downloaded file was SHA-1 and size verified before installation.

## Review-native stage ledger

Each herb uses two real production paths:

1. a quest review searches only the source-backed object for the current herb and produces the exact grimy item;
2. the ordinary Herblore handler cleans that item at level 3 for 2.5 XP;
3. the next quest review consumes the exact clean item and records the Trufitus hand-in.

The pairs repeat in strict order for snake weed, ardrigal, sito foil, volencia moss, and rogue's purse. The eleventh state is the ordinary completion sentinel. No generated `Complete Jungle Potion stage N objective` action survives in live data.

The prerequisite Druidic Ritual dialogue and cauldron steps use their existing deterministic `auto_actions`. This repairs their audit emitters without changing their item transformations or production-handler behavior, allowing the real prerequisite chain to close rather than bypassing it.

## Reachability result

Promoted merge `a0088a593427f0769b6d67f6e9365a59317ce02f` was re-measured against its `main` parent `4f86193c93d5a4c36c8f71a9509bcedc512b0cb9` with the corrected union-of-per-scenario quest-branch audit (`tools/audit_item_reachability.py` SHA-256 `99042e4d583338c56ef72534f37581f9051c0c35fc197f5b09bdcff86a12877b`).

Main before this slice:

- 1,571 actions;
- 2,278 reachable items;
- 72 orphan inputs;
- 45 root orphans;
- 27 cascade orphans;
- 71 unresolved actions;
- 1,105 seed items.

Merged result after this slice:

- 1,581 actions;
- 2,301 reachable items;
- 72 orphan inputs;
- 45 root orphans;
- 27 cascade orphans;
- 71 unresolved actions;
- 1,123 seed items.

The ten added actions are the five source-backed searches and five Herblore cleaning conversions.

Gross reachable-item additions, measured by comparing the corrected main and merged route sets:

- Grimy snake weed
- Clean snake weed
- Grimy ardrigal
- Clean ardrigal
- Grimy sito foil
- Clean sito foil
- Grimy volencia moss
- Clean volencia moss
- Grimy rogue's purse
- Clean rogue's purse
- Wampum belt
- Stone-plaque
- Tattered scroll
- Crumpled scroll
- Zadimus corpse
- Bone shard
- Sword pommel
- Locating crystal
- Bervirius notes
- Bone key
- Bone beads
- Beads of the dead
- Rashiliyia corpse

Gross reachable-item removals: none.

All ten jungle-herb identities and all thirteen named Shilo Village identities are reachable. Shilo routes are one `quest-start:shilo_village` source (`Wampum belt`) plus twelve `quest-stage:shilo_village:*` sources. Neither Jungle Potion nor Shilo Village has a blocked quest-stage diagnostic after closure.

## Re-land verification — 2026-08-19

The preserved slice was merged with `main` commit
`4f86193c93d5a4c36c8f71a9509bcedc512b0cb9` as promoted merge
`a0088a593427f0769b6d67f6e9365a59317ce02f`. Git reported no content
conflicts, so no source-backed Jungle Potion value or `PLACEHOLDER(...)` marker
was reconstructed during conflict resolution. The branch has no production UI
or panel delta from main; quest eligibility remains owned by
`can_start_quest_pure`.

A standalone driver invoked the live `handle_quest_answer` and
`handle_herblore_answer` handlers. It started from an unstarted Jungle Potion
state, produced and cleaned the five herbs in order, consumed each clean herb,
completed at progress 11, moved quest points from 4 to 5, moved Herblore XP
from 250.0 to 1037.5, and made Shilo Village startable. The reachability report
then resolved all ten herb identities and all thirteen Shilo Village-only
products with zero Jungle Potion or Shilo Village blocked-stage diagnostics.

At the named main parent, `tools/audit_item_reachability.py` reported 1,571
actions, 2,278 reachable items, 72 orphan inputs, and 71 blocked actions. The
merged tree reports 1,581 actions, 2,301 reachable items, 72 orphan inputs, and
71 blocked actions. Both expected nonzero audits exit 1 because the repository
still has 71 unrelated blocked actions.

## Post-quest herb searches — 2026-08-19

The five search activities remain available after quest completion. Darkan's
current handlers gate each object to the matching quest stage, but the period
record does not: rev-727 and all six other on-disk caches retain `Search` on
objects 2575, 2577, 2579, 2581, and 32106, while game-main contains only item
identities. The pre-EOC herb pages establish continued acquisition and use:
`Grimy sito foil` oldid `5380474` explicitly says the spot works after the
quest; `Grimy volencia moss` oldid `6358574` says players doing or finished the
quest can search the rocks; and oldids `5379720`, `4363001`, and `5456824`
record the other search spots and their post-start or post-quest uses.

A cross-catalog scan found six quest-item transformations through
strange-rock-eligible handlers: the five Jungle Potion cleanings and Heroes'
Quest `cook_lava_eel`. The latter is recoverable through the repeatable
`lava_eel` Fishing target, so no other strictly one-shot exposure remains.

The shipped Jungle Potion rock exemption is an AnkiScape safeguard, not a rule
recovered from Darkan. Darkan gates each search object on
`questStage == requiredStage`, and only the clean-herb turn-in advances that
stage; a player who loses the clean herb can therefore search the same object
again. AnkiScape splits that source stage into a search review and a later
turn-in review, advancing past the search as soon as the grimy herb is found.
That split makes the search one-shot before turn-in, so the runtime suppresses
strange-rock output replacement for the five cleanings while the quest remains
incomplete. The source-faithful alternative is to keep each herb search
reachable until its corresponding turn-in completes. Replacing the shipped
safeguard with that stage model is queued for an owner decision.
