# Conquest board size: implementation contract

Status: **contract ready; product change pending.** Register row: `conquest.board_size`.
Cutoff: `2012-11-20T00:00:00Z`. AnkiScape research base: `8749ddc60555a5c62f64d8dfbcc04f64f207bcc1`.

## Value and pins

The playable board is **20 × 20 squares**, with local coordinates `0..19` on both axes. Keep the numeric value at `data/conquest_data.py:23`. Remove its marker and matching register row together during implementation.

The new evidence lever is Darkan's retained map projection. The older AnkiScape audit requested this geometry but did not use it.

| Layer | Existing pin |
| --- | --- |
| Period article | `Conquest`, oldid `6450144`, `2012-10-21T19:17:00Z`, literal wikitext line 8: `20x20 squares board`. Packet: `/Users/armantarkhanian/Documents/2012scape with bots/memory-bank/audit/sources/conquest-oldid-6450144.json`. |
| Independent period map | `/Users/armantarkhanian/Documents/2012scape with bots/memory-bank/audit/evidence/static/openrs2-cache-727-742-conquest.json`. Build 742 selects projected contract `a1c749a7bea92c07e4fd65112b2e8dc9e0b28d8adce7397eb09864ddd0476d13`. In `contract.map_objects`, floor IDs `52257/54486/55094/55183/55188/55193` occupy all 400 distinct coordinates in `x=2659..2678`, `y=9041..9060`, plane 0, region `10637`, with no gaps. Builds 727 and 741 agree on this footprint. |
| Accepted qualification | `/Users/armantarkhanian/Documents/2012scape with bots/memory-bank/audit/reports/conquest-iteration-424-contract.md`, “Source facts” and “Cache facts”; supplying outer commit `222566f9fddae8490dbdd140b86ea7a78578a273`. |

The article, Scout, and map packets were supplied by outer commit `387a55935b64e90f42304ae13ccf11b986af3666` (“Freeze Conquest November 2012 source evidence”). The retained map packet dates build 742 to `2012-11-07`, OpenRS2 cache `544`, archive SHA-256 `9f5fdba0d22cdc1b4ad86c984cc0ba4bcd4b3c22039f3290ba48f5083bc100b8`. Accepted hashes were reused; no new harvest or hash verification was performed.

## Conflict and limits

`Scout (Conquest)` oldid `4877028`, `2011-10-27T08:36:23Z`, line 17 says `22x22`. Packet: `/Users/armantarkhanian/Documents/2012scape with bots/memory-bank/audit/sources/conquest-scout-oldid-4877028.json`. The later main article and independent complete floor footprint agree on 20 × 20. Do not claim that the extra squares were borders: no cited source explains the discrepancy.

Darkan server `src/main/java/com/rs/game/content/minigames/conquest/ConquestModel.kt:184` at supplying commit `e9ea84b6bdb2d497dd7d68ade53dca0b82031f1c` also sets `BOARD_SIZE = 20`. Its history says “Restore the Conquest match domain”. It consumes the restored contract; it is not independent historical corroboration.

This contract settles dimensions only. It does not settle collision, diagonal movement, targeting distance, command income, initial points, troop-cap enforcement, default loadout, or rewards. Client identities do not prove these server behaviors.

## Implementation and tests

1. Remove only the marker at `data/conquest_data.py:23` and the `conquest.board_size` row in `memory-bank/placeholder-values.md`; retain `CONQUEST_BOARD_SIZE = 20` and all other placeholders.
2. Update the board-size entries under “Placeholder candidates” and “Conflicts and exclusions” in `memory-bank/source-audits/conquest-harvest-2026-07-28.md` to cite this contract.
3. Strengthen `tests/test_conquest.py:224`, `ConquestEntryAndSetupTests.test_entry_builds_a_bounded_board_and_unlocks_both_tracks`, with the independent exact assertion `CONQUEST_BOARD_SIZE == 20`. Its current bound check reads the constant and would accept an incorrect larger board. Keep the real entry path and coordinate checks.
4. Run the Conquest suite and `tests.test_placeholder_register`; preserve exact marker/register agreement and all audit baselines.

No product, register, or test file was changed by this research slice.
