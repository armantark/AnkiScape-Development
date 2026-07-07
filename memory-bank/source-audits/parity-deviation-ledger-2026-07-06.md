# Parity Deviation Ledger

Generated: 2026-07-06. Classifies mechanics-glue behavior (code, not data
tables — those carry per-row `source` citations) as **adaptation** (Anki-model,
by design), **declared** (documented simplification of a source mechanic), or
**invention** (unjustified — fixed or escalated).

## Audited this pass

| Area | Finding | Class |
| --- | --- | --- |
| Shop sell/buy mechanics | Rebuilt to exact `Shop.java` parity earlier today (uniform getSellPrice/getBuyPrice, currency guard, 40-slot pool, decay-to-default); the ÷3 buyback, name-min prices, and live-buy clamp were removed as inventions | fixed inventions |
| Shop restock | `restock_amount` is 1 for every generated row — matches `ShopItem.tickRestock`'s strict one-unit steps; the field is a knob but unused | parity |
| Review-odds adapter | `normalize_review_success_probability_pure` = `0.20 + sqrt(source) * 0.72`, cap 0.95. Inputs are exact source per-tick rolls; the sqrt curve is AnkiScape's pacing transform (telemetry pass 2026-06-20). This is THE pacing knob — tune here, never in per-skill data | adaptation |
| Mining source roll | `low + (high-low)*(lvl-1)/98`, `/255` — matches `Mining.kt` interpolate | parity |
| Dragon pickaxe bonus | Source (`Mining.kt:59-71`): +0.2 accumulator per swing, every fifth swing rolls again at 1.12x base. AnkiScape folds the 1.12 into every roll (continuous instead of every-fifth-swing — slightly generous at the margin). Was keyed on a `"dragon" in display_name` string with no test; now keyed on cache item id 15261 and pinned by `test_dragon_pickaxe_source_bonus_applies_by_item_id` | declared (was unflagged) |
| Arithmetic-literal sweep | `runtime_actions.py` and `shop_logic.py` contain no remaining unexplained arithmetic literals | clean |

## Standing adaptations (by design, not deviations)

One review = one action tick; actions-per-review multiplier; batch-28
utilities; 10 answered cards = one market tick; combat bursts simulate 50
source ticks; flat name-keyed inventory (canonical-id price tables absorb the
id ambiguity); no spatial world/banking/travel; Anki-undo snapshots.

## Not yet line-audited (scoped follow-ups)

1. **Combat burst engine glue** — per-target data is audited, but attack
   cadence, auto-eat ordering, recovery packets, and special-energy regen have
   never been compared line-by-line against the source combat scripts. This is
   the largest remaining surface.
2. **Woodcutting/Fishing/Hunter source-roll formulas** — they feed the shared
   adapter like Mining; each `*_source_roll_chance_pure` should get the same
   spot-check against its source plugin that Mining got here.
3. **Cooking burn curves and Smithing iron 50-80% curve** — implemented from
   audits at build time; a re-verification pass is cheap insurance.

Follow-up prompt: audit each area against the Source Hierarchy, add a ledger
row per finding, pin every source constant with a test keyed on stable ids.
