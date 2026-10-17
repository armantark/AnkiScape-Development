# Mystic hat variants GE contract — 2026-10-17

Status: qualified for backend implementation. Base: `3c1f481e51a015432a52a3b1b5b2c205e8d0d2a7`.
Cutoff: `2012-11-20T00:00:00Z`. Backend scope only.
Preserve the current storage keys, interface, icons, equipment stats, Slayer drops and review rates.
Root owns promotion, native verification and peer notices.

## Required result

The live `Mystic hat (dark)` ID4099 and `Mystic hat (light)` ID4109 rows are tradeable=true and stackable=false, correctly.
Both are missing from `EXCHANGEABLE_ITEM_NAMES`, `ITEM_VALUES` and `GE_ITEM_CATALOG`.
Both exact period items are GE-eligible. Supply their historical prices and buy limits without merging either identity into the blue hat4089.

| Live storage key | ID | Guide price | Buy limit | Cache value |
| --- | --- | --- | --- | --- |
| Mystic hat (dark) | 4099 | 33058 | 100 | 15000 |
| Mystic hat (light) | 4109 | 8786 | 100 | 15000 |

## Period evidence

Use [Mystic hat oldid 5607613](https://runescape.wiki/w/Special:PermanentLink/5607613), `2012-05-13T16:32:55Z`, non-beta.
The literal infobox states tradeable=Yes and stackable=No and lists dark, light and blue Exchange identities.
Packet: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-9/mystic-hat-oldid-5607613.json`.
Response SHA-256: `6b1b0c20b3fc6182996e3d24ddc40bfffa388873c1631443309de4964db935f6`.
The reused batch6 oldid `6591932`, `2012-11-20T05:54:51Z`, is beta-marked and after the strict cutoff; temporal evidence only.
The complete strict-cutoff history query remains in the external `mystic-hat-history.json`; beta revisions do not replace the non-beta proof.

Use [dark Exchange oldid 6571021](https://runescape.wiki/w/Special:PermanentLink/6571021), `2012-11-18T04:43:56Z`.
The literal fields are Item=Mystic hat (dark), ItemId=4099, Price=33,058, Value=15000 and Limit=100.
Packet: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-9/exchange-dark-mystic-hat-cutoff.json`.
Response SHA-256: `fdf93f7003abea83974f677f7153f9a4f92304157696f789b07693f7b3d2029b`.
Use [light Exchange oldid 6571022](https://runescape.wiki/w/Special:PermanentLink/6571022), `2012-11-18T04:44:04Z`.
The literal fields are Item=Mystic hat (light), ItemId=4109, Price=8,786, Value=15000 and Limit=100.
Packet: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-9/exchange-light-mystic-hat-cutoff.json`.
Response SHA-256: `e668d94210b0cb313fa0a9f3e6cbd30cb9aa855d26161e5ceff1aad508975b44`.
These are the latest revisions returned before the strict cutoff for the pages now named `Exchange:Dark mystic hat` and `Exchange:Light mystic hat`.
The original Exchange title lookups returned missing; those misses were not treated as evidence of historical absence.

Reuse [Calculator oldid 6457777](https://runescape.wiki/w/Special:PermanentLink/6457777), `2012-10-23T03:28:03Z`.
Its literal table independently names both historical Exchange rows and sets each limit to100.
Accepted packet: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-14/harvest-merge-bound-source-2026-10-15/remaining-priority-items/raw/reused-global-buy-limits-oldid-6457777.json`.
This is reuse, not a new harvest or a new verification claim about accepted bytes.

## Exact identity and implementation

Rev727 (`2012-07-24`) and rev742 (`2012-11-07`) separately confirm4099 and4109 as nonstackable, exchangeable Wear items.
Their noted twins4100 and4110 are stackable. Do not assign a noted ID to a worn hat.
Blue4089, all three noted twins, lent10601–10603 and Discard variants13508/13513/13518 were queried separately; no absent inventory variant becomes a defect.

1. Add exact live-name aliases for IDs4099/4109 to the item-value and exchangeable-name authority in `data/item_values.py`, with value15000 each.
2. Add the two exact period price, limit and provenance rows to `data/grand_exchange_period_source.json`; regenerate `generated/grand_exchange_period_generated.py` through the existing generator without a broad harvest.
3. Require the real `GE_ITEM_CATALOG` to expose each existing item with its own ID, price and limit. Preserve tradeability, stackability and all existing equipment/drop metadata.
4. Preserve every pre-existing GE row. Update any affected exact census equality by exactly two rows and cite these two already registered period identities as the reason; never replace an equality with a lower bound.

The base has1858 GE rows,1443 period prices and1838 period limits, measured during qualification; on the unchanged base the resulting totals are1860,1445 and1840.
Re-measure the implementation base rather than treating these branch measurements as a promotion baseline.
The existing blue `Mystic hat`4089 price16225 and limit100 remain unchanged.

## Evidence boundary

The non-beta parent page proves player tradeability and variant taxonomy.
The exact Exchange fields prove price, item identity, cache value and page limit without rendering a template or using a modern market price.
The global period table corroborates each buy limit; both dated caches corroborate exact IDs and GE eligibility.
`ItemDefinitions.canExchange()` alone does not prove direct tradeability.
Exact cache outputs are `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-9/cache-727-exact.txt` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-9/cache-742-exact.txt`.
The reader is `tools/OpenRs2CacheItemSearch.java`; the external `query-receipts.json` records commands and exits. Accepted cache inputs are reused.
This is one family contract covering two live variant omissions, not two family defects.

## Verification

Run `python3 run_tests.py` and the standing documentation, test-quality, item-reachability, worktree and diff audits.
Root runs both full lanes on the merged commit through the promotion gate.
Check the real catalog, buy/sell offer flow, buy-limit enforcement and nonstackable capacity for both exact names; prove the blue row and existing rows remain intact.
Check save/reload and review Undo. Add behavior coverage only for a real coverage gap.
This research contract does not claim implementation, native proof or gameplay acceptance.
