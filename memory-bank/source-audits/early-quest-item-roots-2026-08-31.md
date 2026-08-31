# Early quest item roots audit — 2026-08-31

## Scope and verdict

This slice repairs the acquisition roots that made existing early-quest item
chains appear route-less. It does not duplicate any downstream quest producer.

**Verdict:** the live graph now accepts canonical `Karamjan rum`, registers and
produces `Ugthanki dung`, traverses the existing Agility Pyramid stage output,
and opens karambwan fishing plus Tiadeche's stock when Tai Bwo Wannai Trio is
started. `Fish food` and `Insect repellent` also have their ordinary sourced
world routes. All six affected item identities resolve through live runtime or
shop contracts.

## Period evidence

| Item or rule | Pinned revision | UTC timestamp | Period fact used |
| --- | ---: | --- | --- |
| Karamjan rum | `6552630` | `2012-11-13T22:37:26Z` | Canonical name; sold by Karamja Wines, Spirits, and Beers for 30 coins. |
| Ugthanki dung | `6288566` | `2012-09-24T05:31:50Z` | Red hot sauce is used on the trough, the camel drops dung, and a bucket collects it. |
| Agility Pyramid | `6457748` | `2012-10-23T02:32:50Z` | The course route is period-backed. |
| Pyramid top | `5992470` | pre-cutoff pin in the Agility inventory audit | One item is retrieved per completed ascent. |
| Raw karambwan | `6096116` | `2012-08-15T22:31:42Z` | Catching requires Tai Bwo Wannai Trio to be started, not completed; Tiadeche sells the fish for 440 coins. |
| Fish food | `6358390` | `2012-10-06T20:16:07Z` | Found in Draynor Manor. |
| Insect repellent | `5865450` | `2012-06-30T12:20:35Z` | Found on a table north of Catherby bank. |

The existing Agility source records remain
`memory-bank/source-audits/agility-tables-2026-07-13.md` and
`memory-bank/source-audits/agility-complete-content-inventory-2026-07-15.md`.
No Agility obstacle order, fail-rate, or payout value changed in this slice.

## Darkan corroboration

The read-only Darkan checkout was inspected at
`6277992980582f7b3da3a48e722e96cfa5b0a57d`.

- `src/main/java/com/rs/game/content/quests/the_feud/TheFeud.kt:49-50`
  declares `UGTHANKI_DUNG = 4601` and the green duplicate `4602`.
- `TheFeud.kt:603-631` consumes red hot sauce at the trough, uses the bounded
  green/brown attempt sequence, requires an empty bucket, and exchanges that
  bucket for item `4601`.
- `src/main/java/com/rs/game/content/quests/ernestthechicken/ErnestTheChicken.java:63-70`
  declares Fish food as item `272`.
- `data/items/spawns/spawns.json:189-210` places Fish food in Draynor Manor.
- `src/main/java/com/rs/game/content/world/areas/catherby/npcs/Beekeeper.java:29-36`
  hands the player one Insect repellent, item `28`.

The live acquisition rows are in
`data/quest_item_acquisition_data.py:8-79`. `Ugthanki dung` is registered as
unstackable and untradeable item `4601`. Its Utility action consumes one Bucket
and is gated on The Feud being started. The target-unlock contract cannot
express the exact `POISON_INGREDIENTS` progress stage, so `started` is the least
permissive live gate that keeps the sourced route reachable; the action abstracts
the sauce, trough, camel, and bounded retry inside one review. Fish food and
Insect repellent are zero-input world-collection reviews. No invented probability
is used.

## Defect three measurement: Agility output traversal

Before this slice, `tools/audit_item_reachability.py` enumerated fourteen action
families but omitted Agility. `_outputs()` already understood `output_item`; the
Agility data was never passed to it.

The complete Agility target surface contains exactly one stage with a positive
item output: `agility_pyramid:retrieve_top` produces one `Pyramid top` at
`data/agility_data.py:218-223`. The new adapter at
`data/agility_data.py:328-341` exposes stage outputs through the same action
shape as other skills, and the audit consumes it at
`tools/audit_item_reachability.py:1322-1338`.

Therefore the audit omission affected exactly one modelled Agility stage output:
`Pyramid top`. Nineteen other names in `AGILITY_REWARD_ITEMS` still have no
Agility stage producer; they were already outside this defect and remain
unchanged.

## Defect four measurement: started versus completed

The old `QuestUnlockRule` for `catch_karambwan` was translated to
`kind="quest_completed"` by `_quest_target_unlock_rule`. Tiadeche's generated
shop access row also used `stage="completed"`. Both contradicted the period
source and preserved the stage-2 circularity.

The target rule now uses `kind="quest_started"` at
`data/quest_data.py:11104-11106`. The generator-owned shop rule now uses
`stage="started"` at `tools/generate_npc_shop_data.py:396-397`, and the checked-in
`data/shop_data.py` row matches it. Runtime and audit machinery already support
both started states; no gate resolver changed.

The read-only Darkan server is more specific: `Fishing.java:163-171` requires a
mid-quest knowledge flag and the active quest spot, while
`TaiBwoWannaiTrio.kt:54-60` describes brother-shop access as a post-quest reward.
That timing conflicts with the pinned period page and the explicit period ruling
for this slice. AnkiScape follows the pinned `STARTED` rule. The shop change is
also load-bearing for the live product: Tiadeche's stall is the only modelled
route to a Karambwan vessel and supplies the direct 440-coin Raw karambwan route.

## Canonical rum predicate

`data/quest_data.py:1359-1364,7642-7650` now uses `Karamjan rum` in the Pirate's
Treasure journal, consumed inventory, description, and auto action. The item
registry and shop row were already canonical and were not renamed. The real
review-answer product-flow test buys item `431` from the existing shop and
completes all three quest reviews.

## Reachability result

The report was measured from `tools/audit_item_reachability.py --json` on
rebased main and on the merged slice; neither side's old pin was reused.

| Audit pin | Before | After |
| --- | ---: | ---: |
| `action_count` | 1659 | 1663 |
| `reachable_item_count` | 2270 | 2301 |
| `orphan_input_count` | 167 | 165 |
| `root_orphan_count` | 32 | 32 |
| `cascade_orphan_count` | 135 | 133 |
| `unresolved_action_count` | 256 | 252 |
| `seed_item_count` | 1182 | 1215 |
| blocked quest-stage rows | 143 | 139 |

The four new actions are three Utility acquisitions and one Agility stage
output. The large seed increase comes from the newly reachable quest closure
and the started Tiadeche shop, not from hand-seeding quest products.

### Items that gained routes

Thirty-one item names were absent from the before route map and present after.

- Direct or adjacent economy routes: `Dragon battleaxe`, `Dragon mace`, `Fish food`,
  `Insect repellent`, `Karambwan vessel`, `Mystic fire staff`, `Poison karambwan`,
  `Pyramid top`, `Raw karambwan`, and `Ugthanki dung`.
- Existing quest-owned routes: `Blamish oil`, `Blamish snail slime`, `Bucket of wax`,
  `Casket (Pirate's Treasure)`, `Excalibur`, `Fire feather`, `Grail bell`,
  `Grimy key`, `Holy grail`, `Holy table napkin`, `Ice gloves`, `Id papers`,
  `Magic gold feather`, `Magic whistle`, `Oil can`, `Oily fishing rod`,
  `Pete's candlestick`, `Poisoned fish food`, `Pressure gauge`, `Rubber tube`,
  and `Thieves' armband`.

`Karamjan rum` already had the shop route before the slice. Its defect was the
quest predicate, so it does not appear in the gained-route set.

The live report gained twenty stage-product routes and one quest reward route,
which is broader than the original eighteen-item summary. The extra movement is
an honest adjacent cascade through the already-modelled Merlin's Crystal, Holy
Grail, and Heroes' Quest chains; no producer was added for any of those items.

## Newly exposed second-level blockers

Six formerly blocked first stages leave the report. Two later combat rows become
visible, so the net blocked-row change is `143 → 139` rather than `143 → 137`:

- `dealing_with_scabaras` stage 6 is blocked by combat encounter
  `dealing_with_scabaras_skeletons_1`.
- `tai_bwo_wannai_trio` stage 3 is blocked by combat encounter
  `tai_bwo_wannai_trio_monkey`.

These are combat-resolver data gaps found only after the item roots moved. They
belong to the separate systemic combat slice and were not filled with invented
stats.

The generated catalog still contains dead source-derived `Karamja rum` strings,
including the overridden Pirate's Treasure stage row and another quest's journal
prose. The live Pirate's Treasure journal and stage replacement are canonical;
regenerating unrelated catalog prose is outside this line-neutral slice.

## Coverage and visual check

`tests/test_early_quest_item_routes.py` pins all six live routes, every new
quest-owned route, item `4601`, actual Utility production, both started
karambwan gates, and a shop-to-quest end-to-end pass through `on_answer_card`.
It also drives the real `handle_agility_answer` path through all 32 Agility
Pyramid stages at level 30 and proves the final `apply_agility_review_pure`
output is credited as one `Pyramid top` in inventory. The pure function returns
outputs in its result; `runtime/runtime_actions_activities.py:3067-3076` owns
the inventory credit. The established reachability test owns the seven numeric
pins and blocked-row count.

The existing real Qt Skills-hub renderer showed all three new Utility labels at
`900×560` in dark and light palettes after `dialog.show()`, resize, and event
processing. Geometry probes reported 404-pixel rows, text widths of 96, 135, and
130 pixels, and horizontal-scroll maximum `0` for Fish food, Insect repellent,
and Ugthanki dung. Fish food and Insect repellent reuse their existing item art;
Ugthanki dung uses the consumed Bucket as its activity icon. No label was clipped
or elided, and no UI code or layout changed.
