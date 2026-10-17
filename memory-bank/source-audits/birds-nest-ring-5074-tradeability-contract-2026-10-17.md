# Bird's nest (ring) tradeability contract — 2026-10-17

Status: backend implementation recorded below; promotion remains with Root. Base: `3c1f481e51a015432a52a3b1b5b2c205e8d0d2a7`.
Cutoff: `2012-11-20T00:00:00Z`. Backend scope only.
Preserve the current storage key, interface, icons, reward quantities and review rates.
Root owns promotion, native verification and peer notices.

## Required result

The base live `Bird's nest (ring)` row has tradeable=true, stackable=true and source_item_id=None.
The period item is ID `5074`, tradeable=false and stackable=false. Preserve its GE exclusion.

## Period evidence

Reuse [Bird's nests oldid 6550484](https://runescape.wiki/w/Special:PermanentLink/6550484), `2012-11-13T00:41:33Z`, non-beta and the latest revision before the cutoff.
The literal infobox states `tradeable = No` and `stackable = No`. The prose also states that a bird's nest cannot be traded, while a crushed nest can.
Packet: `/Users/armantarkhanian/Documents/2012scape with bots/memory-bank/audit/sources/birds-nests-source951-oldid-6550484-20261017.json`.
Accepted response SHA-256: `add959283af28d007dee38a9ee0bdae23faa881b896f0c13da86997d1598d14c`.
This is a reused pin, with no new fetch or archive validation.

## Exact identity and implementation

The existing ring opening table binds this storage key to the ring nest. Original Darkan maps ID5074 to `nest_ring`.
The supplying original emulator commit is `c6fbe036b1743f4dd6067ec178332c69c3708856`, path `/Users/armantarkhanian/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/player/content/skills/woodcutting/BirdNests.java`.
The already retained body and successful exact-commit commands are in `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-7/darkan-nest-identity.txt`. This is emulator identity evidence, not original Jagex server code.

1. In `data/woodcutting_data.py`, give the existing `Bird's nest (ring)` metadata item_id=5074, tradeable=false and stackable=false, with the period citation.
2. Require `WOODCUTTING_EXTRA_ITEM_DATA`, merged `EXTRA_ITEM_DATA` and the real `ITEM_DEFINITIONS` row to preserve those values.
3. Preserve the existing opening and grinding tables, item quantities and RNG weights. Keep the established storage key and all other item metadata.

Do not add a new nest state, acquisition route or interface. Do not change the generic Bird's nest row: its ID5070 correction belongs to Harvest7.

## Evidence boundary

Both rev727 (`2012-07-24`) and rev742 (`2012-11-07`) give exact ID5074 stackable=false and exchangeable=false.
Reuse the exact rows in `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-7/cache-727-exact.txt` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-7/cache-742-exact.txt`.
The reader is `tools/OpenRs2CacheItemSearch.java`. The non-beta page supplies direct tradeability; `ItemDefinitions.canExchange()` supplies GE eligibility only.
Exchange price and Calculator oldid6457777 buy limit are not applicable. Do not add a GE row or change existing GE map entries or count assertions.

## Verification

Run `python3 run_tests.py` and the standing documentation, test-quality, item-reachability, worktree and diff audits.
Root runs both full lanes on the merged commit through the promotion gate.
Drive the existing nest producer and consumer with the real registry; check nonstackable carried capacity, GE exclusion, save/reload and review Undo.
Add behavior coverage only for a real gap. Native proof and gameplay acceptance remain with Root.

## Implementation — 2026-10-17

`woodcutting_extra_items_as_dict` applies the exact item metadata after assembling every opening table, so later empty-nest writes cannot erase it. Existing assets, storage keys, quantities and RNG tables stay intact.
The ordinary review dispatcher is tested with default cadence enabled. Complete player state is compared after Undo for earning/opening seed and ring nests and grinding empty nests.
For this exact nest, a saved active prepared pack containing two nests plus27 Shark reloads at28 slots with two nests and26 Shark carried. Complete bank ownership and the requested layout remain unchanged. The shared Pyramid Plunder fix is merged from `8936d93baba43734d37212def0931d699f93fea4`; no second capacity fix exists.
`tests/item_tradeability/test_nest_and_rod_contracts.py` covers the metadata, shop/GE/alchemy exclusion, rock replacement, custody, load and Undo paths. The existing period-price count1443 and buy-limit count1838 remain exact equalities because no GE entry is added or removed.
Branch proof and command receipts are in `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-10/implementation/`. Root owns merged promotion and native checks.
