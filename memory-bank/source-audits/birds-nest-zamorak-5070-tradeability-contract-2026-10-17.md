# Red egg bird nest tradeability contract — 2026-10-17

Status: backend implemented; root promotion and native acceptance remain. Exact ID `5070`, storage key `Bird's nest (Zamorak egg)`.
Base: `452f325d3b62c2247ad990181578c20284265f8a`. Cutoff: `2012-11-20T00:00:00Z`.
Backend scope only. Preserve storage keys, current interface, icons, producers, reward quantities and review rates.
Evidence directory: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-7`. Root owns promotion, native verification and peer notices.

## Required result

Before implementation at the recorded base, `Bird's nest (Zamorak egg)`: tradeable=true, stackable=true, source_item_id=None, GE absent.
Period ID 5070: tradeable=false, stackable=false, GE absent. Bind the existing named egg nest to source_item_id=5070.
At the recorded base, the Woodcutting extra-item builder supplied only category/source for this key, so registry defaults lost the identity and flags.

At the recorded base, the separate `Bird's nest` row also had source_item_id=5070, tradeable=true and stackable=false. Set its tradeable flag to false through `data/gnome_restaurant_data.py`'s explicit untradeable set; preserve its current key and ID. The producer comment calls 5070 a seed-bearing variant, while Darkan binds it to a red egg. This contract qualifies tradeability for the registered ID; it does not qualify the Restaurant reward identity or authorize changing its reward.

## Period evidence and exact identity

Reuse [Bird's nests oldid 6550484](https://runescape.wiki/w/Bird%27s_nests?oldid=6550484), `2012-11-13T00:41:33Z`, non-beta.
Literal infobox: `tradeable = No`, `stackable = No`, `value = 1`. Article explicitly says a bird's nest cannot be traded, while a crushed nest is tradeable.
Packet: `/Users/armantarkhanian/Documents/2012scape with bots/memory-bank/audit/sources/birds-nests-source951-oldid-6550484-20261017.json`.
Accepted response SHA-256: `add959283af28d007dee38a9ee0bdae23faa881b896f0c13da86997d1598d14c` (Darkan shared ledger; reused without re-harvest or re-hash).
The page's Eggs table binds red eggs to Zamorak birds. Its ordinary nest claim applies to egg-bearing nests; it is not an inference from a modern Exchange page.

Rev727 (`2012-07-24`) and rev742 (`2012-11-07`) separately bind 5070 to `Bird's nest`, Search, stackable=false and exchangeable=false.
Exact outputs: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-7/cache-727-exact.txt` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-7/cache-742-exact.txt`.
Reader: `tools/OpenRs2CacheItemSearch.java`, `ItemDefinitions.canExchange()`. The cache flag proves GE exclusion, not direct tradeability; the item page supplies direct tradeability.
All eight nest IDs 5070/5071/5072/5073/5074/5075/7413/11966 are separately nonstackable and exchangeable=false in both caches; crushed IDs6693/6694 are separately exchangeable=true, with only note6694 stackable. No state is merged by cache name.

Darkan identity mapping is unchanged from upstream initial commit `c6fbe036b1743f4dd6067ec178332c69c3708856`:
`src/main/java/com/rs/game/player/content/skills/woodcutting/BirdNests.java` maps nest5070 to egg5076; `src/main/java/com/rs/game/player/content/pet/Incubator.java` names egg5076 as Zamorak.
Current paths: `/Users/armantarkhanian/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/skills/woodcutting/BirdNests.java` and `/Users/armantarkhanian/Documents/2012scape with bots/darkan-world-server/src/main/java/com/rs/game/content/pets/Incubator.java`.
Inspected git history and retained exact initial-commit bodies in `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-7/darkan-nest-identity.txt`. This is original upstream reconstruction, corroborated by the dated item page and caches; no restoration AuditProbe is used.

Exchange price and Calculator6457777 buy limit: not applicable. Explicit item-page prohibition and false exact-ID flags establish exclusion without a missing-title query. No price or buy limit is invented or copied from crushed nest6693.

## Implementation and verification

1. In the existing `data/woodcutting_data.py` extra-item builder, supply item_id=5070, tradeable=false and stackable=false for exact key `Bird's nest (Zamorak egg)`; retain a period-source citation. Use the existing metadata projection. Do not change generic registry defaults or rewrite nest drop/open mechanics.
2. Require the real `WOODCUTTING_EXTRA_ITEM_DATA`, merged `EXTRA_ITEM_DATA` and `ITEM_DEFINITIONS` row to retain this exact metadata. Do not rename the key or merge it with another egg, seeds, rings, empty5075 or crushed6693.
3. Preserve the current GE exclusion. Leave the source/generated period GE maps unchanged. At this base the exact guide-price/buy-limit counts are1443/1838; this contract contributes zero to both counts. Re-measure after parallel integration and retain exact equalities.
4. Drive the existing earned nest and Open bird nests route with the real registry: preserve the Zamorak egg reward and empty nest result, quantities, save/reload, and review Undo. Require no GE listing. Check nonstackable inventory capacity through the existing inventory path; add behavior coverage only for a demonstrated gap.

Run `python3 run_tests.py` and the standing documentation, test-quality, reachability, worktree and diff audits. Root runs both full promotion lanes.
## Backend proof — 2026-10-17

The Woodcutting extra-item metadata now binds the exact egg nest ID with tradeable=false and stackable=false. The registry projects both flags unchanged. The generic Restaurant `Bird's nest` registered5070 is also untradeable under the Zamorak contract; its reward key, ID and quantity stay intact. Seed, ring and empty nest metadata are unchanged. No existing interface, art, producer, drop weight or opening quantity changed.

`tests/item_tradeability/test_egg_nest_tradeability.py` drives real review acquisition, opening, Undo and real save/load with complete-state assertions. The existing configurable legacy cadence path is selected; only RNG and presentation are controlled. Each egg nest opens to exactly one matching egg and one empty nest. Reload performs its existing clamp of a consumed nest out of the old Woodcutting carried view; the complete expected state includes that exact removal.

Shops reject all three egg nests and generic5070 as `item_not_tradeable`. Both alchemy maps omit them and unchanged seed nests; both spells return exactly `Choose a tradeable bank item`. Shattered Heart leaves each egg nest and generic5070 intact while replacing exactly one unchanged seed-nest output with one Woodcutting strange rock. GE already omitted the egg nests: new buy/sell offers return `unknown_item`. Storage can retain historical offers despite catalog absence, so tests preserve buy/sell escrow through real reload, prove no fill at both random extremes, cancel and collect exact111 coins or3 items once.

Ordinary carried behavior already used nonstackable slots: `data.item_values.STACKABLE_ITEM_NAMES` already excludes the named egg nests. Existing Bank counts, saved layouts and carried views holding30 survive reload as30. Slot accounting uses30 slots, the grid shows28 individual nests, and the next pack fill caps at28 without deleting Bank ownership. Pyramid Plunder derives stackability from the registry; the correction now caps its custom entry pack at28 from30 owned nests, and its view reports28 slots. No migration was added. UI projections use that same carried stackable set; shop and GE views delegate eligibility to the checked logic.

The exact period guide-price/buy-limit pins remain1443/1838; this change adds zero entries to either map. Verification commands, counts and exit statuses are in `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-7/implementation/result.json`. Root owns full merged Qt promotion and native acceptance; this record claims neither.
