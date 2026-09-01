# Zogre Flesh Eaters stages 1–6 source audit — 2026-09-01

## Scope

This audit replaces the six generated `Complete Zogre Flesh Eaters stage N
objective` requirements that blocked stages `1` through `6`. It removes
preparation materials that the pinned period dossier identifies as optional,
places the two mandatory fights and their guaranteed drops on their sourced
stages, removes a false undosed Relicym's balm completion reward, and removes an
unsupported Prayer XP award. It does not change quest acceptance, quest points,
the started-quest Zogre source, the ogre-coffin selector, combat statistics,
runtime code, or any user interface.

No placeholder value is used.

## Existing evidence ownership and verdict

The Darkan audit thread already owned and froze the complete evidence harvest.
This slice reconciles against that record and keeps no independent wiki harvest.
The controlling contract is:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/zogre-flesh-eaters-target-contract.json`

Its baseline world commit is `2d4083fb48c69685831268511e147681950a5f53`,
its baseline tree is `ceaf7e33796a2dc9bf28dc47f1438351df132558`,
and its verdict ceiling is exactly
`PARTIAL[source_blocked,conflicting_sources,missing_data]`.

The historical route source that controls stage ordering is the existing final
pre-Evolution-of-Combat dossier:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/zogre-flesh-eaters-final-preeoc-oldid-6441901.json`

That file contains revision `6441901`, timestamp `2012-10-19T11:57:51Z`, and the
full historical wikitext. The build-727 dossier independently predates the final
article revision but belongs to the same cache lineage and is corroborating,
not a second vote:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/zogre-flesh-eaters-build727-oldid-5981068.json`

It contains revision `5981068`, timestamp `2012-07-23T12:55:38Z`, and gives the
same zombie-before-investigation and Slash-Bash-after-stone-doors order.

The focused balm and boss records are:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/zogre-relicyms-balm-oldid-6324779.json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/zogre-slash-bash-oldid-6521180.json`

## Executable ordering check

The read-only Kotlin implementation corroborates the frozen contract:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/zogre_flesh_eaters/ZogreFleshEatersState.kt`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/zogre_flesh_eaters/ZogreFleshEatersContent.kt`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/zogre_flesh_eaters/ZogreFleshEaters.kt`

`ZogreFleshEatersState.kt:51-66` defines the ordered states from
`NOT_STARTED 0` through `COMPLETE 14`. The crypt zombie exists only at
`TOMB_OPEN 2` (`ZogreFleshEatersContent.kt:80-89`), and its owner-scoped death
yields the ruined backpack before evidence progression (`:322-331`). Slash Bash
spawns only after the gate-key and stone-door sequence at `BOSS_READY 11`
(`:241-264`); its owner-scoped death yields the artefact and advances to
`ARTEFACT_RECOVERED 13` (`:363-373`). Giving that artefact to Grish completes
the quest (`ZogreFleshEatersState.kt:238-243`).

This source order requires the level-39 Zombie on AnkiScape stage `2` and Slash
Bash on stage `6`. The generated catalog had stacked both encounters on stage
`5`; that arrangement was rejected because it recorded durable stage actions
claiming fights that had not happened.

## Stage mapping

| AnkiScape stage | Frozen route segment | Source-backed action | Mandatory fight |
| ---: | --- | --- | --- |
| `1` | Acceptance through the barricade and tomb entry | Speak to the ogre guard, open Jiggig's barricade, and enter the tomb. | None |
| `2` | Skeleton, coffin, crypt evidence, Yanille evidence presentation, and Sithik-room search | Defeat the crypt zombie, recover the tomb evidence, show it in Yanille, and search Sithik's room. | Zombie level `39` |
| `3` | Accurate portrait, bartender signature, and evidence hand-off | Draw and sign an accurate portrait of Sithik, then present the complete evidence to Zavistic Rarve for the strange potion. | None |
| `4` | Tea drugging, room exit/re-entry, transformation, and interrogation | Drug Sithik's tea, leave and return after his transformation, then interrogate him about the disease and brutal arrows. | None |
| `5` | Grish report, recoverable gate key, bow knowledge, and return to the tomb | Report Sithik's confession to Grish, receive the ogre gate key and bow knowledge, and return to the tomb. | None |
| `6` | Stone doors, stand search, boss death, artefact recovery, and Grish completion | Open the stone doors, defeat Slash Bash, recover the ogre artefact, and return it to Grish. | Slash Bash level `111` |

The assembled catalog is pinned to exactly that encounter distribution:
`stage 2 -> zogre_flesh_eaters_zombie_39` and
`stage 6 -> zogre_flesh_eaters_slash_bash_111`, with no Zogre quest encounter
on stages `1`, `3`, `4`, or `5`.

## Combat drops and completion XP

The frozen contract states that the owner-scoped Zombie death yields one
`Ruined backpack`, and that Slash Bash yields exactly two `Zogre bones`, three
`Ourg bones`, and one `Ogre artefact`. The relocated encounter rows now carry
those exact guaranteed drops. Focused pure and real review tests verify all four
item quantities after the fights.

The same contract states that completion grants exactly `2,000` XP each in
Fletching, Herblore, and Ranged. It does not grant Prayer XP. The generated
catalog's extra `162.5` Prayer XP is therefore removed through the existing XP
reward replacement boundary, and focused completion tests pin Prayer XP at
zero while the three sourced skills each receive `2,000`.

## Optional materials removed from the stage gates

Both existing historical quest dossiers put the following items under
conditional “if making your own” preparation, and the frozen target contract
separates those production services from the mandatory route:

- `Achey tree logs`;
- `Vial of water`;
- `Rogue's purse`;
- `Snake weed`;
- `Wolf Bones`;
- `Bowstring`.

The final pre-EOC dossier expressly says making Relicym's balm, the composite
ogre bow, and brutal arrows is not necessary. The cleanup therefore removes the
raw generated item names before canonical normalization. The old catalog test
that expected `Clean rogue's purse` at stage `4` was stale; it now pins the
source-backed empty stage inventory instead.

This is not a workaround for absent routes. The pre-change report already had
routes for the canonical identities: `Achey tree logs` through
`Woodcutting:achey`, `Vial of water` through `combat:cave_crawler`,
`Clean rogue's purse` and `Clean snake weed` through Herblore cleaning,
`Wolf bones` through `combat:big_wolf`, and `Bow string` through
`shop:alison_fletch_shop`.

## Relicym's balm reward decision

The frozen contract and the focused balm dossier state that the sourced recipe
combines Rogue's purse potion (unf) with clean snake weed to produce
`Relicym's balm (3)` item `4844`. Quest completion grants the ability to make
the potion; it does not award an undosed item named `Relicym's balm`.

The generated quest catalog had converted that ability into an undosed item
reward. That identity had no dose-state consumer: the nearby Barbarian Herblore
consumer uses `Relicym's balm (2)`. Leaving the generated reward would have
raised reachability by one while closing no real route. The item reward is
therefore replaced with only `Black prism`, which is obtained during the
investigation and may be retained after completion. After the correction:

- undosed `Relicym's balm` has no route;
- `Relicym's balm (2)` remains unrouted;
- `Relicym's balm (3)` retains its existing `shop:uglugs_stuffsies` route;
- `Black prism` becomes reachable through `quest:zogre_flesh_eaters`.

The full cure-production and dose chain remains a separate source-backed product
slice; this stage repair does not pretend to close it.

## Sentinel translation

Each of the six cleanup rows removes its exact generated sentinel through
`remove_required_actions` and adds one same-stage automatic action. This order
is required: `logic_pure/logic_pure_quest.py` records automatic actions only
after the current stage has passed its blockers. Adding an automatic action
without removing the sentinel would leave the quest impassable.

The focused test's action oracle is a pinned literal transcription of the
`quest_route` fields in
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/zogre-flesh-eaters-target-contract.json`;
it is neither copied from nor derived from the cleanup table under test. The
pure flow proves the Zombie blocks stage `2`, Slash Bash blocks stage `6`, and
each durable action proof is written only after its sourced gate passes. The
real `on_answer_card()` path reads the dynamically loaded add-on's own quest
catalog, reaches completion, and stores the completed flag.

## Quest-local item leads

The frozen target contract models the full quest-local custody chain.
AnkiScape now grants the sourced `Ruined backpack` and `Ogre artefact` combat
drops at runtime, but those two names are not registered in the global item
reachability graph, so the graph does not credit them as routes. The remaining
intermediate identities are represented inside the source-backed stage actions
rather than exposed as external inventory gates:

`Torn page`, `Dragon inn tankard`, `Poor portrait`, `Accurate portrait`,
`Signed portrait`, `Book of portraiture`, `Book of 'h.a.m'`, `Strange potion`,
`Necromancy book`, and `Ogre gate key`.

`Black prism` is registered and reachable through the completed quest.
`Ogre gate key` is not the existing `Ogre coffin key`. Registering the two
runtime-only drops and modeling the remaining custody chain are follow-on leads
for a detailed quest-item slice.

## Reachability measurement

The baseline was re-measured from commit
`1e6795922e3860c74c4791b5fa97bc8bc478a79b`, and the result was re-measured from
the corrected implementation tree.

| Measure | Before | After |
| --- | ---: | ---: |
| `action_count` | `1663` | `1663` |
| `reachable_item_count` | `2301` | `2302` |
| `orphan_input_count` | `165` | `165` |
| `root_orphan_count` | `32` | `32` |
| `cascade_orphan_count` | `133` | `133` |
| `unresolved_action_count` | `252` | `252` |
| `seed_item_count` | `1215` | `1217` |
| blocked quest-stage rows | `139` | `138` |
| `completable_quest_count` | `51` | `52` |

`zogre_flesh_eaters` changes from one blocked row at stage `1` to no row in
`blocked_quest_stage_products`. `Black prism` is the only newly reachable item.
`Ourg bones` remains reachable but its preferred route becomes the sourced
Slash Bash quest encounter; `Zogre bones` retains its existing regular-Zogre
route. The unregistered backpack and artefact drops are verified at runtime but
are not counted by the graph. Zogre Flesh Eaters is the one newly completable
quest. No descendant count is attributed to this repair.

No placeholder is registered. The existing
`bone_sources.ogre_coffin_selector_weights` placeholder and the started-quest
Zogre combat source are unchanged.

## Separate start-contract lead

The frozen contract requires Druidic Ritual, Big Chompy Bird Hunting, Jungle
Potion, Smithing `4`, Herblore `8`, and Ranged `30`; it treats Strength `20` as
a recommendation and Fletching `30` as conditional. The current generated
AnkiScape start contract differs. This stage-sentinel slice preserves the
already live start contract and records the discrepancy as separate work.
