# Acquisition queue final audit — 2026-08-12

## Definitive outcome

The acquisition queue is closed at commit `a08827aa`. The corrected baseline was
1,556 actions, 2,493 reachable items, 103 orphan inputs, and 102 blocked actions.
The shipped slices moved it to 1,562 actions, 2,503 reachable items, 97 orphan
inputs, and 100 blocked actions.

No unblocked, settled acquisition implementation remains in this queue. The last
untested candidate, Curly root, is blocked by missing Jadinko Lair integration.
The dominant structural blocker is the production quest-action emitter gap: the
live quest registry has 196 playable entries, and 185 are directly uncompletable
because their `required_actions` have no emitter; prerequisite closure raises the
approximate impact to 190 of 196. These emitter-less routes are inert for an
ordinary player progressing from level one. The single unblocking action is to
implement and verify the production emitter mechanism, which would make each
quest-gated route testable from an actually reachable player state.

## Verified complete

| Entry | State | Evidence |
| --- | --- | --- |
| Polar kebbit quota route | Verified complete in `baca063f` | Ordinary tracking is available from Hunter 1; the separate quota-ticket purchase remains Hunter 70. |
| Shadow vine | Verified complete in `16375023` | Shadow jadinko tracking yields the fixed primary drop. |
| Corrupt vine | Verified complete in `16375023` | Diseased jadinko tracking yields the fixed primary drop. |
| Plant teeth | Verified complete in `16375023` | Cannibal jadinko trapping yields the fixed primary drop. |
| Guthix vine | Verified complete in `16375023` | Guthix jadinko trapping yields the fixed primary drop. |
| Dragon arrowtips | Verified complete in `a08827aa` | Looting a filled Dragon impling jar supplies the component. |
| Dragon dart tip | Verified complete in `a08827aa` | Looting a filled Dragon impling jar supplies the component. |
| Amulet of glory | Verified complete in `a08827aa` | The same source-enumerated jar table makes the item reachable. |
| Magic seed | Verified complete route in `a08827aa` | The jar table delivers it; it already had another route, so the reachable-item count does not increase for this row. |
| Summer pie | Verified complete route in `a08827aa` | The jar table delivers it; it already had another route, so the reachable-item count does not increase for this row. |
| Dragon bolt tips | Verified registered jar reward in `a08827aa` | The correctness pass restored this source-backed reward; it already had another route. |
| Dragonstone ammy | Verified registered jar reward in `a08827aa` | The correctness pass restored this source-backed reward; it already had another route. |
| Death tiara | Verified registered jar reward in `a08827aa` | The correctness pass restored this source-backed reward; it already had another route. |

The Dragon-jar rows answer two distinct questions. The five acquisition-queue
items newly routed through the jar are Dragon arrowtips, Dragon dart tip, Amulet
of glory, Magic seed, and Summer pie. Separately, the correctness pass restored
the registered Dragon bolt tips, Dragonstone ammy, and Death tiara rewards; they
were already reachable elsewhere and therefore did not change the graph totals.

The four Jadinko routes moved 1,556 / 2,493 / 103 / 102 to
1,560 / 2,497 / 99 / 102. Polar kebbit then moved the graph to
1,561 / 2,498 / 99 / 102. The Dragon-jar action moved it to
1,562 / 2,503 / 97 / 100.

## Farming guide rebuild

The withdrawn Farming skill-guide projection from `e0e8871a` has been rebuilt from
the period client's enum-5463 spine rather than inferred from internal crop data.
All 110 structs are pinned with their cache labels, levels, param-2213 icon
references, guide keys, and categories. The product renders the 88 non-Dungeoneering
rows in five sections; the 22 Dungeoneering structs remain source-pinned but are
not rendered. This deliberately departs from the period client's Milestones-first
single-category view by showing Milestones, Produce, Trees, Special, and Other
together.

Level requirements remain separate from quest and cross-skill gates. A further
17 rows carry the distinct `Not implemented in AnkiScape` lock: 12 resolved crop
rows whose mechanics are not runnable, the catalogued-only Scroll of life reward,
and four period rows whose owning mechanic is unresolved. These rows stay visible
because period membership does not depend
on implementation availability. Registry matches share one availability contract:
each resolution returns its owning target, and the guide asks the common predicate
whether that target is implemented. Crop targets map `runnable` into the contract;
Dungeoneering rewards map `fully_functional`; patch, Livid Farm, Evil Tree, Bork,
and skillcape targets are available when their live owning target exists.

The rebuild also established that resolution aliases must identify the entity
described by the guide row, not merely the closest matching name; the
second-spirit-tree unlock therefore resolves against the secondary spirit-tree
patch rather than the ordinary Spirit tree crop.

The 88 rendered rows require 82 distinct param-2213 icon IDs. A guide-only explicit
mapping resolves 73 IDs against existing canonical storage keys; nine IDs have no
semantically correct registered sprite and render with a neutral missing-asset
marker: `18336`, `20704`, `22494`, `18778`, `18779`, `18780`, `18781`, `14667`,
and `9810`. These nine are an asset-acquisition gap. No closest-name substitute
exists for any of them.

## Blocked queue

The blocker types are the queue's operational categories: **owner**, **source**,
**dependency**, **integration**, and **quota**. No listed entry is quota-blocked.
A blocker records what this investigation could not establish; it does not prove
that an unestablished source or route does not exist.

| Entry | Classification | Specific blocker |
| --- | --- | --- |
| Bush snake | Blocked — dependency | The authentic Snake-hide producer is inside Tai Bwo Wannai Cleanup. That route needs Jungle Potion and Druidic Ritual progression, and the production quest runtime cannot emit their required stage actions. |
| Fresh crab claw and Fresh crab shell | Blocked — dependency | Period sources identify the distinct Crab NPC producer, but its combat route requires partial `recipe_for_disaster_freeing_pirate_pete`; all three stage actions lack emitters. |
| Raw chompy | Blocked — dependency | Oldid `6286360` says the ability to hunt chompies is unlocked during Big Chompy Bird Hunting and that Chompy bird drops quantity `1`, rarity `Always`. The quest has three required actions and zero emitters; this branch also has no Chompy producer framework. |
| Snake hide | Blocked — dependency | Bush snakes drop it `Always`, quantity `1–5` (`Snake hide` oldid `6009794`; `Bush snake` oldid `6352282`), but the Tai Bwo Wannai Cleanup route is inaccessible through the emitter-blocked Jungle Potion and Druidic Ritual chain. |
| Chain link mould | Blocked — dependency | Oldid `5813414` says it is obtained during Legacy of Seergaze or replaced from the Myreque Hideout crate. Legacy of Seergaze has eight required actions and zero emitters. |
| Conductor mould | Blocked — dependency | Oldid `5606711` says it is obtained by cleaning Fenkenstrain Castle's upstairs fireplace during Creature of Fenkenstrain. That quest has five required actions and zero emitters. |
| Demonic sigil mould | Blocked — dependency | Oldid `5504638` says Jennifer supplies it for Shadow of the Storm. That quest has five required actions and zero emitters. |
| Rod clay mould | Blocked — dependency | Oldid `4567285` says the player makes it on Ivandis' tomb during In Aid of the Myreque. That quest has eight required actions and zero emitters. |
| Orb of armadyl | Blocked — dependency | Oldid `6504411` says one orb is made from 100 Shards of armadyl. Shards require the post–Ritual of the Mahjarrat glacor route, while this branch has neither a glacor producer nor the combination action; Ritual of the Mahjarrat itself has nine required actions and zero emitters. |
| Emerald lens | Blocked — owner | This is assigned to the parallel Darkan quest thread. Oldids `6202817` and `6569662` place the non-tradeable grant at Lunar Diplomacy's Cabin Boy ship-investigation checkpoint. Do not add a generic source; `memory-bank/codex-briefs/darkan-quest-handoff-emerald-lens-2026-08-09.md` owns the integration. |
| Inferno adze | Blocked — dependency | Oldid `6564688` requires All Fired Up completion, all fourteen beacons alight, 92 Firemaking, and additional quest, skill, and repair gates. This branch has no beacon-network producer, and All Fired Up, Land of the Goblins, and Troll Stronghold all stop on un-emitted actions. The item is integrated as a Mining/Woodcutting tool, but acquisition is not. |
| Spirit roots | Blocked — source | No obtainable producer has been established for this queue. The Farming dossier supports only the narrower conclusion that Spirit roots are distinct from ordinary roots and must not be inferred from spirit-tree harvesting; it does not establish that no qualified pre-EOC producer exists. |
| White tree sapling | Blocked — dependency | Oldid `6084594` identifies it as a Garden of Tranquillity quest item grown from a White tree shoot. The live White-tree patch consumes it, but the quest has nine required actions and zero emitters, and no shoot-to-sapling producer exists outside that progression. |
| Cursed magic logs | Blocked — dependency | Oldid `5742321` says Spirit of Summer completion is required to access the Spirit Realm tree. Spirit of Summer has five required actions and zero emitters; the target-local realm behavior cannot replace the missing prerequisite. |
| Magic essence (2) | Blocked — dependency | `Herblore:finished_magic_essence_mix` requires the exact two-dose identity. Oldid `6317371` places Starflower and Gorak-claw-powder acquisition on Fairy Ring dimensions during A Fairy Tale II. The mix identity is fixed, but the actual potion inputs remain inaccessible because A Fairy Tale II has five required actions and zero emitters and this branch has no Starflower acquisition route. |
| Shrunk ogleroot | Blocked — owner | Oldid `5936336` places the item in Grim Tales, from the piano/root-pile route or Experiment No. 2 after first potion use; the drop is quantity `1`, rarity `Always`. Quest stages, recovery, and acquisition remain Darkan quest-thread owned, and Grim Tales has five required actions and zero emitters here. |
| Relicym's balm (2) | Blocked — dependency | `Herblore:finished_relicyms_mix` requires the exact two-dose identity; base `Relicym's balm` is reachable and is not the blocked item. Oldid `6324779` requires Zogre Flesh Eaters progress until Sithik Ints teaches the recipe. Uglug Nar opens only after the player already supplies a 3- or 4-dose balm, so the shop does not independently establish the required two-dose route while Zogre Flesh Eaters' six actions remain un-emitted. |
| Skewer stick | Blocked — integration | No live source produces the root. A correct route needs the period thatching-spar producer, and `Utility:skewer_spider_on_a_stick` currently consumes the stick permanently instead of returning it. |
| Spider carcass | Blocked — source | The reachable level-one Spider target drops charms only. No live shop, combat, quest, gathering, or activity source supplies a Jungle spider carcass. |
| Curly root | Blocked — integration | Oldid `6518326` says a player with Woodcutting 83 cuts and collects curly jade roots in the Jadinko Lair; collecting yields exactly `4 curly roots`. Jadinko Lair oldid `6436518` says quests are `None`, the activity requires Woodcutting 83, and first entry only requires speaking to Dotmatrix. The player gates are satisfiable, but this branch has no Jadinko-Lair or curly-jade-root producer. |
| White lily seed | Blocked — dependency | White lily seed oldid `6219558` says Wyson exchanges one Mole skin after completion of the Falador hard tasks. This branch has no Giant Mole encounter, Mole skin producer, or Wyson exchange. Falador Easy is 9 active tasks out of a fixed 12 and Falador Hard is 9/12, so shield 3 also cannot be claimed through the current diary contract. |
| Achievement-diary latent-task denominator | Blocked — owner | Claim completion counts only active tasks but compares against each tier's fixed designed total. The registry contains 107 latent rows, all with `conditions=()`, leaving 23 tiers impossible: Ardougne elite 8/12; Falador easy 9/12, hard 9/12, elite 8/12; Fremennik easy 5/12, hard 10/12; Karamja easy 7/12, hard 10/12, elite 10/12; Lumbridge beginner 2/12, easy 9/12, medium 11/12, hard 7/12; Morytania hard 11/12, elite 11/12; Seers easy 8/12, hard 11/12, elite 8/12; Varrock easy 9/12, hard 11/12, elite 11/12; Burthorpe period 17/55; Miscellaneous 33/95. Positive control: Ardougne Easy is 12 active / 12 total and Ready to Claim. Option 1 is to implement all latent task conditions and supporting mechanisms. Option 2 is to compute completion from active tasks while visibly listing missing period tasks. Lean: option 2 now, with option 1 as ordinary data-depth work; owner decision required. |

## Curly-root viability probe

`python3 tools/audit_item_reachability.py --json` reports exactly one Curly-root
orphan row:

```text
item=Curly root
kind=root
known_producers=[]
consumers=[Firemaking:curly_root]
```

It also reports exactly one unresolved consumer, `Firemaking:curly_root`, whose
only missing input is Curly root. A direct inspection of `WOODCUTTING_TARGETS`
finds zero rows producing Curly root. The same probe finds exactly one producer
for each positive control: `Eucalyptus logs -> eucalyptus` and
`Arctic pine logs -> arctic_pine`; the reachability audit attributes them to
`Woodcutting:eucalyptus` and `Woodcutting:arctic_pine`. This proves the producer
probe can find comparable live Woodcutting routes. Match counts were checked
before interpreting the result: one orphan row, one consumer row, and zero
Woodcutting producer rows.

The period route itself is well specified:

- `Curly root?oldid=6518326`: “obtained from chopping curly jade roots (83 Woodcutting required) within the Jadinko Lair”; “Collecting the roots yields 4 curly roots.”
- `Jadinko Lair?oldid=6436518`: `quests = None`; chopping and collecting jade roots each require Woodcutting 83; the main entrance is available after speaking to Dotmatrix.

Therefore Curly root is not source-blocked or quest-blocked. It is
**integration-blocked** on the absent Jadinko-Lair curly-vine Woodcutting
producer.

## Ranking-tool caveat

> **Do not read `--rank-roots` on this branch as the acquisition work queue.**

The current ranking reports Wyvern bones, five grimy herbs, several bone types,
and Emerald lens as high-leverage candidates. Wyvern bones and the five herbs
already exist on unmerged `goal/breadth-2026-08-11` /
`goal/herbs-2026-08-11`; the bone families exist on
`goal/bones-2026-08-11`; Emerald lens belongs to the parallel Darkan thread.
Until those branches merge, this branch's graph over-reports work. Reading the
ranking directly cost a wasted slice. Before selecting any candidate, compare it
with the other branches' reachability audits and ownership records.

The ranking is a synthetic graph-leverage calculation only. It does not prove an
authentic source, gate satisfiability, ownership, or absence from another branch.

## Program blocker

No unblocked, settled implementation remains after the Curly-root verdict. The
quest-action emitter gap dominates the remaining queue: 185 of 196 quests are
directly blocked and approximately 190 of 196 are blocked after prerequisite
closure. Implementing and verifying the production emitter mechanism is the one
action that would reopen the largest part of this program.

## Verification state

The acquisition implementations and informational Farming guide leave
reachability unchanged at **1,562 actions / 2,503 reachable items / 97 orphan
inputs / 100 blocked actions**. The Farming guide has separate pure mutation
proof, plain-test, and offscreen-Qt verification because it is a product surface,
not an acquisition-graph change.
