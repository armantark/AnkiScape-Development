# Fly fishing rod value contract — 2026-10-17

Status: qualified for backend implementation. Base: `3c1f481e51a015432a52a3b1b5b2c205e8d0d2a7`.
Cutoff: `2012-11-20T00:00:00Z`. Backend scope only.
Preserve the current storage key, interface, icons, reward quantities and review rates.
Root owns promotion, native verification and peer notices.

## Required result

The live ordinary `Fly fishing rod` row is source ID309, tradeable=true and stackable=false; those flags are correct.
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
Add behavior coverage only for a real gap. This research contract does not claim implementation, native proof or gameplay acceptance.
