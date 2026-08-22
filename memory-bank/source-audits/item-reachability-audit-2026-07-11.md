# Live Item Reachability Audit — 2026-07-11

## Scope

`tools/audit_item_reachability.py` constructs a deterministic acquisition graph from the eleven live review skills, Utility/Activities, item consumption transitions, visible positive-stock shops, Combat drops, registered quest rewards, Woodcutting nest drops, and bird-nest opening transformations. It asks whether every item consumed by a live action has some current route.

This is a reachability audit, not a historical-fidelity claim. A reachable item can still have an incomplete rate, quantity, gate, or source table.

## Baseline

At 2026-07-11 HEAD:

- 1,061 executable transformations inspected.
- 1,211 distinct seed items.
- 1,679 reachable items after graph closure.
- 690 distinct consumed inputs.
- 267 orphan inputs: 136 roots with no live producer and 131 cascades whose known producer is itself blocked.
- 303 transformations remain blocked by at least one orphan input.

The JSON mode is the durable handoff surface:

```bash
python3 tools/audit_item_reachability.py --json
```

## Closed defect

Woodcutting opens seed, ring, and egg nests into item 5075, `Bird's nest (empty)`. The Utility grind action incorrectly required a generic `Bird's nest`, so the source-backed crushed-nest chain was impossible. It now consumes the empty nest, and the audit explicitly models variant nest → opened rewards plus empty nest → crushed nest.

Period implementation evidence: `game-main/plugins/src/main/kotlin/gg/rsmod/plugins/content/items/pestle_and_mortar/PestleAndMortarData.kt` maps item 5075 to `CRUSHED_NEST`.

## Remaining dependency buckets

1. **Missing skills and Farming** — crops, fruit, roots, mushrooms, Habitat herbs/vines, and several unfinished potions cannot close before Farming/Jadinko and related acquisition loops exist.
2. **Magic and activity transformations** — elemental orbs, Armadyl components, special moulds, lantern state, and other contextual item actions need their authentic skill/quest/activity owners.
3. **Deferred activities and special methods** — cave eel, living minerals, Arctic pine/eucalyptus/cursed magic logs, special fish, and minigame resources remain behind the corresponding kanban cards and stable Darkan evidence.
4. **Combat and world acquisition breadth** — dragonhides, scales, claws, horns, teeth, fungi, and other secondaries require source-audited drop, spawn, shop, or claim coverage.
5. **Potion-state plumbing** — many two-/four-dose and flask roots reveal that the global dose/decant/drink graph is not complete outside the currently supported Combat potion families. Effects and automatic use must follow the settled per-target `Use potions` policy rather than fake recipe gates.

These buckets are now explicit dependencies. They should not be “fixed” by seeding free items or inventing recipes.

## Known instrument blind spot — claim grants (2026-08-22)

`tools/audit_item_reachability.py` does not read `CLAIM_DATA` or traverse the
claim application path. It seeds shops, Combat drops, and bird nests, closes
ordinary item actions, and models quest-stage/start/completion products, but it
never adds claim outputs.

The shipped claim catalog grants 16 unique items. Eleven starter-kit items also
have non-claim routes and are counted for those routes. Five items are granted
only through claims — `Wicked hood`, `Apmeken mask`, `Ankh`, `Scabaras mask`,
and `Was` — and the audit currently counts 0 of those 5. On
`goal/ditr-hidden-2026-08-22`, the unchanged audit result is `1599 actions; 2370
reachable items; 38 orphan inputs; 37 blocked actions` even though the real
claim kernel grants all four Diamond in the Rough items.

Repair this in a dedicated instrument slice: add claim item bundles as explicit
acquisition sources/actions, preserve required-quest gating in the quest
scenarios, and add regressions proving both an unconditional claim (`Wicked
hood`) and the two quest-gated skill claims enter the route map. Re-measure every
pinned field from the repaired audit rather than adjusting counts arithmetically.

## Maintenance rule

Run the audit whenever an action family, shop, Combat drop table, quest reward, claim, or item transformation changes. The focused test protects deterministic accounting and representative routes; count growth is expected as authentic content is added.

