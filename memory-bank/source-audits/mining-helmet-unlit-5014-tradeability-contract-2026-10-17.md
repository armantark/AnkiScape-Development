# Unlit mining helmet GE contract — 2026-10-17

Status: backend implemented; branch verification recorded below. Exact ID `5014`, storage key `Mining helmet (unlit)`.
Base: `452f325d3b62c2247ad990181578c20284265f8a`. Cutoff: `2012-11-20T00:00:00Z`.
Backend scope only. This source contract changes no product code. Keep the current interface, storage keys, icons, quest rewards, levels and review quantities.
Evidence directory: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-6`. Root owns promotion, native verification and peer notices.

## Required result

Live registry: tradeable=true, but its storage key is absent from `EXCHANGEABLE_ITEM_NAMES` and the GE catalog.
The period item is tradeable and exchangeable. Preserve tradeable=true and add its exact storage key to GE.
The existing value 900 is correct. No period price, limit or provenance row exists for this storage key.

## Period evidence and variants

Reuse [Mining helmet oldid5371805](https://runescape.wiki/w/Mining_helmet?oldid=5371805), `2012-03-13T03:44:53Z`.
The page explicitly says `tradeable = Yes, if unlit` and gives distinct lit/unlit descriptions.
Darkan packet: `/Users/armantarkhanian/Documents/2012scape with bots/memory-bank/audit/sources/mining-helmet-source831-prebeta-response-20261017.json`.
Accepted response SHA-256: `e6b55200213e7299169b7e266ed174f78b5822105d0bd982878faec96b89a914` (shared ledger; reused without a new harvest).
Rev727 (`2012-07-24`) and rev742 (`2012-11-07`) each bind 5013 to Extinguish and exchangeable=false, 5014 to Light and exchangeable=true, and 5015 to the stackable note and exchangeable=true.
Reuse exact probes: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-5/cache-727-exact.txt` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-5/cache-742-exact.txt`.
Reader: `tools/OpenRs2CacheItemSearch.java`, Darkan `ItemDefinitions.canExchange()`. The cache flag proves GE eligibility; the item page supplies direct tradeability.

## Exact Exchange price and limit

Exchange price: exists. [Exchange:Mining helmet oldid 6562665](https://runescape.wiki/w/Exchange:Mining_helmet?oldid=6562665), `2012-11-16T04:22:07Z`, latest revision returned on or before the cutoff.
Literal fields: `Item=Mining helmet`, `ItemId=5014`, `Price=466`, `Value=900`, `Limit=100`.
Literal price date: `04:21, November 16, 2012 (UTC)`; do not substitute the revision timestamp.
Retained complete API response: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-6/exchange-mining-helmet.json`.
Response SHA-256: `44ebf16db86097aebc818fe499fe4bb0ee21bf86cce7dee5726395dc20c6b851`. Literal body SHA-256: `09f060af68aec866a8f39c04c01e03f7b632c1f607bddb43efd9e7a53087fbd1`.
Calculator row: exists. [Calculator:Grand Exchange buying limits oldid 6457777](https://runescape.wiki/w/Calculator:Grand_Exchange_buying_limits?oldid=6457777), `2012-10-23T03:28:03Z`, literal `Exchange:Mining helmet` → 100.
Reused calculator packet: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/harvest-merge-bound-source-2026-10-15/remaining-priority-items/raw/reused-global-buy-limits-oldid-6457777.json`; body line 5603 and next line bind the pair.
The title resolves directly and its dated ItemId matches 5014; no missing-title inference is used.

## Implementation and verification

1. Add exact key `Mining helmet (unlit)` to the exchangeable set in the existing `data/item_values.py` table build. Preserve value 900. Do not alias all Mining helmet states.
2. Add this storage key to `data/grand_exchange_period_source.json`: price 466, limit 100, page_title `Exchange:Mining helmet`, oldid 6562665, timestamp `2012-11-16T04:22:07Z`, price_date `04:21, November 16, 2012 (UTC)`, page_item `Mining helmet`, item_id 5014, cache_value 900, page_limit 100.
3. Run `python3 tools/generate_ge_period_data.py generated/grand_exchange_period_generated.py` without `--harvest`.
4. Increase each existing exact price/limit equality by one: base 1443/1838 becomes 1444/1839 for this contract alone. Re-measure after integration with parallel slices; retain exact equalities.
5. Require the real GE row to report source ID 5014, guide price 466, limit 100 and the exact provenance above. Keep lit 5013 absent from GE and do not register note 5015 separately.
6. Drive the existing earned helmet/light/extinguish route, GE offer Undo, escrow, settlement, collection and save/reload. Check review Undo and quantities; no new UI.

Run `python3 run_tests.py` and the standing documentation, test-quality, reachability, worktree and diff audits. Root runs both full promotion lanes.
Use the real item registry and catalog. Do not stub either. Add behavior coverage only where existing coverage has a real gap.
This contract claims no native proof or gameplay acceptance.

## Implementation — 2026-10-17
The exact storage key enters the exchangeable set. The committed source row retains every pinned Exchange field, including price 466, limit 100 and literal price date. Offline generator: `python3 tools/generate_ge_period_data.py generated/grand_exchange_period_generated.py`; no harvest.
Exact price/limit equalities increase from 1443/1838 to 1444/1839 solely for 5014. The lit state and note 5015 receive no period row.
The kernel proof covers buy escrow and offer Undo, collection, light/extinguish reviews and review Undo, sell escrow, settlement, collection and complete-state save/reload. The deterministic market pays 482 coins on the one-item sale at submitted price 466; the real Shop controls sell one unlit helmet for the existing price 270 coins. Neither simulation price is a new historical price pin.
Native verification and exact merged promotion lanes remain Root-owned; no existing UI changed.

Final focused proof: `tests.item_tradeability.test_mining_helmet_rat_pole` and `tests.skills.test_summoning_market` pass 8 plain tests. These modules, the Shop proof `tests.item_tradeability.test_helmet_rat_pole_shop` and `tests.test_grand_exchange_data` pass 25 offscreen Qt tests with zero skips. All listed audits exit 0. Full plain output and the final commit are recorded in `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-6/report.md`.
