# Rat pole tradeability contract — 2026-10-17

Status: backend implemented; branch verification recorded below. Exact empty ID `6773`, storage key `Rat pole`.
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
This contract claims no native proof or gameplay acceptance.

## Implementation — 2026-10-17
The existing reward-fragment assembly now supplies equipment identity 6773, stackable=false, tradeable=false and item oldid 5671031. QUEST_REWARD_ITEM_DATA, EXTRA_ITEM_DATA and ITEM_DEFINITIONS retain those fields. Filled variants and the GE maps are unchanged.
Reward proof starts from a saved runtime stage 9 of 10 with the existing stage-9 action proof. A real review awards one Rat pole, review Undo restores the complete earlier state, replay and real save/load retain one, and another reward attempt cannot duplicate it. This is a final-stage reward delivery proof: generated Rat Catchers checkpoints have no playable action producers; the test does not claim a playable whole-quest route.
A saved bank count of 3 and a carried view of 3 survive real save/load unchanged. The cache STACKABLE_ITEM_NAMES already excludes Rat pole, so ordinary carried accounting was already three slots. Pyramid Plunder uses registry stackability and requires the shared capacity correction below; bank quantities stay unchanged. No migration is added. The ordinary Shop controls refuse sale; alchemy and Shattered Heart replacement exclude the pole. Its pre-existing missing asset remains unchanged under the no-icon-change scope.
Native verification and exact merged promotion lanes remain Root-owned.

Original proof at `3160e5a2e0e6836bc5814a0d0c207acc91237247`: `tests.item_tradeability.test_mining_helmet_rat_pole` and `tests.skills.test_summoning_market` pass 8 plain tests. These modules, the Shop proof `tests.item_tradeability.test_helmet_rat_pole_shop` and `tests.test_grand_exchange_data` pass 25 offscreen Qt tests with zero skips. All listed audits exit 0. Full plain output and the final commit are recorded in `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-6/report.md`.

## Active Pyramid Plunder saves — 2026-10-17
Astra found a separate registry-based consumer: a saved active pack of two corrected items and 27 Shark grew from 28 to 29 slots. The branch merges shared fix `8936d93baba43734d37212def0931d699f93fea4`; it adds no second fix. The shared logic applies entry's capacity rule on load, view and review without changing bank ownership.
`test_base_stackable_pyramid_saves_load_at_capacity_without_losing_bank_items` reuses the relevant fields from Astra's real base saves on `3c1f481e51a015432a52a3b1b5b2c205e8d0d2a7`. The committed fixture preserves the saved pack, layout, session and positive inventory fields; unrelated defaults are omitted. On the rejected head, all three subtests fail with `AssertionError: 29 != 28`.
With the shared fix, each saved pack loads as two items and 26 Shark in 28 slots. The bank retains two items and all 27 Shark; the desired layout and active session stay intact. Real save/load then preserves the complete current state. No registry or storage mock supplies these results.
The regression, shared test and existing Pyramid Plunder suite pass 19 plain and 19 offscreen Qt tests with zero skips. The non-blocking Rat Catchers route limitation remains unchanged. Round-1 evidence and final verification: `/Users/armantarkhanian/Documents/ankiscape-goal-evidence-2026-10-17/harvest-6/review-round-1/`.
