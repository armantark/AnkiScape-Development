# Fly fishing rod value contract — 2026-10-17

Status: backend implementation recorded below; promotion remains with Root. Base: `3c1f481e51a015432a52a3b1b5b2c205e8d0d2a7`.
Cutoff: `2012-11-20T00:00:00Z`. Backend scope only.
Preserve the current storage key, interface, icons, reward quantities and review rates.
Root owns promotion, native verification and peer notices.

## Required result

The base live ordinary `Fly fishing rod` row is source ID309, tradeable=true and stackable=false; those flags are correct.
Its live store/cache value is50, which also makes its GE catalog low/high alchemy values20/30.
The period ordinary item has value5, low alchemy2 and high alchemy3. Correct those three values.
Preserve its existing GE guide price20, buy limit100, tradeability, stackability and source ID309.

## Period evidence

Reuse [Fly fishing rod oldid 6104930](https://runescape.wiki/w/Special:PermanentLink/6104930), `2012-08-17T22:43:21Z`, non-beta and the latest revision before the cutoff.
The literal infobox states `tradeable = Yes`, `stackable = No`, `high = 3` and `low = 2`.
Packet: `/Users/armantarkhanian/Documents/2012scape with bots/memory-bank/audit/sources/fly-fishing-rod-source951-oldid-6104930-20261017.json`.
Accepted response SHA-256: `9cde558341aa2804ccf2a3b6da2f30df6b55f352ee0ca589e94cee596cc2e60e`.
The page discusses ordinary and Daemonheim rods sharing a name and appearance. Shared names do not establish shared values or GE eligibility.

## Exact identity and implementation

Both dated caches distinguish these unnoted items:

| ID | State | Value | Stackable | Exchangeable |
| --- | --- | --- | --- | --- |
| 309 | Ordinary rod; Add-to-toolbelt | 5 | false | true |
| 17794 | Daemonheim rod; Add-to-toolbelt | 50 | false | false |

Exact noted twins310 and17795 were queried separately; no noted storage key exists.
The current `tools/gen_item_values.py` keeps the maximum value across repeated names. Its generated `Fly fishing rod` value50 therefore selects the Daemonheim value for the ordinary live row.
The existing GE price provenance independently binds ordinary ID309 to cache_value5.

1. Make the ordinary live storage key resolve to store/cache value5 through `data/item_values.py` and its owning generated input, without applying the Daemonheim value to it.
2. Require the real `GE_ITEM_CATALOG` row for source ID309 to expose cache_value5, low_alchemy_value2 and high_alchemy_value3.
3. Preserve guide price20 from Exchange oldid `6561944`, `2012-11-16T03:33:03Z`, and limit100 from Calculator oldid `6457777`, `2012-10-23T03:28:03Z`, already accepted in `data/grand_exchange_period_source.json`.

Do not add a Daemonheim inventory key or a second GE row. Do not change shop sale prices, unrelated duplicate names, catalog entries or exact count assertions.
This contract corrects an ordinary-item value collision; the rod's tradeability and GE eligibility already match.

## Evidence boundary

Rev727 is dated `2012-07-24`; rev742 is dated `2012-11-07`. Accepted cache inputs are reused without a new archive validation.
Exact flags: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-10/cache-727-exact.txt` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-10/cache-742-exact.txt`.
Exact-ID values: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-10/cache-727-values.json` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-10/cache-742-values.json`.
Readers: `tools/OpenRs2CacheItemSearch.java` and `tools/DumpDarkanItemValues.java`; commands and exits are retained in `cache-query-receipts.json` and `value-query-receipts.json` in that external directory.
No new Exchange query or missing-title inference is used. The page supplies direct tradeability and alchemy values; the client rows independently supply value, stackability and GE eligibility.

## Verification

Run `python3 run_tests.py` and the standing documentation, test-quality, item-reachability, worktree and diff audits.
Root runs both full lanes on the merged commit through the promotion gate.
Check the real registered ordinary rod's value and GE alchemy amounts, with its retained price and limit. Check an existing value consumer and the generated-data repeatability requirement.
Add behavior coverage only for a real gap. Native proof and gameplay acceptance remain with Root.

## Implementation and consumer check — 2026-10-17

The generator selects ordinary ID309 when the fly-fishing-rod name collides with17794. Other names keep the existing maximum-value rule. The generated rod value is5 and flows through `data/item_values.py` without a runtime override. A duplicate-order regression proves the generator retains5 in either source order.
The base static `ALCH_VALUES` and runtime `_magic_alch_values` already read shop buy price5; only the GE catalog's displayed low/high alchemy values inherited20/30 from cache value50. The real ordinary Magic review route now has explicit proof of coin payouts2/3, exact rune consumption, complete-state Undo and save/load in a temporary Anki collection, including close/reopen after each payout. Default cadence stays enabled.
Shops retain buy5/sell1. GE retains guide20/limit100 and now exposes cache5/low2/high3. Loot filtering uses high-alch3; unsafe-death ranking uses5. Mobilising Armies offers2 investment credits per rod. Shattered Heart checks tradeability rather than value, so the rod remains replaceable while the three corrected nests are excluded.
The value consumers are `logic/inventory_pure.py`, `runtime/runtime_actions_combat.py`, `logic_pure/logic_pure_combat_model.py`, `logic/mobilising_armies_logic.py`, `data/grand_exchange_data.py` and the item-value exports; static/runtime Magic, shop pricing and Shattered Heart are independent consumers checked by the focused regression. No shop price or unrelated duplicate name changes.
`tests/item_tradeability/test_nest_and_rod_contracts.py` owns the behavior proof. The original backend checkpoint kept exact guide-price1443 and buy-limit1838 pins: these corrections change values and metadata, not the catalog census.
Branch proof and command receipts are in `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-10/implementation/`. Root owns merged promotion and native checks.

## Current-main integration — 2026-10-18

Main a8d71621641dc3e356890cbba65c5619590645e0 includes three separately qualified GE rows: Mystic hats4099/4109 and unlit Mining helmet5014. Its generated maps contain1446 guide prices and1841 buy limits. The nest/rod slice adds zero rows. Its four census assertions now use exact1446/1841 equalities; no earlier row, period value, consumer rule or measuring instrument changes. Original accepted source and native evidence remain valid for their recorded scopes.
