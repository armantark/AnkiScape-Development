# Rum Deal stages 1–4 source audit — 2026-09-01

## Scope

This audit replaces the four generated `Complete Rum Deal stage N objective`
requirements that blocked stages `1` through `4`. It removes preparation and
quest-supplied items that the frozen dossier does not treat as external stage
inputs, keeps Slayer gloves as the sourced stage-4 item gate, moves the Fever
spider encounter from stage `3` to stage `4`, and gives that encounter its
quest-only guaranteed body drop. It does not change the quest's generated skill
requirements, prerequisite-quest list, combat statistics, completion rewards, or
runtime code. The retained, unregistered Fever spider body adds a user-visible
Bank row under `Other`.

No placeholder value is used. The recovered Blindweed interval is exactly `4
minutes 35 seconds` and is written into the stage-2 action.

## Frozen evidence ownership

The Darkan restoration thread already harvested and froze the complete Rum Deal
dossier. This slice did not fetch, revise, or repin any source. The controlling
contract is:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/rum-deal-target-contract.json`

Its baseline world commit is
`76a472b6cae63d9ffc05628010aca4152a4e4951`, its baseline world tree is
`d3020375ba2b385823bb85f73471c2fd0e16767b`, and its verdict ceiling is exactly
`PARTIAL[source_blocked]`.

The complete pinned source set is:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/rum-deal-final-preeoc-oldid-6556008.json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/rum-deal-blindweed-final-preeoc-oldid-4361673.json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/rum-deal-fever-spider-final-preeoc-oldid-6469080.json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/rum-deal-fishbowl-net-final-preeoc-oldid-6358392.json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/rum-deal-holy-wrench-final-preeoc-oldid-6518059.json`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/sources/rum-deal-transcript-history.json`

The transcript-history record confirms that neither candidate transcript has a
pre-cutoff revision. The earliest full transcript is comparator-only, so this
slice makes no verbatim dialogue or presentation claim.

## Read-only executable corroboration

A mixed-extension search under the read-only Darkan quest tree found the Rum
Deal implementation in Kotlin rather than assuming every quest uses Java:

- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/rum_deal/RumDeal.kt`
- `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/quests/rum_deal/RumDealState.kt`

`RumDeal.kt` orders the route from Blindweed assignment through stagnant water,
five sea creatures, wrench blessing, the owned Evil spirit, the Fever spider
body, swill delivery, and completion. It also enforces at least `470` current
Prayer points without draining them, gives the Fever spider body only during the
required quest state, and applies exactly the three `7,000` XP rewards.

## Stage mapping

The frozen contract's `quest_route` fields and the pinned route's four journal
segments map as follows:

| AnkiScape stage | Frozen route segment | Source-backed action | Mandatory fight |
| ---: | --- | --- | --- |
| `1` | Pirate Pete acceptance, island transport, Captain Braindeath briefing, farming-tool recovery, and Blindweed planting | Accept Pirate Pete's offer, reach Braindeath Island, receive the Blindweed seed, and rake and plant the surviving patch. | None |
| `2` | Dated Blindweed growth, harvest and hopper hand-in, followed by the stagnant-water route and hopper hand-in | Wait 4 minutes 35 seconds, harvest the Blindweed, add it to the hopper, then collect and add stagnant water. | None |
| `3` | Fishbowl-and-net grant, five sea creatures, pressure barrel and lever, wrench grant and blessing, then the possessed controls | Catch and pressurise five sea creatures, bless the wrench with at least 470 current Prayer points without draining them, then defeat the Evil spirit. | Evil spirit level `150` |
| `4` | Fever spider body, hopper hand-in, output tap, swill delivery to Captain Donnie, and final report | Defeat a Fever spider while wearing Slayer gloves, add its body to the hopper, give the swill to Captain Donnie, and report to Captain Braindeath. | Fever spider level `49` |

The assembled catalog contains exactly four requirement rows with the stage set
`{1, 2, 3, 4}`. The Evil spirit remains on stage `3`; the Fever spider moves to
stage `4`, whose action text is the first stage that tells the player to kill it.

## Item-gate reconciliation

The generated stage-1 row mixed mandatory, optional, and quest-supplied items.
The cleanup removes these external blockers:

- `Armour` and `Food` are generic combat preparation, not exact item identities;
- `Seed dibber` and `Rake` are available from the quest cupboard;
- `Ectophial`, `Relicym's balm`, and `Ring of charos` are optional convenience or mitigation suggestions;
- `Bucket` is supplied by Captain Braindeath if missing.

`Slayer gloves` remain mandatory but move from stage `1` to stage `4`, where the
Fever spider route requires them. The equipment-aware `required_tools` gate
accepts carried or equipped gloves; the sourced action still records that the
player wears them for the fight. The pure-flow test proves that stage `4`
refuses to resolve without the item and permits the fight when it is equipped.
The quest-level Prayer `47` gate is also exercised before the quest starts. The
more precise `470` current-Prayer-point blessing condition is preserved in the
sourced action text; the generic quest-stage requirement model has no
current-resource predicate.

`tests/test_quest_catalog.py` expands its Rum Deal forbidden generated-blocker
set from only `Armour` and `Food` to the full source-excluded set: `Seed dibber`,
`Rake`, `Bucket`, `Ectophial`, `Relicym's balm`, and `Ring of charos`. This is not
a weakened expectation. The test continues to reject those values anywhere in
Rum Deal's assembled stage inventory, while the focused contract test separately
requires the exact equipment-aware stage tool gate `stage 4 -> Slayer gloves x1`.
Together, the tests reject both stale generated preparation gates and an
accidental removal or relocation of the mandatory gloves gate.

## Encounters and guaranteed drops

The frozen contract states that the Evil spirit is an owner-scoped progression
fight and promises no item drop. Its `guaranteed_drops` therefore remains empty.

The frozen contract and focused Fever-spider dossier state that a player-credited
Fever spider kill during the required stage yields exactly one `Fever spider
body`. The stage-4 encounter now carries:

- `Fever spider body ×1`.

The pure-flow and real review-answer tests pin the body at quest completion. This
retained residue contradicts the frozen contract's `quest_route.fever_spider`
line, which says the hopper consumes the body once. The unregistered inventory
key appears permanently in the Bank's `Other` category without an icon, value,
or sell action. It is not registered in the global reachability graph, so the
graph does not credit it as a route. Registration and a post-combat hand-in
boundary remain a separate item-model slice, not reasons to omit the sourced
drop or hide its current residue.

A shown-dialog offscreen Bank check after full Rum Deal completion confirms the
blank-icon `×1` cell under `Other` and the full selected title `Fever spider body
×1`. At `1280×752`, the Bank has no horizontal overflow. At `900×560`, the body
cell, title, and metadata remain visible without ellipses, while the outer Bank
surface has a `132`-point horizontal range and clips the right-side action
buttons until the player scrolls. The item-grid scrollbar itself remains at
maximum `0` in both sizes.

## Completion rewards

The frozen contract states that completion grants exactly:

- `2` quest points;
- `7,000` Farming XP;
- `7,000` Fishing XP;
- `7,000` Prayer XP;
- retained `Holy wrench`;
- retained `Fishbowl and net`;
- Braindeath Island access;
- Cabin Fever eligibility.

The two Squeal of Fortune spins are explicitly excluded. The assembled catalog
already matched the sourced XP and retained-item rewards, so this slice does not
replace or broaden them. Focused tests pin all three XP rows and both item
rewards, and verify that Slayer XP remains zero.

## Sentinel translation and test oracle

Each cleanup row removes its exact generated sentinel through
`remove_required_actions` and adds one same-stage automatic action. Removing the
sentinel is essential because automatic actions are recorded only after the
current stage has passed its blockers.

The focused action oracle is a literal transcription of the frozen contract's
`quest_route` fields, grouped by the pinned four-stage journal. The test names
`/Users/ArmanTarkhanian1/Documents/2012scape with bots/memory-bank/audit/evidence/static/rum-deal-target-contract.json`
and does not derive expected actions from the cleanup table under test. Unit
coverage pins row count, stage set, source paths, inventory gates, encounter
placement, drops, XP, and rewards. Pure integration coverage exercises the
Prayer level gate, Slayer-gloves item gate, both fights, action proofs, drops,
and completion. The end-to-end test reads the dynamically loaded add-on's own
catalog, asserts both row count and stage set, and drives `on_answer_card()`
through completion.

## Reachability measurement

The baseline and result were both measured from this branch's parent and working
tree respectively.

| Measure | Before | After |
| --- | ---: | ---: |
| `action_count` | `1663` | `1663` |
| `reachable_item_count` | `2302` | `2304` |
| `orphan_input_count` | `165` | `165` |
| `root_orphan_count` | `32` | `32` |
| `cascade_orphan_count` | `133` | `133` |
| `unresolved_action_count` | `252` | `252` |
| `seed_item_count` | `1217` | `1219` |
| blocked quest-stage rows | `138` | `137` |
| `completable_quest_count` | `52` | `53` |

Before the repair, `rum_deal` had one blocked row at stage `1`, missing the stage
sentinel plus `Ectophial`, `Relicym's balm`, and `Ring of charos`. After the
repair, it has no blocked row. The only newly reachable registered items are
`Fishbowl and net` and `Holy wrench`, both through `quest:rum_deal`. Rum Deal is
the one newly completable quest. No descendant count is attributed to this
slice.

## Follow-on leads

The frozen contract requires completed `Priest in Peril` and `Zogre Flesh
Eaters`, but the generated AnkiScape quest start contract currently lists no
prerequisite quests. Correcting that start contract is separate from replacing
the four stage sentinels.

The quest-local custody chain remains represented by source-backed stage actions
rather than distinct global acquisition nodes. Exact item leads are `Blindweed
seed`, `Blindweed`, `Stagnant water`, `Sluglings`, `Karamthulhu`, `Wrench`, and
`Unsanitary swill`. `Fever spider body` additionally needs global item
registration and a post-combat hand-in boundary before its verified drop and
hopper consumption can both be represented in the graph and pure flow.

The current-resource condition of at least `470` Prayer points without drain and
the equipment-only distinction for worn Slayer gloves are not expressible by
the generic stage requirement schema. They remain exact contract leads rather
than being approximated by new hardcoded action gates.
