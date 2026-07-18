# Fish Flingers Review Loop

Date: `2026-07-17`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Pinned period evidence

`Fish Flingers` oldid `6529096` (`2012-11-03`) establishes a recurring
multiplayer D&D with no level, quest, or item requirement; temporary bait,
hook, and weight controls; six species across four locations; rating feedback
used to deduce optimal tackle; communal depletion; cooperative big fish;
Fishing-level-scaled XP; two daily tickets capped at ten held; medals, tokens,
and a reward shop:

<https://runescape.wiki/w/Fish_Flingers?oldid=6529096>

The earlier provenance summary is
`memory-bank/source-audits/gap-grill-13-fishing-provenance-2026-07-10.md`.

## Settled AnkiScape abstraction

The source's tackle deduction survives as a visible automatic efficiency ramp,
not as controls the player must babysit:

- neither Casual nor Advanced exposes bait, hook, or weight selection;
- the first three successful reviews all produce catches;
- those reviews successively discover bait, hook, and weight, visibly raising
  catch efficiency until the third review reaches full efficiency;
- the exact intermediate efficiency percentages are labeled AnkiScape balance
  values rather than source claims;
- stock depletion automatically rotates species or location;
- a fixed communal depletion pressure replaces simulated competitors; and
- any cooperative big-fish opportunity is captured automatically inside the
  triggering review using the public-event baseline.

Persist only the bounded state that affects a later result: event progress,
discovery step, current stock/rotation, score, and earned reward counters. Do
not persist competitors, tackle candidates, search history, or background
workers. All changes are answered-card-driven and undoable.

## Open design value

The event's total successful-review length remains owner-open. The recommended
shape is six reviews: one compact sweep matching the source's six species,
including the three-review discovery ramp and three reviews at full efficiency.
