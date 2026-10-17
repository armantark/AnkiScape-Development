# Rat pole tradeability contract — 2026-10-17

Status: qualified for backend implementation. Exact empty ID `6773`, storage key `Rat pole`.
Base: `452f325d3b62c2247ad990181578c20284265f8a`. Cutoff: `2012-11-20T00:00:00Z`.
Backend scope only. This source contract changes no product code. Keep the current interface, storage keys, icons, quest rewards, levels and review quantities.
Evidence directory: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-6`. Root owns promotion, native verification and peer notices.

## Required result

Live registry: tradeable=true, stackable=true, source_item_id=None; GE absent.
Period: untradeable, nonstackable, source ID 6773 for the empty reward. Keep the existing GE exclusion.
The existing equipment record already binds the reward name to 6773. The quest reward projection carries only category/source, so registry defaults lose these flags and the ID.

## Period evidence and every variant

Reuse [Rat pole oldid 5671031](https://runescape.wiki/w/Rat_pole?oldid=5671031), `2012-05-29T02:03:21Z`.
Literal item facts: `tradeable = No`, `stackable = No`, `exchange = No`. The page distinguishes empty and one-to-six-rat states and describes the empty replacement reward.
Darkan packet: `/Users/armantarkhanian/Documents/2012scape with bots/memory-bank/audit/sources/rat-pole-source851-prebeta-response-20261017.json`.
Accepted response SHA-256: `57faa5ee1d149e356f6ecdb31635aa9b0586d63ae371f52a11a6535d8a6c6be4`.
Rev727 (`2012-07-24`) and rev742 (`2012-11-07`) bind each ID 6773/6774/6775/6776/6777/6778/6779 separately: every ID is nonstackable and exchangeable=false. 6773 has Wield; 6774–6779 also have Remove-rat. No note variant appears in either complete bounded name search.
Exact query outputs: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-6/cache-727-exact.txt` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-6/cache-742-exact.txt`; name inventories: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-6/cache-727-names.txt` and `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-6/cache-742-rat-pole-names.txt`.
Reader: `tools/OpenRs2CacheItemSearch.java`, Darkan `ItemDefinitions.canExchange()`. The item page supplies direct tradeability; the cache supplies exact-ID GE flags.
`data/equipment_data.py` already has Rat pole source_item_id 6773. Only the empty reward is registered; do not collapse filled variants into a new item or add rat mechanics in this slice.
Exchange price and buy-limit rows: not applicable. The explicit item-page prohibition and false cache flags establish GE exclusion without a missing-title query.

## Implementation and verification

1. Add the Rat pole's explicit item metadata to the existing quest reward fragment assembly in `data/quest/reward_item_fragments.py` and `data/quest/reward_items.py`: category equipment, item_id 6773, stackable=false, tradeable=false, and the period source above. Follow the existing reward-fragment convention; do not modify generated quest records or generic registry defaults.
2. Require `QUEST_REWARD_ITEM_DATA`, `EXTRA_ITEM_DATA` and the real `ITEM_DEFINITIONS` row to retain this metadata after the quest overlay and equipment enrichment.
3. Leave `EXCHANGEABLE_ITEM_NAMES` and the source/generated period GE maps unchanged. Keep the exact price/limit counts unchanged.
4. Drive the existing Ratcatchers reward claim with its real registry record. Check one nonstackable 6773 reward, no GE entry, no duplicate reward after save/reload, and reward/review Undo using existing coverage. Add a regression only if the flags/identity projection has no behavioral coverage.

Run `python3 run_tests.py` and the standing documentation, test-quality, reachability, worktree and diff audits. Root runs both full promotion lanes.
Use the real item registry and catalog. Do not stub either. Add behavior coverage only where existing coverage has a real gap.
This contract claims no implementation, native proof or gameplay acceptance.
