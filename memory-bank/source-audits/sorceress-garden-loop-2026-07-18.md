# Sorceress's Garden Review Loop

Date: `2026-07-18`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Pinned period evidence

- `Sorceress's Garden` oldid `6466752`
  (`2012-10-24T20:04:59Z`) establishes four level-gated seasonal gardens,
  elemental stealth, one fruit or two random grimy herbs per successful trip,
  immediate return to the central garden after harvesting, Farming XP, fruit
  requirements `5/4/3/2`, and juice hand-in/drinking benefits:
  <https://runescape.wiki/w/Sorceress%27s_Garden?oldid=6466752>.
- `Sq'irkjuice` oldid `6520647` (`2012-11-02T13:02:44Z`) establishes that juice
  consumes the appropriate fruit count plus an empty beer glass, uses a pestle
  and mortar, can be handed to Osman or drunk, and that the Sorceress's-house
  cupboard provides an infinite free supply of beer glasses:
  <https://runescape.wiki/w/Sq%27irkjuice?oldid=6520647>.
- `Tool belt` oldid `6538396` (`2012-11-06T01:19:10Z`) lists pestle and mortar
  as a tool-belt item and states that all non-quest belt tools were
  automatically present after the `2012-03-13` update:
  <https://runescape.wiki/w/Tool_belt?oldid=6538396>.
- `Summer sq'irk` oldid `6520800` (`2012-11-02T13:28:52Z`) identifies juice as
  the fruit's only period use:
  <https://runescape.wiki/w/Summer_sq%27irk?oldid=6520800>.

The pinned pages do not award XP for squeezing fruit. A local Darkan
reconstruction adds `5 Herblore XP`, but without cutoff corroboration that is a
source conflict, not authority for an extra skill reward.

## Resolved design implications

- Herbs and fruit are legitimately competing garden outputs: the source allows
  one fruit **or** two herbs before teleporting the player out.
- Free beer-glass retrieval is incidental activity setup, not a purchase,
  inventory grind, or review action.
- Pestle and mortar is ambient through the cutoff tool-belt contract.
- Unsqueezed fruit has no meaningful strategic use. It is only staging state
  until the sourced `5/4/3/2` threshold is reached.
- Squeezing should therefore not become a separate review-bearing processing
  activity. A successful fruit trip adds one real fruit; reaching the threshold
  automatically consumes the fruit and an abstracted free glass and produces
  one real juice. Any stranded fruit from a changed setting remains real and
  is processed automatically when a complete threshold becomes available.

## Settled review and UI contract

Do not combine harvest destination and juice disposition into one dropdown.
The settled surface is:

1. **Harvest:** Fruit / Herbs / Alternate evenly.
2. **Completed juice:** Hand to Osman automatically / Keep as juice.

The juice control is relevant only when Fruit or Alternate can produce juice.
No manual squeeze or Osman-dialogue action consumes a review.

One successful review resolves one attempt through the selected seasonal
garden. A caught player returns to the central garden with no output, no damage,
and no extra recovery review. A successful attempt awards the source Farming XP
and then:

- **Fruit** picks one fruit;
- **Herbs** picks two source-rolled grimy herbs; or
- **Alternate** switches between those two outputs after each successful
  harvest. Failed attempts never advance the alternation.

Fruit remains a real carried item only until its seasonal `5/4/3/2` threshold.
At that threshold it automatically consumes the fruit and an abstracted free
beer glass and produces one real juice using the ambient tool-belt pestle and
mortar. **Hand to Osman automatically** immediately consumes completed juice
for its exact source Thieving XP; **Keep as juice** retains the item for its
temporary Thieving and run-energy effect.

The remaining source/design work is the automatic route-failure abstraction:
the source makes capture a movement/timing consequence rather than publishing a
simple success rate.
