# Relicym's mix stackability contract — 2026-10-17

Status: qualified for backend implementation. Base: `3c1f481e51a015432a52a3b1b5b2c205e8d0d2a7`.
Cutoff: `2012-11-20T00:00:00Z`. Backend scope only.
Preserve the current storage key, interface, icons, recipe, output quantity and review rate.
Root owns promotion, native verification and peer notices.

## Required result

The live `Relicym's mix (2)` row has tradeable=true, stackable=true and source_item_id=None.
The drinkable period item is ID `11437`, tradeable=true and stackable=false.
Its existing GE row is correct: guide price `268`, buy limit `1000`, cache value `150`.
Keep that GE row and its provenance. Do not apply the stackability of the noted item to the drinkable item.

## Period evidence

Use [Relicym's mix oldid 5503026](https://runescape.wiki/w/Special:PermanentLink/5503026), `2012-04-17T11:31:31Z`, non-beta.
The literal item infobox states `tradeable = Yes` and `stackable = No`.
Packet: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-9/relicyms-mix-oldid-5503026.json`.
Response SHA-256: `c2b6b4bbe066491a94b06dc046c37dd8eaaecafe20e01c66a8608cacbbf3ec5f`.
The latest revision before the strict cutoff is oldid `6325238`, `2012-09-30T16:53:35Z`.
It is beta-marked and agrees on these flags; it supplies temporal corroboration only.
Packet: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-9/relicyms-mix-oldid-6325238.json`.
Response SHA-256: `40780f90f8e859a276ad008e204ac6c0da5e9fedff95a9c04f265fb3754a2512`.
The reused Darkan batch6 oldid `6593178`, `2012-11-20T10:11:29Z`, is after the strict cutoff and marked gone; it is not the authority for a pre-EOC correction.

## Exact identity and implementation

Both rev727 (`2012-07-24`) and rev742 (`2012-11-07`) identify four separate states:

| ID | State | Stackable | Exchangeable |
| --- | --- | --- | --- |
| 11437 | Two doses; Drink/Empty | false | true |
| 11438 | Two-dose noted twin; no Drink | true | true |
| 11439 | One dose; Drink/Empty | false | true |
| 11440 | One-dose noted twin; no Drink | true | true |

Only the two-dose drinkable state has a live inventory row in this family.
The existing recipe `finished_relicyms_mix` outputs that exact two-dose name; the existing GE provenance independently binds it to ID11437.

1. In `data/herblore_data.py`, set item_id=11437 and stackable=false on the existing two-dose extra-item metadata; retain tradeable=true and the period citation.
2. Require `HERBLORE_EXTRA_ITEM_DATA`, merged `EXTRA_ITEM_DATA` and the real `ITEM_DEFINITIONS` row to preserve those values.
3. Preserve price268 from Exchange oldid `6095907`, `2012-08-15T21:45:42Z`, and limit1000 from Calculator oldid `6457777`, `2012-10-23T03:28:03Z`, already accepted in `data/grand_exchange_period_source.json`.

Do not add one-dose or noted inventory keys, alter disease or healing behavior, or change any other potion.
Preserve all GE map entries and exact count assertions: this contract changes metadata, not the catalog census.

## Evidence boundary

The non-beta page supplies direct tradeability and stackability; the dated client definitions independently corroborate stackability, options and GE eligibility.
`ItemDefinitions.canExchange()` is not direct player-trade evidence.
Exact outputs are `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-9/cache-727-exact.txt` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-9/cache-742-exact.txt`.
The reader is `tools/OpenRs2CacheItemSearch.java`; commands and exits are in the external `query-receipts.json`.
Accepted cache inputs and committed GE facts are reused without a new archive validation or a new Exchange harvest.
The source infobox's `Exchange mix` template supplies no new numeric claim here; the existing exact two-dose Exchange provenance supplies the retained price and limit.

## Verification

Run `python3 run_tests.py` and the standing documentation, test-quality, item-reachability, worktree and diff audits.
Root runs both full lanes on the merged commit through the promotion gate.
Drive the real Herblore recipe with a nearly full carried inventory and check the existing capacity rule for separate nonstackable outputs.
Check the real registry and retained GE row, save/reload and review Undo. Add behavior coverage only for a real coverage gap.
This research contract does not claim implementation, native proof or gameplay acceptance.
