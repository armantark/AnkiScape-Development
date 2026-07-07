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

## Gathering and processing source rolls (now source-exact)

The first pass misread the helper family; the corrected picture, now
implemented exactly:

- **MiscExt.kt 3-arg interpolate** (Mining, Woodcutting):
  `floor(low*(99-lvl)/98 + floor(high*(lvl-1)/98) + 1)`, success on
  `interp > nextInt(255)` -> probability `interp/255`. Implemented in
  `_scape2011_interpolate_255`.
- **MiscExt.kt 5-arg Boolean interpolate** (Fishing cap 255, iron smelting
  cap 100): integer-division linear interpolation, success on
  `nextInt(cap) <= interp` -> probability `(interp+1)/cap`. Iron smelting is
  therefore exactly 51%..81% (not the nominal 50..80); fishing crayfish at
  level 1 is 59/255.
- **Mining pickaxe ratio**: the source chance is ratio-free — the pickaxe
  sets roll cadence (`ticksBetweenRolls`). AnkiScape folds cadence into the
  per-action chance (`interp * ratio / 255`) as a **declared adaptation** of
  the one-roll-per-review model; Woodcutting's ratio genuinely scales the
  chance inputs in source (`(low*ratio).toInt()`), matched exactly.
- The old linear un-floored forms under-rolled by up to ~1pp; all four roll
  functions were made source-exact on 2026-07-07 and the affected pinned
  expectations updated (crayfish 59/255, iron 0.51/0.66/0.81).

- **Hunter** (`Utils.skillSuccess`, bytecode-verified): chance =
  `int(rate1 + (rate99 - rate1) * level / 99)` clamped 0..256, success on
  `nextInt(255) <= chance` -> `(chance + 1)/255`. Ours used `(level-1)/98`
  over 256 — made source-exact 2026-07-07.
- **Cooking and Firemaking** both use the 3-arg floor/+1 helper with
  `interp > nextInt(255)` — made source-exact via
  `_scape2011_interpolate_255` (shrimps level 1 is 129/255; normal logs
  66/255), pinned expectations updated.

All seven probabilistic source rolls (mining, woodcutting, fishing, hunter,
cooking, firemaking, iron smelting) are now exact ports of their engine
formulas; the only remaining transform is the declared sqrt pacing adapter.

## Standing adaptations (by design, not deviations)

One review = one action tick; actions-per-review multiplier; batch-28
utilities; 10 answered cards = one market tick; combat bursts simulate 50
source ticks; flat name-keyed inventory (canonical-id price tables absorb the
id ambiguity); no spatial world/banking/travel; Anki-undo snapshots.

## Combat recovery / special energy (closes the sweep)

- **Special attack regen**: Darkan restores 10% every 50 ticks
  (`Player.java` tick loop -> `CombatDefinitions.restoreSpecialAttack`,
  base 10; auras unimplemented). Ours is `10 per 50 ticks` pro-rated across
  burst ticks — identical in expectation, continuous-vs-stepped cadence is
  the standard declared adaptation. **parity**
- **Safe-boundary recovery packets** (food/potion/ammo/rune refills between
  fights): no engine counterpart exists — real players bank manually — so
  this is an **adaptation** by definition, not a formula to diverge from.
  Its own QA baseline is the 2026-06-25 hardening pass.

## Sweep status: complete

Every mechanics-glue surface is classified. Inventions found and fixed:
sell-price heuristics (2026-07-06), the landed-hit damage roll, and the
seven skilling rolls' interpolation semantics (2026-07-07). When adding new
mechanics code, cite the engine line for every constant and pin it with a
stable-id-keyed test, or classify the behavior here.
