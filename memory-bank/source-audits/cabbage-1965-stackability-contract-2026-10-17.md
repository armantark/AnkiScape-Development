# Cabbage stackability contract — 2026-10-17

Status: qualified for backend implementation. Base: `3c1f481e51a015432a52a3b1b5b2c205e8d0d2a7`.
Cutoff: `2012-11-20T00:00:00Z`. Backend scope only.
Preserve the current storage key, interface, icons, reward quantities and review rates.
Root owns promotion, native verification and peer notices.

## Required result

The live ordinary `Cabbage` row is source ID1965, tradeable=true and stackable=true.
The period ordinary item is tradeable=true and stackable=false. Correct stackability only.
Preserve store/cache value1, GE guide price56, buy limit1000 and GE low/high alchemy0/0.

## Period evidence

Reuse [Cabbage oldid 5743345](https://runescape.wiki/w/Special:PermanentLink/5743345), `2012-06-11T11:16:48Z`, the retained non-beta revision.
The literal item infobox states `tradeable = Yes`, `stackable = No`, `high = 0` and `low = 0`.
Packet: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-10/cabbage-oldid-5743345.json`.
Accepted response SHA-256: `8abaa3ad6f31008aeb27a3d0182100c3290dce80853e7eee45cfec05b364bf84`.
This existing Harvest10 pin was read without fetching or re-hashing it.

The latest revision before the cutoff is [Cabbage oldid 6174079](https://runescape.wiki/w/Special:PermanentLink/6174079), `2012-08-31T23:11:02Z`.
It is beta-marked and agrees on these flags and alchemy values; use it as temporal corroboration only.
Packet: `/Users/armantarkhanian/Documents/2012scape with bots/memory-bank/audit/sources/cabbage-source981-oldid-6174079-20261017.json`.
Accepted response SHA-256: `d5e566800ad43afdf3964d12b1a3dd6025d7bc792ade17ea24b3fe995705209e`.
No new wiki fetch is needed for this family. No transcluded template value supplies the corrected flag.

## Exact identity and implementation

Rev727 and rev742 distinguish these exact client identities:

| ID | State | Stackable | Exchangeable | Options |
| --- | --- | --- | --- | --- |
| 1965 | Ordinary unnoted Cabbage | false | true | Eat, drop |
| 1966 | Ordinary noted Cabbage | true | true | drop |
| 1967 | Draynor Manor unnoted Cabbage | false | false | Eat, drop |
| 1968 | Draynor Manor noted definition | true | false | drop |

Both unnoted IDs have value1. The existing `Cabbage` registry explicitly binds1965.
Do not apply the Draynor Manor GE exclusion or its separate food effect to this storage key.
`data/cooking_data.py` owns the ordinary metadata: `SOURCE_ITEM_DATA` maps `Cabbage` to `(1965, True)`, where the boolean means tradeability.
Its `cooking_extra_items_as_dict()` emits `stackable=false` only for names in `SOURCE_NONSTACKABLE_ITEMS`; Cabbage is absent, so the registry defaults it to true.
The committed cache-derived `STACKABLE_ITEM_NAMES` already excludes Cabbage. Correct the owning metadata rather than changing the default for unrelated items.

1. Extend the existing Cooking nonstackable metadata set for the exact `Cabbage` key, with the period citation.
2. Require Cooking metadata, merged `EXTRA_ITEM_DATA` and the real registered `food_cabbage` row to retain ID1965 and tradeable=true while exposing stackable=false.
3. Preserve the current ordinary acquisition and consumers, including Farming and garden-pie preparation. Preserve existing quantities, food effects and rates.
4. Preserve the GE row, guide price56 from Exchange oldid6549629 (`2012-11-12T13:10:46Z`) and limit1000 from Calculator oldid6457777 (`2012-10-23T03:28:03Z`), already accepted in `data/grand_exchange_period_source.json`.

Do not add Draynor Manor, noted Cabbage or new inventory keys. Do not change unrelated foods, sack items, GE map entries or exact count assertions.
This contract corrects registered item metadata; it does not claim that every inventory consumer currently uses the incorrect registry flag.

## Evidence boundary

Rev727 is dated `2012-07-24`; rev742 is dated `2012-11-07`. Accepted cache inputs and Harvest10 exact-ID outputs are reused without archive validation or repeat queries.
Exact flags: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-10/cache-727-exact.txt` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-10/cache-742-exact.txt`.
Values: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-10/cache-727-values.json` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-10/cache-742-values.json`.
Readers: `tools/OpenRs2CacheItemSearch.java` and `tools/DumpDarkanItemValues.java`; exact commands and successful exits are retained in Harvest10's `cache-query-receipts.json` and `value-query-receipts.json`.
The wiki supplies direct tradeability; `canExchange()` supplies GE eligibility only. They agree for ordinary1965.
Live import evidence: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-11/live-items.json` and `checked-variants.json`.

## Verification

Run `python3 run_tests.py` and the standing documentation, test-quality, item-reachability, worktree and diff audits.
Root runs both full lanes on the merged commit through the promotion gate.
Check the real Cooking metadata and registered item, the retained GE price/limit/alchemy values and an existing ordinary producer/consumer.
Check the existing carried-capacity behavior and an old saved pack containing multiple Cabbage, preserving total ownership through save/load and review Undo.
Reuse the shared capacity/save repair where applicable; do not invent an independent migration or duplicate test machinery.
Add behavior coverage only for a real gap. This research contract does not claim implementation, native proof or gameplay acceptance.
