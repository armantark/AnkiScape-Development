# 28-Slot Carried Inventory — Design (owner-grilled 2026-07-07)

Status: **slices 1–3 substantially shipped (2026-07-07).** Foundation, the live
overlay (churn teeth, 1-review bank-runs, Keep/Drop), death-drop, the Coal-bag
mechanic, and the collapsible Bank-tab panel are built and tested (814 tests).
Remaining: **2f** loot filter (blocked on a runtime item→value table — needs a
full-cache dump), **2g** ambush-unify (resolved as *keep separate*), the advanced
UI (click-from-bank fill, Keep/Drop toggle, loot checkboxes), and a live
render-check of the panel in an aqt environment (Qt is unavailable in the build
env, so the offscreen UI test only runs there).

## Foundation slice implemented (2026-07-07)

- `inventory_pure.py` now owns the standalone 28-slot API: slot accounting,
  capacity checks, high-alch loot filtering, money-pouch balance helpers, and
  carried state defaults/sanitization.
- `storage_pure.py` seeds `carried_inventory`, `carried_pack_mode`, and
  `loot_value_threshold` on new and migrated saves.
- **The money pouch is not a separate store (correction 2026-07-07).** Coins
  stay canonical in the flat `inventory["Coins"]` — the same store shops,
  quests, and crafting already transact through — and the "money pouch" is just
  that balance surfaced under a pouch label (`inventory_pure.money_pouch_balance`
  reads it read-only). The design goal (coins never occupy a carried slot, never
  drop on death) is met by the overlay/death/loot paths simply *excluding* coins
  (`inventory_pure.COIN_ITEM_NAME`), not by relocating them. This avoids a large,
  risky economy repoint (coins flow through the generic requirement/reward engine
  across dozens of quests, crafting recipes, shops, and death-office reclaim) and
  removes any chance of stranding a coin balance. No `CURRENT_CONFIG_VERSION` bump
  is needed for the coin model.
- Tests: `test_inventory_pure.py` covers the new pure API; the migration tests
  assert the overlay keys are seeded while coins remain in the flat inventory.
- `pack_carried_inventory_pure(bank, spec, mode, stackable_names)` (the casual
  preset packer named in the design) is built and tested: required held items
  first, a mode-scaled food reserve, then the primary material fills the rest,
  every count capped by the bank. Bag packing is deferred to the bag slice.

## Slice 2 — wiring plan (seam confirmed 2026-07-07)

The invasive core-loop change. The integration seam is confirmed:

- **Where actions happen:** `__init__.py::on_good_answer` dispatches a per-skill
  handler via `_registered_answer_handler(current_skill)`. Combat runs once and
  already owns its loadout + bank-run. Skilling handlers loop
  `_review_action_multiplier()` times, and each tick calls the handler, which
  consumes inputs from and writes outputs to `player_data["inventory"]` directly
  (e.g. `apply_crafting_pure`, `apply_mining_pure`). This loop is the insertion
  point for the skilling overlay + bank-run.
- **Combat is the template**, already built: `combat_supply_loadout` is a carried
  subset drawn from the bank; `combat_bank_run` = `{reviews_remaining, target_id}`
  charges `COMBAT_BANK_RUN_REVIEWS` (2) and refills on completion
  (`_combat_progress_or_start_bank_run`). Slice 2 generalizes this to skilling at
  1 review.

### Key wiring decision — the carried subset is a real item dict, not a meter

A tempting shortcut is to model "carried" as a virtual capacity meter over the
single flat store (decrement per action, charge a review when exhausted). It is
rejected: death-drop, loot-competes-for-slots, and bags all need **item-level**
knowledge of *what* is carried. So `carried_inventory[target_id]` is a real
`{item: count}` subset, and the skilling handler must consume from it:

1. Before a skilling tick, ensure the carried subset can supply the action's
   inputs. If it cannot but the bank can, start/continue a `skilling_bank_run`
   (1 review; mirror `_combat_progress_or_start_bank_run`) *instead of* acting;
   on completion, repack the carried subset from the bank via
   `pack_carried_inventory_pure` (casual) or the saved per-target layout
   (advanced), and resume.
2. The tick consumes inputs from the carried subset. Gathering with **Keep**
   deposits outputs into the carried subset and auto-banks (1 review) when full;
   **Drop** bypasses the subset entirely (no bank, fastest XP).
3. Coins and quest items are excluded from the subset (see coin note above).

### 2d mechanism decision — item-level view over the single flat store

The carried subset is a real per-target item dict (settled above), but it is a
**view over the unified flat store, not a second physical store.** The flat
inventory stays the single source of truth that shops, quests, and the UI read as
the bank. `carried_inventory[target_id]` = `{item: count}` marks *which subset of
the owned total is in hand right now*. Rationale:

- Per-skill handlers (`apply_crafting_pure`, `apply_mining_pure`, …) keep
  consuming from / producing to `player_data["inventory"]` unchanged — no handler
  rewrite, no transient inventory-swap, no risk to the ~20 modules reading it.
- The overlay logic lives in **one pure function** called from `on_good_answer`
  after each tick: it updates the carried view (inputs drawn / outputs kept),
  decides when 28 slots are exhausted, and drives `bank_run_progress_pure`. This
  keeps 2d unit-testable; the `__init__.py` change is a thin call.
- Death-drop subtracts the carried view from the flat store into the grave
  (coins/quest items excluded). Loot/bags update the same view.

This reconciles "real item dict" with "least-invasive": item-level knowledge for
death/loot/bags, but no storage split.

### Unified teeth — output view + input budget (refinement 2026-07-07)

The pure overlay built so far (`carried_bank_run_gate_pure` / `carried_fold_gains_pure`)
models **output teeth** correctly: gathered/produced items accumulate in the view
and a full pack (28 slots) forces a bank-run. But consumption skills (Firemaking
burns logs and produces nothing; net-consumption processing) would never fill an
output pack, so they'd get no teeth — contradicting decision 5 (input + output,
unified).

RS reality: whatever the slot mechanics, the cadence is ~28 actions per bank run
(28 empty → fill, or 28 inputs → consume, or 28 in → 28 out). The cleanest
slot-accurate unified trigger is a single **churn scalar**, not two counters:

- Per action, `churn += max(output_slots_gained, input_slots_consumed)`, both read
  from the inventory delta (positive side = gained, negative side = consumed).
- Bank-run when `churn >= CARRIED_CAPACITY`; on completion reset `churn = 0` and
  clear the output view.

Why max() and one scalar: gathering (gain 1, consume 0) and consumption (gain 0,
consume 1) both churn 1/action → bank at 28; a 3-output gather churns 3/action →
banks at ~9 (pack really is full then); 1:1 processing churns 1/action. So churn
replaces the `carried_slots_used(view) >= 28` check in the gate. The item **view**
stays exactly as built — it is the death/loot content record, cleared on bank —
but it is no longer the trigger. `carried_churn` ({target_id: int}) is new state.
**Refactor the gate to take churn before writing the runtime wrapper.**

### 2d integration is unit-testable (key finding 2026-07-07)

The skilling handlers live in `runtime_actions.py` and are exercised in
`tests/test_runtime_actions.py` through a plain `RuntimeActionContext` built from
lambda stubs — **no live Anki needed.** So 2d lands as a tested wrapper in
`runtime_actions.py`, not a blind `__init__.py` edit. Concrete shape:

```
def run_with_carried_overlay(ctx, skill_id, target_key, handler):
    target_id = str(player_data.get(target_key, ""))
    keep = carried_keep_drop.get(target_id, "keep") != "drop"
    view  = carried_inventory.get(target_id, {})
    state = player_data.get("skilling_bank_run", {})
    new_state, new_view, event, act = carried_bank_run_gate_pure(view, keep, ...)
    if not act:            # this answer buys the bank-run, no XP
        persist state+view; ctx.show_activity_gain("Bank run"); return True
    before = dict(inventory); result = handler(ctx); after = inventory
    if result is not False and keep:
        fold inventory_delta_gains(before, after) into the view; persist
    return result
```

Then `on_good_answer`'s skilling branch calls this wrapper instead of the raw
handler. Remaining prep before writing it:
- Add `carried_keep_drop` ({target_id: "keep"|"drop"}, default keep) to
  `default_carried_state` + `sanitize_carried_state` and a `skilling_bank_run`
  state key.
- Build the `skill_id -> target_key` map (e.g. mining→`current_mining`,
  crafting→`current_craft`, fishing→`current_fishing`, …) from the handlers.
- Stackable set: pass empty for v1 (gathering outputs are unstackable); wire the
  real cache `stackable` set with the loot/bag slice.
Verify with new `test_runtime_actions.py` cases (28 gather ticks → 29th banks,
no XP → 30th gathers), then a light offscreen/live smoke.

### Click-from-bank manual layout — obviated by the churn overlay (2026-07-07)

The original "click items from the bank to fill a carried loadout" was a feature
of the *split-storage* model (physically pre-load 28 slots). The overlay actually
built is a **view over the flat store + churn meter**: gathering fills the pack
from actions, and processing draws inputs from the infinite bank on demand — there
is no pre-loaded loadout to hand-fill. So click-from-bank does not map onto the
chosen architecture. The advanced controls that *do* fit are shipped in the Bank
panel: packing mode, the Keep/Drop power-gather toggle, and the **loot-value
threshold** spinbox (the coarse form of the per-drop "loot checkboxes", driving
the 2f filter). If a split-storage loadout is ever wanted, it would be a separate
model change, not a UI addition.

### 2g ambush unify — SHIPPED as one shared constant (2026-07-07)

`shop_logic._WILDERNESS_SLOTS_PER_TRIP` now *is* `inventory_pure.CARRIED_CAPACITY`,
so a Wilderness "trip" and the carry model share a single 28 source of truth. The
two *accumulators* stay distinct on purpose: `wilderness_shop_slots` counts shop
purchase volume, `carried_churn` counts skilling slots — collapsing them would
conflate unrelated flows.

### 2f loot filter — SHIPPED (2026-07-07)

The observable behaviour the owner asked for ("no auto-hoarding every tiny drop")
is live: `item_values.py` builds a 943-item value table from committed shop buy
prices (the cache value for coin shops) plus the real cache `stackable` set, and
`inventory_pure.filter_loot_pure` runs in `handle_combat_answer` — after a kill,
below-threshold known-value unstackable drops are left on the floor; stackables,
coins, and unknown-value items are always kept. Default threshold lowered from a
placeholder 50 to **10** (keep a monster's real drops like raw meat; leave only
near-worthless junk); tunable.

Two refinements remain, both genuinely gated:
- **Full-cache value table** (all items, not just the 943 shop items) needs the
  JDK-24 cache dump — the machine has JDK 23, so unknown-value drops are kept
  conservatively until then.
- **Kept loot competes for carried slots / drops on death** needs combat to feed
  drops into a carried pack; combat runs its own `combat_supply_loadout` +
  bank-run, so this is a real integration whose feel needs the live app and owner
  validation.

### 2f / 2g findings (2026-07-07) — earlier blocker notes

- **2f loot filter needs a runtime item→value table — and the extractor is
  environment-blocked (verified 2026-07-07).** `loot_should_pick_up` is built and
  tested, but it needs values for *drop* items. There is no name→cache_id map for
  drops (`ItemDefinition` carries a slug `id`, not the numeric cache id; enemy
  drops are keyed by name), so the value table must come from a cache dump that
  reads names directly. The Darkan cache, core jar, and dep jars are all present,
  **but the core jar is compiled for JDK 24 (class file v68) and this machine only
  has JDK 23/17/8 — running the dump throws `UnsupportedClassVersionError`.** So
  2f-a (the `ITEM_VALUES` dump) is blocked until JDK 24 is installed. 2f-b (route
  rolled combat drops through the filter) additionally needs combat to feed drops
  into a carried pack — combat uses `combat_supply_loadout` with its own bank-run,
  so this is a real integration, and its feel can only be verified in the live app.
- **2g ambush unify — reconsider.** `wilderness_shop_slots` counts *shop purchase*
  volume (28 bought → 1% ambush); the carried `churn` counts *skilling* slots.
  These measure unrelated flows; folding them into one accumulator would conflate
  buying with gathering. Recommendation: keep them separate (they already share the
  28 constant); do not force a merge. Revisit only if a unified "trip" concept
  emerges.

### Remaining slice-2 sub-slices (each its own tested commit)

- **2c — skilling bank-run state machine** (pure, mirrors combat; 1 review).
- **2d — handler-loop integration** in `on_good_answer`: consume-from-carried +
  bank-run interception + Keep/Drop, one processing skill first, then the rest.
- **2e — death drop:** extend the grave path to drop the carried subset
  (coins/quest items excluded) alongside equipment.
- **2f — loot filter application:** combat drops routed through
  `loot_should_pick_up`; picked-up loot enters the carried subset.
- **2g — ambush unify:** collapse `wilderness_shop_slots` into the carried-slot
  accounting.

Undo already snapshots `player_data` around a review (`_capture_player_data_snapshot`
in `on_answer_card`), so bank-run mutations roll back for free — verify, don't rebuild.

## The problem it solves

The number 28 already recurs everywhere as a shadow of the same missing
primitive: combat food loadout capacity (28), batch-28 utilities, the
"inventory-bounded bank run" rationale for tanning/sawmill, and the Wilderness
ambush's 28-slot accounting. A real 28-slot carried inventory is the model
those five constants are all approximating.

## Core decisions

1. **Teeth, for everyone (option A).** The 28-slot carry limit is a real
   constraint, not cosmetic — because a coal/gem/rune bag is worth *exactly*
   the cost of a bank run, and bags are content the owner wants. Without teeth,
   the whole system (and every bag) is inert.

2. **Overlay, not replacement.** The flat name-keyed inventory stays the source
   of truth (the bank = unlimited storage; zero risk to the parity price
   tables and the ~20 modules that read `inventory[name]`). The 28-slot grid is
   a *carried subset* — an ordering + capacity layer over the flat bank. This
   generalizes the existing `combat_supply_loadout` into one model used
   everywhere.

3. **Shared execution, swappable policy (this is the whole UX answer).** Bank
   runs *always auto-execute* — the player never opens a menu when the
   inventory empties (that would be "playing a game with learning on the
   side"). Default and advanced run identical machinery; they differ only in
   who decides the packing:
   - **Default (casual):** a **mode dropdown** of named preset packing
     strategies (e.g. balanced / max-food / max-materials) — not one opaque
     auto-manager, so each preset is individually inspectable and sane. The
     eat-queue is subsumed here (owner 2026-07-07): consume order falls out of
     the chosen mode. Transparency: the player sees e.g. "banked: 20 food /
     8 coal, +1 review."
   - **Advanced (opt-in):** the player sets the 4×7 layout / packing policy
     *once*; the system auto-executes it at every bank run. No per-depletion
     micromanagement. A smart layout (bags, food-vs-supply split, order) beats
     the dumb default.
   This mirrors how **combat already works today**: teeth exist for everyone
   (running out of food → bank run costs 2 reviews), auto-eat manages them at a
   decent-but-not-perfect default, and advanced players tune food priority /
   loadout. Advanced mode here is just *exposing the manual controls combat
   already half-hides*, extended to skilling — not a new concept.

4. **Advanced genuinely yields more XP/review.** The default auto-manager is
   deliberately modest (not optimal). An optimizer beats it — but by a **small
   gap** (target ~10-20% fewer bank-run reviews, never a 2x gulf that punishes
   casuals for not "doing homework").

5. **Input + output teeth (option B), unified.** Every session both draws from
   *and* deposits to the same 28 carried slots. Processing/combat drain it
   (food, supplies, materials); gathering fills it and banks when full. One
   model everywhere — and the canonical coal bag (mining) and gem bag finally
   have their home.

6. **Stackable rule (source-authentic, non-negotiable for bags to matter).**
   Stackables (runes, ammo, coins) occupy one slot regardless of count;
   unstackables occupy one slot each. Bags pack an otherwise-unstackable
   material (coal, gems) into a single slot — that is the entire value of a
   bag, and it only exists because of this rule. (The Wilderness ambush already
   reads the cache `stackable` flag; reuse it.)

7. **Every bank run costs a review (owner correction 2026-07-07 — no free
   banking).** A bank run costs review-answers everywhere, gathering included
   (combat keeps its existing 2; skilling starts at 1; tunable). This *sharpens*
   the Keep/Drop toggle below: Drop = never bank = never pay = fastest XP;
   Keep = pay bank-run reviews for materials. Bags reduce the number of bank
   runs, so they buy back reviews in every skill — which is exactly why gem
   bags (mining), coal bags (mining/smithing), and rune pouches all earn their
   keep.

8. **Gathering Keep/Drop toggle (per target).** Power-gathering vs collecting:
   - **Keep** (default): product goes to the carried grid, auto-bank when full
     (costs a bank-run review, per decision 7). You get materials.
   - **Drop:** no product, no banking, maximum XP/action. Bypasses the
     inventory entirely. This is the authentic power-mining / power-chopping
     choice and the real reason "some skills you bank, others you drop."

## Held-item requirements meet the toggle (the cannonball-mould rule)

Many actions require a *held item to be present* — the cannonball mould for
cannonball smithing, a chisel for gem cutting, a needle for leather, a
tinderbox for firemaking, etc. The carried-inventory toggle resolves "present"
cleanly:

- **Inventory management ON (advanced):** the required item must be in your 28
  carried slots — it occupies space, a real cost (bringing a mould means one
  fewer slot of coal).
- **Inventory management OFF (default):** "present" means "owned" — satisfied
  if the item is anywhere in the bank. No carry cost; the requirement is just
  a possession gate.

The toolbelt shrinks this: any belt-able tool (hammer, chisel, needle, knife,
tinderbox, gathering tools — the 2011 belt) needs no slot; only non-belt tools
(moulds, glassblowing pipe) are carried requirements. So the carried-tool
residual is tiny. Full map:
`memory-bank/source-audits/held-item-interactions-audit-2026-07-07.md`.

## Johari pass (2026-07-07) — the focused pre-code grill agenda

A one-round known/unknown pass surfaced four items beyond the original
"not-yet-decided" list. The implementation grill must cover, in priority order:

1. **Death + carried inventory (load-bearing).** RS drops carried inventory on
   death (except protected). AnkiScape's grave/death-office covers *equipment*
   only. Does the carried grid also drop on death, into the grave? Biggest open
   interaction.
2. **Undo snapshot for a bank run inside a review.** Bank runs mutate state and
   cost reviews *during* a card answer; Anki-undo must roll it all back. Known
   constraint, unsurfaced design.
3. **Unify (or separate) the carried-slot counter with the Wilderness ambush's
   existing 28 purchase-slot counter** — same number, different meaning; check
   for conflict.
4. **Quest items competing for carried slots** (RS quest-inventory pressure).

Plus the original known-unknowns: which preset modes exist; v1 bag roster +
capacities (source-audit each); exact skilling bank-run cost; grid UI
drag-vs-list; how it subsumes `combat_supply_loadout`; storage migration.

### Resolved (owner, 2026-07-07 — grill essentially complete)

- **Death drops the carried inventory** (into the grave, alongside equipment —
  extend the existing grave path from equipment-only to equipment + carried).
- **Undo rolls back everything** a bank run / consume touched (standard snapshot).
- **Wilderness ambush counter unifies** with the carried-slot model (same 28,
  one accumulator — collapse `wilderness_shop_slots` into the carry model).
- **Quest items stay abstracted** — they do not compete for carried slots.
- **Coins go in a Money pouch — zero carried slots.** The Money pouch released
  6 Dec 2011, ~2 months after the Oct-4 rev-667 baseline, so it is a clean
  **documented pre-EOC exception** (per the source hierarchy) rather than an
  invention. Adopting it means coins never occupy a carried slot, which is also
  what the owner wanted. Bank stays infinite. *Implementation (2026-07-07):* the
  pouch is not a separate coin store — coins stay canonical in the flat bank and
  are excluded from the carried grid and the death drop. See the foundation-slice
  note above.
- **Skilling bank-run cost = 1 review.** Flat, everywhere (combat keeps 2).
- **Per-target persistence:** the carried inventory is saved *per selected
  target*. Switching a target banks its loadout (free — a menu reorg, not a
  mid-session depletion) and restores/repacks the new target's saved loadout;
  only mid-session depletion refills cost the 1 review.
- **UI:** no drag-grid. Click items from the bank to fill a **collapsible
  carried-inventory side panel** next to the bank. Manual click-fill IS advanced
  mode; the saved layout auto-refills per target. Casual mode skips clicking via
  a preset dropdown (below).
- **Subsumes `combat_supply_loadout`** and the storage migration shape — both
  inferred at implementation time, not pre-specified.

### Loot drops (owner-decided 2026-07-07 — value-filtered pickup)

Loot **does** compete for carried slots (this reverses an earlier
over-simplification of "loot auto-banks with no slot cost" — that removed the
authentic "is this worth carrying?" tension). Pickup is auto-managed by a value
filter so the casual player never micromanages, but junk still carries a
perceived penalty (it would eat slots → earlier bank runs), so the filter
leaves it:

- **Default: high-alch-value filter.** A drop is picked up iff its high-alch
  value (`0.6 * cache value`, already extracted for shop pricing — no GE
  needed) is at or above a threshold. Below-threshold junk is left, so it never
  eats a slot. The threshold is a **declared AnkiScape balance knob** (tunable,
  not a source value).
- **Stackables are always picked up.** A stackable costs at most one slot ever,
  so there is no space penalty — grab it unconditionally (runes, ammo, charms;
  coins go to the Money pouch regardless). No filtering for that whole class.
- **Later: GE market value, optionally.** Same filter, swap the value metric
  from high-alch to market price once the GE exists — a one-line change.
- **Advanced: per-drop checkboxes.** Tick exactly which drops to keep/bank,
  overriding the threshold (e.g. "keep bones" once Prayer matters).

Consequences: loot picked up this trip is in the carried grid, so it drops on
death (authentic) and its accumulation contributes to triggering bank runs
alongside food/supply depletion. v1 is fully buildable now (cache value is in
hand).

### Preset modes (proposal — casual dropdown)

Presets only bite where categories compete (combat food/potions/supplies;
gathering-with-bags). For pure single-material processing they're moot (you
carry the one input). Proposed set — a small, honest three, implemented as one
pure `pack_carried_inventory_pure(player_data, target, mode)` that returns the
28-slot fill from the bank:

1. **Balanced (default):** pack required inputs, keep a safety reserve in combat
   (food covering the auto-eat threshold), fill the rest with the primary
   material. The sensible casual default.
2. **Max output:** no safety reserve — every free slot to the primary
   input/material for the most actions per bank run (in combat: minimal food,
   riskier, for when you out-gear the target).
3. **Max safety** (combat-meaningful): bias slots to food/potions, fewer
   supplies — survive tougher fights.

**Bags are not a preset choice** — they auto-apply whenever owned (strictly
better: pack an unstackable into one slot), under any mode. So the dropdown is
just the ratio strategy; the pack function consults owned bags automatically.

### Bag roster (audit 2026-07-07)

Present in the Oct-2011 cache (`items.yml`): **Coal bag**, **Gem bag**, **Bolt
pouch**. Absent (correctly): Money pouch, Rune pouch — later additions.

- **Coal bag** — v1 confident pick. Dungeoneering reward (skill launched Dec
  2010), holds 27 coal in one slot. Iconic mining/smithing bag.
- **Gem bag** — in the cache, but its *release date* is uncertain (may post-date
  Oct 2011). **Cross-check a runescape.wiki 2011 revision before shipping**; do
  not invent its capacity.
- **Bolt pouch** — Ranged ammo; relevant once Ranged carries bolts.

Recommendation: ship **Coal bag** in v1 (confident, iconic, 27-coal capacity),
defer Gem bag pending the wiki date check, and add Bolt pouch with the Ranged
ammo path. **Owner decision:** register + implement the Coal bag now and leave
it unobtainable (live-but-inert) until Dungeoneering or another source exists —
it lights up with zero changes when the source ships. No stopgap shop/token
source needed.

### Surfaced tacit assumptions (now explicit)

- **The carried inventory is skill-agnostic and persists across skill
  switches** — "combat loadout" and "skilling materials" are the *same* 28
  slots. This is the RS loop falling out for free (mine coal → switch to
  Smithing → forge from carried → bank when dry).
- Bank = infinite; only the carried grid is limited.
- Coins/currency are exempt from carried slots.
- Worn equipment is already outside the 28 (separate Equipment tab).

## Scope note

This is the flat-inventory-adjacent change the parity ledger flags as a
"standing adaptation" (flat name-keyed inventory). The overlay approach keeps
that adaptation intact — the grid is a view over the flat bank, so the price
tables and every module reading `inventory[name]` are untouched. That is the
whole reason overlay beats replacement.
