# Lit mining helmet tradeability contract — 2026-10-17

Status: qualified for backend implementation. Exact ID `5013`, storage key `Mining helmet (lit)`.
Base: `452f325d3b62c2247ad990181578c20284265f8a`. Cutoff: `2012-11-20T00:00:00Z`.
Backend scope only. This source contract changes no product code. Keep the current interface, storage keys, icons, quest rewards, levels and review quantities.
Evidence directory: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-6`. Root owns promotion, native verification and peer notices.

## Required result

Live registry: `tradeable=True`; GE absent. Period: direct trade prohibited; GE prohibited.
Set only the lit state's tradeable flag to false. Keep the unlit state tradeable.

## Period evidence and variants

Reuse [Mining helmet oldid5371805](https://runescape.wiki/w/Mining_helmet?oldid=5371805), `2012-03-13T03:44:53Z`.
The page explicitly says `tradeable = Yes, if unlit` and gives distinct lit/unlit descriptions.
Darkan packet: `/Users/armantarkhanian/Documents/2012scape with bots/memory-bank/audit/sources/mining-helmet-source831-prebeta-response-20261017.json`.
Accepted response SHA-256: `e6b55200213e7299169b7e266ed174f78b5822105d0bd982878faec96b89a914` (shared ledger; reused without a new harvest).
Rev727 (`2012-07-24`) and rev742 (`2012-11-07`) each bind 5013 to Extinguish and exchangeable=false, 5014 to Light and exchangeable=true, and 5015 to the stackable note and exchangeable=true.
Reuse exact probes: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-5/cache-727-exact.txt` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-5/cache-742-exact.txt`.
Reader: `tools/OpenRs2CacheItemSearch.java`, Darkan `ItemDefinitions.canExchange()`. The cache flag proves GE eligibility; the item page supplies direct tradeability.

Exchange price and buy-limit rows: not applicable for lit 5013. Its explicit item-page exclusion and two false cache flags establish the result; this is not an inference from a missing or moved Exchange title.
No price, limit or provenance row is to be added for 5013. Keep 5015 as a source note identity, not a new AnkiScape storage item.

## Implementation and verification

1. In `data/firemaking_data.py`, set `lit_tradeable=False` on `light_mining_helmet`; retain `raw_tradeable=True`.
2. Require the real `ITEM_DEFINITIONS` row to report ID 5013, nonstackable, tradeable=false, absent from `GE_ITEM_CATALOG`.
3. Drive the existing level 65 Firemaking light/extinguish reducer with owned 5014 and Tinderbox. Lighting must return 5013; extinguishing must restore 5014. Check quantity conservation, review Undo and save/reload. No new recipe or acquisition route.
4. Keep period price and limit counts unchanged for this contract.

Run `python3 run_tests.py` and the standing documentation, test-quality, reachability, worktree and diff audits. Root runs both full promotion lanes.
Use the real item registry and catalog. Do not stub either. Add behavior coverage only where existing coverage has a real gap.
This contract claims no implementation, native proof or gameplay acceptance.
