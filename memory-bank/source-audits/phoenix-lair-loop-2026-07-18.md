# Phoenix Lair Review-Native Source Pin

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period source pinned; cavern compression under owner grill.**

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

Exact guardian rosters and drops, Phoenix combat data, egg chance, first-kill
reward lineage, and source-day completion boundary remain implementation-source
work.

## Settled platform boundaries

The once-per-day allowance resets through AnkiScape's 240-answered-card day,
never the wall clock. The five twigs, ribbons, and unfinished pyre are
session-local items and never enter the ordinary Bank.

Phoenix Lair is a non-resumable finite activity because the source reset the run
on logout or escape before pyre lighting. Viewing another page does not leave;
switching to another review target or explicitly abandoning the run requires
the shared destructive-leave confirmation and then clears all Lair state.

The Phoenix itself uses the standard live Combat reducer. Guardian passage may
apply a single bounded, visible traversal consequence, but the implementation
must not simulate cavern maps, choke points, or individual background enemies.
The source pet-egg choice is preserved through the contextual review action
surface when an egg drops; it does not require a permanent setting.

## First owner fork: cavern compression

The five cavern layouts differ spatially, but the required progress in each is
the same: pass the blocking guardians and cut the one mandatory twig. There is
no source route choice, distinct tool choice, or persistent resource decision
between those five repetitions.

The recommendation is one **Traverse the five caverns** review beat. Its result
line names the five twigs, guardian passage, and any bounded LP/resource
consequence. One subsequent **Prepare the pyre** review cuts all five twigs into
ribbons and builds the nest. The next state starts the ordinary Phoenix Combat
encounter; the killing review atomically lights the pyre and grants the
completion reward.

Five separate cavern reviews would reenact spatial repetition without creating
five AnkiScape decisions. Two grouped traversal reviews would split the
difference numerically without gaining a source or product rationale.
