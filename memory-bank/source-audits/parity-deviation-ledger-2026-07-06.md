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

## Combat burst engine (audited vs Darkan CombatFormula.kt)

| Area | Finding | Class |
| --- | --- | --- |
| Accuracy probability | `1-(def+2)/(2*(atk+1))` / `atk/(2*(def+1))` — exact match | parity |
| Attack/defence rolls | `(floor(level)+style+8) * (bonus+64)` with +3 accurate / +1 controlled — exact match | parity |
| Melee/ranged max hit | old-HP `0.5 + eff*(bonus+64)/640` x10 == Darkan LP `5 + strLvl*(strBonus+64)/64`, same style structure | parity |
| Landed-hit damage roll | Darkan rolls `Utils.random(1, maxHit)` = `1 + nextInt(maxHit-1)`: uniform 1..maxHit-1, never 0, never max (verified by bytecode disassembly of core-2.0.5.jar). Ours rolled 0..max-1, allowing 0-damage landed hits — **fixed** in `_combat_roll_damage_lifepoints` and pinned by `test_combat_landed_hit_damage_matches_darkan_random_semantics` (it previously had zero coverage) | fixed invention |
| Prayer multipliers / combat-mod plugins | Prayer unimplemented => multiplier 1.0 is exact for a prayer-less player; slayer-helm-style modifier plugins out of scope | adaptation |
| Engagement cadence | Player attacks at tick 0 then every weapon-speed ticks; enemy offset by its own speed; auto-eat is AnkiScape's stand-in for manual eating | adaptation |

## Gathering source rolls

Weights match everywhere (`low*(99-lvl)/98 + high*(lvl-1)/98`, ratio-scaled
inputs for WC), but the shared 2011Scape helper (`MiscExt.kt:51`) is
`floor(low*(99-level)/98 + floor(high*(level-1)/98) + 1)` and success is
`RANDOM.nextInt(cap) <= interp`, i.e. probability `(interp + 1)/255` — our
mining/woodcutting/fishing rolls use the un-floored linear form with plain
`/255`, so they systematically under-roll by roughly 2/255 (~0.8pp) plus
flooring nuances. Classified **declared approximation** for now (the rolls
feed the sqrt pacing adapter with a 0.20 floor, which dwarfs the delta);
an exactness fix needs per-skill verification of where each source applies
the tool ratio before the floor. Fishing (`Fish.kt:77` roll cap 255) and
Hunter remain to be walked.

## Standing adaptations (by design, not deviations)

One review = one action tick; actions-per-review multiplier; batch-28
utilities; 10 answered cards = one market tick; combat bursts simulate 50
source ticks; flat name-keyed inventory (canonical-id price tables absorb the
id ambiguity); no spatial world/banking/travel; Anki-undo snapshots.

## Not yet line-audited (scoped follow-ups)

1. **Fishing/Hunter source-roll formulas** — same spot-check Woodcutting and
   Mining received.
2. **Cooking burn curves and Smithing iron 50-80% curve** — implemented from
   audits at build time; a re-verification pass is cheap insurance.
3. **Combat recovery packets / special-energy regen** — the burst core is now
   audited (see above); the safe-boundary recovery glue is the remaining
   combat surface.

Follow-up prompt: audit each area against the Source Hierarchy, add a ledger
row per finding, pin every source constant with a test keyed on stable ids.
