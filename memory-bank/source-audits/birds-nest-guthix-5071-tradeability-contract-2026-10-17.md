# Green egg bird nest tradeability contract — 2026-10-17

Status: qualified for backend implementation. Exact ID `5071`, storage key `Bird's nest (Guthix egg)`.
Base: `452f325d3b62c2247ad990181578c20284265f8a`. Cutoff: `2012-11-20T00:00:00Z`.
Backend scope only. No product code changes in this research commit. Preserve storage keys, current interface, icons, producers, reward quantities and review rates.
Evidence directory: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-7`. Root owns promotion, native verification and peer notices.

## Required result

Live `Bird's nest (Guthix egg)`: tradeable=true, stackable=true, source_item_id=None, GE absent.
Period ID 5071: tradeable=false, stackable=false, GE absent. Bind the existing named egg nest to source_item_id=5071.
The Woodcutting extra-item builder supplies only category/source for this key, so registry defaults lose the identity and flags.

## Period evidence and exact identity

Reuse [Bird's nests oldid 6550484](https://runescape.wiki/w/Bird%27s_nests?oldid=6550484), `2012-11-13T00:41:33Z`, non-beta.
Literal infobox: `tradeable = No`, `stackable = No`, `value = 1`. Article explicitly says a bird's nest cannot be traded, while a crushed nest is tradeable.
Packet: `/Users/armantarkhanian/Documents/2012scape with bots/memory-bank/audit/sources/birds-nests-source951-oldid-6550484-20261017.json`.
Accepted response SHA-256: `add959283af28d007dee38a9ee0bdae23faa881b896f0c13da86997d1598d14c` (Darkan shared ledger; reused without re-harvest or re-hash).
The page's Eggs table binds green eggs to Guthix birds. Its ordinary nest claim applies to egg-bearing nests; it is not an inference from a modern Exchange page.

Rev727 (`2012-07-24`) and rev742 (`2012-11-07`) separately bind 5071 to `Bird's nest`, Search, stackable=false and exchangeable=false.
Exact outputs: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-7/cache-727-exact.txt` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-7/cache-742-exact.txt`.
Reader: `tools/OpenRs2CacheItemSearch.java`, `ItemDefinitions.canExchange()`. The cache flag proves GE exclusion, not direct tradeability; the item page supplies direct tradeability.
All eight nest IDs 5070/5071/5072/5073/5074/5075/7413/11966 are separately nonstackable and exchangeable=false in both caches; crushed IDs6693/6694 are separately exchangeable=true, with only note6694 stackable. No state is merged by cache name.

Darkan identity mapping is unchanged from upstream initial commit `c6fbe036b1743f4dd6067ec178332c69c3708856`:
`src/main/java/com/rs/game/player/content/skills/woodcutting/BirdNests.java` maps nest5071 to egg5078; `src/main/java/com/rs/game/player/content/pet/Incubator.java` names egg5078 as Guthix.
Current paths: `/Users/armantarkhanian/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/woodcutting/BirdNests.java` and `/Users/armantarkhanian/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/pets/Incubator.java`.
Inspected git history and retained exact initial-commit bodies in `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-7/darkan-nest-identity.txt`. This is original upstream reconstruction, corroborated by the dated item page and caches; no restoration AuditProbe is used.

Exchange price and Calculator6457777 buy limit: not applicable. Explicit item-page prohibition and false exact-ID flags establish exclusion without a missing-title query. No price or buy limit is invented or copied from crushed nest6693.

## Implementation and verification

1. In the existing `data/woodcutting_data.py` extra-item builder, supply item_id=5071, tradeable=false and stackable=false for exact key `Bird's nest (Guthix egg)`; retain a period-source citation. Use the existing metadata projection. Do not change generic registry defaults or rewrite nest drop/open mechanics.
2. Require the real `WOODCUTTING_EXTRA_ITEM_DATA`, merged `EXTRA_ITEM_DATA` and `ITEM_DEFINITIONS` row to retain this exact metadata. Do not rename the key or merge it with another egg, seeds, rings, empty5075 or crushed6693.
3. Preserve the current GE exclusion. Leave the source/generated period GE maps unchanged. At this base the exact guide-price/buy-limit counts are1443/1838; this contract contributes zero to both counts. Re-measure after parallel integration and retain exact equalities.
4. Drive the existing earned nest and Open bird nests route with the real registry: preserve the Guthix egg reward and empty nest result, quantities, save/reload, and review Undo. Require no GE listing. Check nonstackable inventory capacity through the existing inventory path; add behavior coverage only for a demonstrated gap.

Run `python3 run_tests.py` and the standing documentation, test-quality, reachability, worktree and diff audits. Root runs both full promotion lanes.
This contract claims no implementation, native proof, acquisition qualification or gameplay acceptance.
