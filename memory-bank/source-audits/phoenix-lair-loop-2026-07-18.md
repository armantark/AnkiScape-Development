# Phoenix Lair Review-Native Source Pin

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **owner-design loop closed; period source, compressed traversal,
non-resumable session, Combat handoff, rewards, and eggling choice settled.
Exact source-table harvesting remains.**

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

Exact guardian rosters and drops, Phoenix combat data, egg chance, first-kill
reward lineage, duplicate-egg behavior, and source-day completion boundary
remain implementation-source work.

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

Phoenix Lair has no remaining owner-facing product fork. Implementation must
still pin the source work named above, wire the fixed XP and quill rewards,
attach the guardian and Phoenix combat/drop tables, register the temporary and
real items, and provide period assets. Missing numeric evidence may use only a
labeled bounded abstraction that preserves this settled loop.
