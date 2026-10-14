# Independent Sol verification — 2026-07-28

Repository: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork`

Result: **13 findings** across the four newest activity families: 9 broken mechanics, 3 wrong values (two are unregistered reconstructions), and 1 misleading panel state. No family survived clean.

## Findings

### 1. Temple Trekking — the three-charge Druid pouch is an unregistered reconstruction

- **File:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/temple_trekking_data.py:25-27`
- **Severity:** wrong-value
- **What is wrong:** `TEMPLE_TREKKING_DRUID_POUCH_CAP = 3` is explicitly described in code as a breadth-one abstraction, but it appears in neither `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/temple-trekking-trek-model-2026-07-18.md` nor `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/placeholder-values.md`, and it has no `PLACEHOLDER(...)` marker. The durable audit says unrecovered orchestration values are registered; this one is not.
- **Failure scenario:** Complete Nature Spirit, hold a Silver sickle (b), and run `prepare_pouch`. A nominally “filled” Druid pouch is hard-capped at three Ghast uses. The player must refill after the third Ghast encounter because of an undocumented invented cap.
- **Proof:** Real command probe returned `pouch_charges: 3`, `inventory_pouch: 1`, message `Used Bloom in Mort Myre Swamp and filled a Druid pouch.` The placeholder-register test passed because the value has no marker, which is exactly the known unlabelled-reconstruction failure mode.

### 2. Mobilising Armies — Explore orders incorrectly qualify for rank

- **Files:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/mobilising_armies_data.py:241-245`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/mobilising_armies_logic.py:967-1003`
- **Severity:** broken-mechanic
- **What is wrong:** The sourced rule says rank requires at least ten actions, explicitly excluding walking and exploring. The reducer increments `session["commands"]` before dispatching every productive order, including `order == "explore"`.
- **Failure scenario:** Enter Conflict with ten squads, select Explore, and issue only Explore orders. At timeout the run has eighteen “commands” and receives participation rank even though it performed zero rank-eligible actions.
- **Proof:** The real 18-beat scenario probe, including a save/load round-trip after beat 8, ended with `outcome: timeout`, `rank_gained: 1`, `rank: 1`; the beat-17 status still showed `explore`. The family tests cover idle and stalled orders but never assert that Explore is excluded from the rank counter.

### 3. Gnome Restaurant — the first 12 points grant a meal too early

- **Files:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/source-audits/gnome-restaurant-harvest-2026-07-28.md:56-62`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/gnome_restaurant_logic.py:641-656`
- **Severity:** wrong-value
- **What is wrong:** The audit says twelve points pays the Reward token and **each further twelve** adds one banked meal. The reducer grants the token and then increments `token_meals` for the same first threshold.
- **Failure scenario:** Start at nine points and complete one hard delivery. The player reaches twelve points and receives both the token and one free meal; the first meal should arrive at twenty-four points.
- **Proof:** Real delivery probe returned `points: 12`, `token_granted: true`, `token_inventory: 1`, and `token_meals: 1`. `test_twelve_points_pay_a_token_and_each_twelve_more_bank_a_meal` checks only the eventual cap after 45 deliveries and never checks the first threshold’s meal count.

### 4. Gnome Restaurant — accepting a job can steal another persistent activity’s session

- **Files:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/gnome_restaurant_logic.py:237-254`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/gnome_restaurant_logic.py:436-456`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/core/storage_pure.py:1893-1908`
- **Severity:** broken-mechanic
- **What is wrong:** `_accept_reason()` checks service state, outstanding orders, decline wait, and customer reachability, but not the exclusive `activity_session`. `accept_gnome_restaurant_order_pure()` then unconditionally overwrites `activity_session.active_id` with `gnome_restaurant`.
- **Failure scenario:** Open Gnome Restaurant service, then start a real Temple Trekking session. While the trek is active, accept an easy Gnome Restaurant order. The Gnome command succeeds, replaces the owner, and the next save/load reconciliation deletes the live Temple Trekking session.
- **Proof:** Probe began with a real Temple route `['abidor_crank', 'ghasts', 'bridge', 'swamp_snakes']`. Gnome acceptance returned `ok: true`, changed owner from `temple_trekking` to `gnome_restaurant`, and after `migrate_loaded_data()` reported `temple_active_after_reload: false`. The existing persistence test checks the inverse repair—an already-created Gnome order losing ownership—but not entry while another family owns the session.

### 5. Dominion Tower — Leave works during a live match despite the sourced lock-in rule

- **Files:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/dominion_tower_logic.py:1290-1299`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/dominion_tower_logic.py:1875-1877`
- **Severity:** broken-mechanic
- **What is wrong:** The combat path cites the rule that a player cannot leave a match until winning or losing, but the `leave` command accepts any non-empty mode and does not check `state["roster"]`.
- **Failure scenario:** Start a Freestyle match against Nomad and immediately press Leave before one review. The run ends safely, allowing the player to evade the match and any defeat consequence.
- **Proof:** Real command probe had `roster_before: 1`; `leave` returned `ok: true`, `roster_after: 0`, and cleared the activity owner. The tests routinely use `leave` after a win when the implementation has already spawned the next roster, but never call it during an uncleared first match.

### 6. Dominion Tower — No Familiar does nothing

- **Files:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/dominion_tower_data.py:245-249`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/dominion_tower_logic.py:631-686`
- **Severity:** broken-mechanic
- **What is wrong:** `no_familiar` is a real handicap effect, but `_apply_burst_handicaps()` has no branch for it. The active Summoning follower is neither dismissed nor suppressed. This also contradicts the audit’s statement that only the two movement handicaps are factor-only translations.
- **Failure scenario:** Enter Freestyle with an active Spirit wolf and the No Familiar handicap, then resolve a review. The familiar remains live throughout the arena.
- **Proof:** Real review probe returned the unchanged active follower after combat: `kind: familiar`, `entity_id: spiritwolf`, `remaining_reviews: 100`. No family test exercises the No Familiar effect.

### 7. Dominion Tower — armour-removal handicaps delete equipped items instead of banking them

- **Files:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/dominion_tower_data.py:260-266`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/dominion_tower_data.py:300-305`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/dominion_tower_logic.py:658-672`
- **Severity:** broken-mechanic
- **What is wrong:** The source-backed descriptions say body armour and shields are sent to the bank. The reducer removes the slot from `equipment` but grants the item to neither inventory nor bank.
- **Failure scenario:** Equip a Dragon chainbody, enter a No Body Armour match, and resolve one review. The chainbody disappears from all ownership stores.
- **Proof:** Probe result after one real combat review: equipment contained only `weapon: Abyssal whip`, while both bank and inventory held `0` Dragon chainbodies. The Dominion tests record that No Food was suffered, but do not execute No Body Armour or No Shield ownership behavior.

### 8. Dominion Tower — No Food permanently rewrites combat preferences

- **Files:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/dominion_tower_logic.py:645-657`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/dominion_tower_logic.py:1693-1717`
- **Severity:** broken-mechanic
- **What is wrong:** A match-local handicap mutates the persistent `combat_supply_loadout` and `combat_auto_eat_food`; the post-burst state is saved rather than restoring those preferences after the slice or match.
- **Failure scenario:** Configure auto-eat to Shark and a food loadout, enter a No Food match, resolve one review, then leave. The user’s ordinary combat configuration is no longer the one they selected.
- **Proof:** Probe started with `combat_auto_eat_food: "Shark"` and a Shark loadout. After one real review it held the engine’s default food list and an empty food loadout. Existing handicap tests do not assert post-match preference restoration.

### 9. Dominion Tower — hit-budget weapons lose six charges per review, not per hit

- **Files:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/dominion_tower_data.py:1485-1504`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/dominion_tower_logic.py:1722-1727`
- **Severity:** broken-mechanic
- **What is wrong:** The crossbow’s exact budget is 100 shots and the staff placeholder is 100 hits, but the reducer subtracts `DOMINION_TOWER_REVIEW_TICKS` from every weapon regardless of its `charge_unit`. The sword is tick-based; the crossbow and staff are not.
- **Failure scenario:** Wield the Dominion crossbow and complete a six-tick review in which the enemy is not killed. Six charges disappear even though the budget is denominated in hits.
- **Proof:** Real review probe returned `before: 100`, `after: 94`, `spent: 6`, `combat_killed: false`. The test suite asserts the same six-charge decrement only for the tick-based Dominion sword and never exercises crossbow/staff charge units.

### 10. Dominion Tower — multiple Xp books overwrite each other’s value

- **Files:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/dominion_tower_logic.py:247-254`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/dominion_tower_logic.py:1319-1362`
- **Severity:** broken-mechanic
- **What is wrong:** Book value is stored once in global state as `xp_book_factor`, while inventory can contain multiple Xp books. A later reward claim or exchange overwrites the factor for every previously held book.
- **Failure scenario:** Exchange one Scorpion meat for a 500-factor book, keep it, then exchange two meat for a 1,000-factor book. Read both. Both books pay the second book’s amount.
- **Proof:** Probe recorded factors `500` then `1000`; both reads paid `100.0 attack_exp`, for `200` total. Per-book values should produce `50 + 100 = 150` under the shipped placeholder scale. The existing test creates and reads only one book.

### 11. Dominion Tower — the 20-per-item reward-box cap is applied per roll, not per box

- **Files:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/dominion_tower_data.py:1569-1588`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/dominion_tower_logic.py:1021-1029`
- **Severity:** broken-mechanic
- **What is wrong:** The source says a Reward box gives at most 20 of any individual capped item at once. The code caps each roll at 20, then allows repeated rolls of the same item to accumulate beyond 20.
- **Failure scenario:** All three reward rolls select Blood rune. The box grants 60 Blood runes.
- **Proof:** Controlled real claim returned `granted: {'Xp book': 1, 'Blood rune': 60}` and inventory `Blood rune: 60`. The source-audited cap is 20.

### 12. Dominion Tower — the three reward-box rolls are an unregistered reconstruction

- **File:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/data/dominion_tower_data.py:1569-1571`
- **Severity:** wrong-value
- **What is wrong:** `DOMINION_TOWER_REWARD_BOX_ROLLS = 3` is justified only by Darkan’s reconstructed box shape. The durable audit lists reward-box contents and the 20-item cap, says missing values are registered, and does not list a roll count. There is no `PLACEHOLDER(dominion_tower.reward_box_rolls)` row or code marker.
- **Failure scenario:** A claim deterministically produces three common-item draws even though the period count is not sourced. With Scorpion meat selected, the box grants 84 meat because it performs three 28-meat draws.
- **Proof:** Real claim with a constant roll returned `Scorpion meat: 84` plus one Xp book. `rg` found `REWARD_BOX_ROLLS` only in the data constant and consumer, with no audit or placeholder entry.

### 13. Dominion Tower — the panel enables rewards the logic layer says cannot be claimed

- **Files:** `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/ui/dominion_tower_panel.py:404-423`; `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/logic/dominion_tower_logic.py:929-935`
- **Severity:** cosmetic
- **What is wrong:** The panel reconstructs claimability from membership in `unlocked_rewards` instead of consuming the view’s readiness flags. It enables the claim button for an unlocked Dreadnip with zero reward credits, and similarly cannot represent the next Ascendancy-mine kill threshold.
- **Failure scenario:** Have 450 kills and the spectate unlock, spend the available reward credit, then open the panel. The Dreadnip row and claim button remain enabled; clicking it produces a backend refusal.
- **Proof:** Offscreen Qt probe returned `dreadnip_ready: false`, `reward_rows: 1`, `claim_enabled: true`; the real command then refused with `No reward credits banked; five more boss kills earn the next one.` The UI module’s header claims every enable decision comes from the pure view, but its tests do not cover this state.

## What was executed

### Temple Trekking

- Real entry gate, pouch preparation, follower-food loading, seeded route generation.
- `Again` with no advancement.
- JSON save → `migrate_loaded_data()` → continuation.
- Full real route: `Abidor Crank → Ghasts → Bridge → Swamp snakes`, completed in 23 reviews and paid a blue token.
- Companion-death failure and player-death failure.
- Direct abandon.
- Review undo restored the exact pre-review save; direct-action undo test restored food and inventory.

### Mobilising Armies

- Real investment, squad recruitment, policy, entry, eighteen-beat Conflict scenario, midpoint save/load, timeout settlement.
- All-Explore rank probe.
- Direct forfeit: zero rank, zero reward credits, ten surviving squads returned.
- Review undo and direct-action undo.

### Gnome Restaurant and gnome Cooking

- All twenty gnome Cooking rows executed through `apply_cooking_action_pure`; every row produced its real output and sourced XP.
- Training gate, open service, easy/hard order acceptance, `Again`, save/load, delivery, next-order chaining, first token threshold, leave, and active-session conflict.
- Review undo and direct-action undo.

### Dominion Tower

- Real gate, face command, Freestyle entry, live combat review, save/load continuation, leave, reward claim, reward exchange, Xp-book reads, power-up use, handicaps, familiar state, and panel state.
- Family tests also executed the real defeat, multi-NPC, Pest Queen healing, special, reward-ladder, and safe-death paths.
- Review undo and direct-action undo.

## Test results

- Direct `/opt/homebrew/bin/python3 -m pytest` could not run because that interpreter has no `pytest` installed.
- Native pytest collection through an ephemeral `uv` pytest environment imports the add-on root `__init__.py` and fails without Anki’s `aqt` host. An isolated pytest wrapper then ran the actual family unittest modules: **192 methods, 176 ordinary passes, 16 skips, 0 failures/errors**.
- Real offscreen Qt lane: **168 methods, 167 ordinary passes, 1 skip, 0 failures/errors**.
- Four targeted family direct-action undo tests: **4/4 passed**.
- Placeholder register: **3/3 passed**—but findings 1 and 12 bypass it because their constants have no marker.
- `tools/audit_test_quality.py`: **3,449 tests across 165 files, 0 hard issues**.
- Repository remained clean; no repo files were edited.
