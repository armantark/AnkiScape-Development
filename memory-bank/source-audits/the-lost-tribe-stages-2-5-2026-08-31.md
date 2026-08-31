# The Lost Tribe stages 2–5 source audit — 2026-08-31

## Scope

This audit replaces the four generated stage sentinels that blocked The Lost
Tribe at stages `2`, `3`, `4`, and `5`. It keeps the source-backed Thieving `13`
gate at stage `5` and does not change the stage-1 cellar contract, quest
acceptance, rewards, or any user interface.

The cutoff remains `2012-11-20T00:00:00Z`. No placeholder value is used.

## Primary authority and correction of the older source block

The primary local authority is the read-only Darkan Kotlin implementation:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/the_lost_tribe/TheLostTribe.kt`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/the_lost_tribe/TheLostTribeState.kt`

The earlier stage-1 audit relied on the derived Darkan evidence contract at
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/the-lost-tribe-target-contract.json`.
That contract correctly marked the intermediate meanings of varbit `532` as
source-blocked within its own evidence boundary. It did not inspect the Kotlin
quest implementation above.

`TheLostTribeState.kt:48-62` explicitly defines every value of varbit `532`:
`NOT_STARTED 0`, `STARTED 1`, `PERMISSION_GRANTED 2`, `RUBBLE_MINED 3`,
`TUNNEL_ENTERED 4`, `BROOCH_IDENTIFIED 5`, `SYMBOL_BOOK_FOUND 6`,
`EMOTES_LEARNED 7`, `PEACE_REPORTED 8`, `TREATY_RECEIVED 9`,
`TREATY_DELIVERED 10`, and `COMPLETE 11`. The executable transition functions
in `TheLostTribe.kt` enforce those meanings. This audit therefore relies on the
Kotlin files for stages 2–5 because they are direct implementation evidence,
not a derived contract that stopped before those states.

The already pinned historical article remains corroborating evidence:
`https://runescape.wiki/w/The_Lost_Tribe?oldid=6534350`. No new wiki revision is
needed.

## Stage mapping

| AnkiScape stage | Darkan states covered | Source-backed action | Evidence |
| ---: | --- | --- | --- |
| `2` | `TUNNEL_ENTERED 4` through `SYMBOL_BOOK_FOUND 6` | Find the stone brooch, show it to Duke Horacio and Sigmund, ask Reldo about it, then recover the Goblin symbol book. | Journal lines `TheLostTribe.kt:43-44`; brooch recovery and identification `:155-165`; Reldo and bookcase path `:167-182`; Duke and Reldo handlers `:321-324,356-359`; bookcase wiring `:392`. |
| `3` | `SYMBOL_BOOK_FOUND 6` through `EMOTES_LEARNED 7` | Read the Goblin symbol book and question the two generals in Goblin Village about the Dorgeshuun. | Journal line `TheLostTribe.kt:45`; book read `:184-189`; five-step general branch `:191-198`; general handler `:362-365`; item-read wiring `:450`. |
| `4` | `EMOTES_LEARNED 7` through `PEACE_REPORTED 8` | Translate the tunnel symbols, follow the safe route, perform Goblin Bow before Mistag, then follow him back to Lumbridge. | Journal line `TheLostTribe.kt:46`; symbol and route logic `:200-221`; Goblin Bow and Mistag return `:223-234`; object and NPC wiring `:368-374,449`. |
| `5` | `PEACE_REPORTED 8` through `COMPLETE 11` | Pickpocket Sigmund's key, search his chest, recover the castle silverware, receive Duke Horacio's peace treaty, follow Kazgar, deliver the treaty to Mistag, and witness its signing. | Journal lines `TheLostTribe.kt:47-50`; Thieving `13` and key `:236-245`; chest, H.A.M. outfit, and silverware `:247-259`; treaty receipt, escort, delivery, and completion `:261-290`; Duke, Mistag, and Kazgar handlers `:326-345,368-384`; interaction wiring `:445,447-453`. |

The stage-5 Thieving gate is exact executable evidence:
`TheLostTribe.kt:236-241` rejects Sigmund's pickpocket interaction below level
`13`. No later stage has another skill, tool, combat, or external route gate.
The tunnel symbol sequence is a navigation puzzle whose wrong branch resets
local progress at `TheLostTribe.kt:208-220`; it is not an item or skill
requirement and is represented inside the stage-4 action rather than as a new
AnkiScape subsystem.

## AnkiScape translation

Each cleanup removes its exact generated `Complete The Lost Tribe stage N
objective` requirement and adds one same-stage automatic action. This ordering
matters: automatic actions are recorded only after the current stage passes its
blockers, so adding an action without removing the sentinel would still leave
the stage impassable.

Stages 2–5 cite both the pinned wiki revision and the read-only Darkan
implementation through `THE_LOST_TRIBE_STAGE_ACTION_SOURCE`. Stage `5` retains
its existing
Thieving `13` requirement. No item is produced, consumed, or required by the
AnkiScape stage contract, and no runtime or interface code changes.

## Unavailable quest-local item leads

The Darkan source uses the exact item identities in
`TheLostTribeState.kt:19-34`, but AnkiScape has no faithful acquisition route for
them. The repaired stages therefore model the interactions as source-backed
actions instead of inventing item producers or creating unreachable gates.

| Source item | Item id | AnkiScape finding |
| --- | ---: | --- |
| Brooch | `5008` | Only the value row `generated/item_values_generated.py:1728`; absent from the item registry and reachability routes. |
| Goblin symbol book | `5009` | Only the value row `generated/item_values_generated.py:4149`; absent from the item registry and reachability routes. |
| Sigmund's key (`KEY`) | `5010` | AnkiScape has a generic `Key` identity and a Biohazard route, but no item-id-specific Sigmund key contract; using the generic item would be a false gate. |
| Silverware | `5011` | Only the value row `generated/item_values_generated.py:8552`; absent from the item registry and reachability routes. |
| Peace treaty | `5012` | Only the value row `generated/item_values_generated.py:6758`; absent from the item registry and reachability routes. |
| H.A.M. shirt (`HAM_SHIRT`) | `4298` | A `Ham shirt` value row exists at `generated/item_values_generated.py:4616`, but the item is absent from the registry and routes. |
| H.A.M. robe (`HAM_ROBE`) | `4300` | Absent from the item registry and routes. |
| H.A.M. hood (`HAM_HOOD`) | `4302` | Absent from the item registry and routes. |
| H.A.M. cloak (`HAM_CLOAK`) | `4304` | Absent from the item registry and routes. |
| H.A.M. logo (`HAM_LOGO`) | `4306` | Absent from the item registry and routes. |
| H.A.M. gloves (`HAM_GLOVES`) | `4308` | Absent from the item registry and routes. |
| H.A.M. boots (`HAM_BOOTS`) | `4310` | Absent from the item registry and routes. |

These identities are follow-on leads for a future detailed quest-item model.
They are not prerequisites for this completion slice.

## Reachability measurement

The baseline was re-measured from commit
`2df4709c7253a202207275add2c6d5ca9f497338`, and the result was re-measured from
the implementation tree.

| Measure | Before | After |
| --- | ---: | ---: |
| `action_count` | `1608` | `1608` |
| `reachable_item_count` | `2243` | `2244` |
| `orphan_input_count` | `190` | `190` |
| `root_orphan_count` | `39` | `39` |
| `cascade_orphan_count` | `151` | `151` |
| `unresolved_action_count` | `277` | `277` |
| `seed_item_count` | `1177` | `1179` |
| blocked quest-stage rows | `145` | `144` |

`the_lost_tribe` changes from one blocked row at stage `2` to no location in
`blocked_quest_stage_products`. `Lumbridge Swamp Caves` becomes newly reachable;
`Ring of life` remains reachable and its preferred route changes from
`Magic:enchant_diamond_ring` to `quest:the_lost_tribe`. Completable quests
move from `44` to `45`; The Lost Tribe is the sole addition. Its `13` transitive
descendants remain outside the completable closure because each still has its
own generated sentinel.

No placeholder is registered. No new acquisition route is claimed for any of
the quest-local items above.
