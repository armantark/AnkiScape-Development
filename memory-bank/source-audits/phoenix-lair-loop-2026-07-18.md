# Phoenix Lair Review-Native Source Pin

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **breadth level one implemented. Period evidence, labelled
abstractions, and source-blocked values are separated below; both automated
lanes verify the complete loaded-add-on review chain.**

## Pinned period evidence

`Phoenix Lair`, oldid `6574295` (`2012-11-18T09:12:43Z`), establishes:

- completion of `In Pyre Need` and level 51 Slayer are required;
- the activity may be completed once per source day;
- five sequential caverns each contain a distinct tree whose twig must be cut;
- the five twigs are cut into ribbons and used to construct the Phoenix's pyre;
- the caverns contain Reborn guardians spanning the combat triangle, with at
  least one blocking encounter in each cavern;
- constructing the pyre summons the Phoenix for a mandatory boss fight;
- after the fight, the player lights the pyre and speaks to the reborn Phoenix
  to receive the reward;
- logging out, escaping, or teleporting before the pyre is lit resets the run;
- a repeat completion grants 7,500 Firemaking XP, 3,000 Fletching XP, 1,000
  Crafting XP, 500 Slayer XP, five Phoenix quills, and the collected guardian
  drops; the first Phoenix defeat grants 5,000 Slayer XP instead;
- completion has a chance to award a Phoenix egg;
- the egg may be obtained below level 72 Summoning, but hatching it in the
  cavern requires level 72; and
- clapping or kicking selects the Cute or Mean phoenix eggling respectively.

Source:

- <https://runescape.wiki/w/Phoenix_Lair?oldid=6574295>
- `Phoenix egg`, oldid `4364298` (`2011-06-05T00:56:14Z`):
  <https://runescape.wiki/w/Phoenix_egg?oldid=4364298>
- `Cracked phoenix egg`, oldid `4362222`
  (`2011-06-04T23:46:16Z`):
  <https://runescape.wiki/w/Cracked_phoenix_egg?oldid=4362222>

The breadth-one ledger below records which of the guardian, Phoenix, egg, and
day-boundary values are exact, which are explicit AnkiScape abstractions, and
which remain source-blocked rather than silently inferred.

## Settled platform boundaries

The once-per-day allowance resets through AnkiScape's 240-answered-card day,
never the wall clock. The five twigs, ribbons, and unfinished pyre are
session-local items and never enter the ordinary Bank.

Phoenix Lair is a non-resumable finite activity because the source reset the run
on logout or escape before pyre lighting. Viewing another page does not leave;
switching to another review target or explicitly abandoning the run requires
the shared destructive-leave confirmation and then clears all Lair state.

The Phoenix and the aggregate Reborn-guardian front both use the standard live
Combat reducer. The guardian front must not simulate cavern maps, choke points,
or individual background enemies. The source pet-egg choice is preserved
through the contextual review action surface when an egg drops; it does not
require a permanent setting.

## Final review-native run

The five cavern layouts differ spatially, but the required progress in each is
the same: pass the blocking guardians and cut the one mandatory twig. There is
no source route choice, distinct tool choice, or persistent resource decision
between those five repetitions.

The delegated owner decision is:

1. **Guardian front** — the five spatially repetitive cavern blockages become
   one persistent aggregate Reborn-guardian encounter derived from the exact
   five source rosters. Every successful review advances the ordinary live
   Combat reducer by `6 × M` ticks. Defeating the front cuts all five twigs and
   resolves the source-shaped guardian loot without instantiating five maps or
   background NPCs.
2. **Prepare the pyre** — one successful review cuts all five twigs into ribbons
   and builds the nest. This is one declared finite activity grouping; the
   source completion XP is not paid early.
3. **Defeat the Phoenix** — the ordinary live Combat reducer owns as many
   reviews as the encounter needs. The killing review atomically lights the
   pyre, speaks to the reborn Phoenix, consumes the daily completion allowance,
   and grants the fixed completion rewards.

Five separate cavern graphs would reenact spatial repetition without creating
five AnkiScape decisions. Grouping their actual Combat XP and attrition into one
instant traversal review would instead violate the live cadence contract. The
aggregate guardian front preserves the source roster's total encounter work and
loot through one visible combat state while keeping the spatial compression.

`Again` advances the global world clock but does not create twigs, apply
traversal attrition, prepare the pyre, or advance either Combat encounter.

## Requirements, real loot, and reset behavior

The start preflight requires:

- `In Pyre Need`;
- Slayer 51;
- the source knife, secateurs, and tinderbox through the ordinary toolbelt or
  carried-tool rules; and
- a Combat loadout that passes the shared encounter-readiness check.

This preflight is a direct UI check and consumes no review. The five twigs,
ribbons, and pyre are session-local. Real guardian drops and Combat XP are
credited when earned and remain real even if the player later abandons the run.

Death uses the shared PvM death and grave flow, places the grave outside the
activity boundary, and clears the unfinished Lair run. Explicit abandonment or
switching review targets uses the shared destructive-leave confirmation and
also clears the run. Neither failure consumes the daily completion allowance;
only the atomic pyre-lighting completion does. No pause or resume state exists.

All traversal, preparation, Combat, completion, daily-charge, loot, XP, pet,
and RNG mutations participate in the normal review/direct-action undo
boundaries.

## Phoenix eggling choice

A successful rare egg roll creates the contextual action:

**Phoenix egg — `Clap` / `Kick`**

- `Clap` selects the ordinary Phoenix egg and Cute phoenix eggling.
- `Kick` selects the Cracked phoenix egg and Mean phoenix eggling.
- An explicit choice is remembered for this context family.
- Ignoring the row until the next answered card uses the remembered valid
  choice, or `Clap` as the authored default.
- The same behavior applies in Casual and Advanced; there is no permanent
  checkbox.

At Summoning 72 or above, resolution grants the chosen eggling through the
shared pet-entity store. Below 72, it grants the corresponding unhatched egg as
an ordinary source-owned item; the shared Pets surface exposes its direct hatch
action automatically once level 72 is reached. Owning one temperament never
blocks acquiring the other. Exact repeat/duplicate-egg behavior remains
source-table work rather than justification to suppress the rare roll.

## Owner-design closure

Phoenix Lair has no remaining owner-facing product fork. The implemented route
pins the available source values, keeps unresolved depth explicitly labelled,
wires the fixed XP, quill, egg and eggling rewards, registers the real items and
period assets, and uses bounded abstractions only where the evidence ledger
below says so.

## Breadth-one evidence ledger

### Exact period evidence

The implementation treats only the following as exact period facts:

- `In Pyre Need`, Slayer level 51, a knife, secateurs, and a tinderbox are entry
  requirements. The ordinary AnkiScape carried-inventory policy decides whether
  an owned tool may remain in the Bank or must occupy the selected activity's
  carried pack; the source requirement itself is unchanged.
- Five cavern blockages, five twigs, ribbon cutting, pyre construction, the
  mandatory Phoenix fight, pyre lighting, and reward conversation are the
  source sequence.
- Escape, teleport, logout, or abandonment before completion resets unfinished
  ritual state without consuming the daily completion.
- Repeat completion grants exactly `7,500` Firemaking XP, `3,000` Fletching XP,
  `1,000` Crafting XP, `500` Slayer XP, and five Phoenix quills. The first
  completion substitutes exactly `5,000` Slayer XP.
- Level 72 Summoning gates in-cavern hatching. `Clap` selects the Cute eggling;
  `Kick` selects the Mean eggling. The level-below-72 egg items use cache IDs
  `14629` and `14630` from OpenRS2 revision 742.
- The six implemented Reborn guardian identities, combat levels, lifepoints,
  and combat-triangle styles are pinned individually to the historical page
  revisions named in `data/phoenix_lair_data.py`. The Phoenix identity, combat
  level `235`, `2,550` lifepoints, magic style, and approximate `290` maximum
  hit are pinned to `Phoenix` oldid `6588809`.
- Phoenix quill, Phoenix egg, Cracked phoenix egg, and both eggling art assets
  have recorded provenance in `assets_provenance.json`; registry and asset-path
  tests keep those files live.

### Labelled AnkiScape abstractions

These values are implementation abstractions and are not presented as exact
RuneScape values:

- `abstraction/review-day`: one source day is `240` answered cards. This is the
  settled shared AnkiScape world-day boundary, not a claim about wall-clock
  RuneScape time.
- `abstraction/spatial-compression`: the five repeated cavern blockages are one
  persistent aggregate guardian front. Five guardian variants are sampled from
  the six period identities, with replacement, to provide the smallest live
  combat roster that preserves five blockages.
- `abstraction/review-cadence`: one productive answer advances six live Combat
  ticks; one separate answer cuts the five twigs into ribbons and builds the
  pyre; the killing Phoenix answer also lights the pyre and claims the reward.
- `abstraction/combat-shape`: source-visible levels and lifepoints drive
  level-shaped attack, defence, magic, and ranged values where the hidden full
  stat block is unavailable. The aggregate front uses the summed guardian
  lifepoints.
- `abstraction/guardian-loot-slice`: the horizontal route preserves one Ashes
  item for each of the five compressed guardian blockages. Full guardian drop
  tables remain depth work.
- `abstraction/dust-cadence`: every fifth Phoenix review applies the sourced
  half-level dust effect. The review interval is disclosed rather than claimed
  as an exact attack timer.
- `abstraction/egg-roll`: the hidden completion roll is `1/1,000`. The UI and
  source string identify it as a bounded hidden-roll abstraction.
- `abstraction/atomic-finish`: lighting the pyre, speaking to the Phoenix,
  charging the day, paying XP and quills, and opening any egg choice are one
  review transaction so Anki undo can restore the pre-kill state exactly.

### `source_blocked` values

The breadth-one route does not invent the following unresolved depth:

- `source_blocked/guardian-composition`: exact per-cavern spawn composition and
  spatial pathing.
- `source_blocked/guardian-stats`: full hidden combat-stat and bonus blocks,
  exact attack speeds, and the Lesser reborn warrior's maximum hit.
- `source_blocked/guardian-drops`: complete quantity and probability tables
  beyond the minimal five-Ashes horizontal slice.
- `source_blocked/phoenix-stats`: the hidden full Phoenix combat-stat and bonus
  block and exact attack speed.
- `source_blocked/dust-timing`: exact wall-clock or attack-cycle timing for the
  Phoenix dust special.
- `source_blocked/egg-chance`: the exact Phoenix egg probability and duplicate
  egg behavior.

None of these values blocks the settled entry → guardians → preparation →
Phoenix → reward → daily-charge → undo route. They remain labelled depth work.

## Breadth-one implementation closure

The entry preflight now follows the shared held-item policy instead of treating
Bank ownership as universal. In casual inventory mode, Bank ownership or the
2011 toolbelt satisfies each tool. In advanced inventory mode, the toolbelt or
the saved `carried_layout["phoenix_lair"]` satisfies it; entry materializes that
layout into `carried_inventory["phoenix_lair"]`, capped by the 28-slot limit and
real Bank ownership. The loaded Activities menu now exposes Phoenix Lair as the
active carried-pack target. Its lock copy reports the active rule, so an
advanced player sees `carried pack or toolbelt` rather than a misleading Bank
gate.

A loaded-add-on integration test now enters through the real Activities
callback, dispatches three successful answers through the reviewer path,
exercises guardian clearance, preparation, Phoenix completion, rewards and the
same-day lock, then undoes the killing review and compares the entire save with
the pre-completion snapshot. Focused pure, runtime, direct-action, write-through,
asset, and offscreen Qt checks remain in place. No owner design fork is present.

Final verification on canonical main passed both complete lanes: `python3
run_tests.py` ran `2,723` tests with `332` declared skips, and the real offscreen
Qt discovery command ran the same `2,723` tests with one declared skip.
