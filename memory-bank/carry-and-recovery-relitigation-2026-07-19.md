# Carry-model and Combat-recovery relitigation

Date: `2026-07-19`

Status: **owner-settled; closes the two genuine forks from the Sol
relitigation audit of pre-kernel design docs.**

## 1. Bank-run teeth: sourced-rate selection

Replaces the 2026-07-07 carry model's universal "every bank run costs a
review" rule, which double-counted banking on routes whose sourced XP/hour
already includes it:

- Carry choices (packing, Keep/Drop, banking vs dropping) **select between
  sourced rate rows** — the period record usually publishes distinct banked
  and powertrained rates, and the player's choice picks which authentic row
  applies. That is the model's teeth, with zero invention.
- Bags and capacity change XP/review **only where a period source attests
  their rate effect** (e.g., the coal bag at the Blast Furnace). Elsewhere
  they buy item-side value only: more loot kept per trip, fewer forced
  interruptions.
- Routes whose sourced rates exclude banking keep the charged bank-run
  review exactly as today.

## 2. Off-route Combat recovery: world-clock recovery

Replaces the dead 50-ticks-per-review conversion:

- Between encounters, Combat resources (LP, special energy, run energy, and
  any other real-time-regenerating pool) recover on the 240-cards/day world
  clock at their **sourced real-time rates** — matching the 2012 reality that
  between-fight recovery was trivial background time.
- Inside a live encounter, the 6-tick combat clock governs exclusively:
  world-clock recovery never applies mid-fight; it flows only while no
  encounter is engaged.
- Neither freezing (invented punishment) nor per-review tick recovery
  (invented scarcity) is permitted.

Both rules carry the standard follow-through: sourced rates pinned per the
verification standard, and parity tests asserting the with/without behavior
at the first implementing route.
