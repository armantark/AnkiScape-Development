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
- `Prince Ali Rescue` oldid `6564887` (`2012-11-17T04:11:58Z`) records Garden
  access as a quest reward, but also records that the quest was removed on
  `2012-09-26`. `Talk:Sorceress's Garden` oldid `6307582`
  (`2012-09-27T20:26:25Z`) asks whether the replacement quests inherited the
  prerequisite and contains no answer. The cutoff Garden article likewise
  states the Osman/apprentice introduction but no quest prerequisite. A
  `Diamond in the Rough` requirement first appears in the article after the
  cutoff.

The period documentation trail does not independently close that migration,
but the owner has supplied high-confidence firsthand cutoff memory that
`Diamond in the Rough` inherited the prerequisite. AnkiScape therefore uses
completion of `Diamond in the Rough` as the product gate. This is explicitly an
owner-resolved historical gap rather than a claim that the pinned article
stated the replacement gate.

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

One successful non-`Again` review resolves one attempt through the selected
seasonal garden. An `Again` is the caught-player outcome: the elemental returns
the player to the central garden with no output, no damage, no partial
progress, and no extra recovery review. A successful attempt awards the source
Farming XP and then:

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

## Crowd and capture abstraction

The activity assumes a busy public world as narrative framing. The pinned
cutoff page describes heavy bot infestation and elemental capture behavior,
while the owner's period play memory supplies the familiar crowd-cover scene.
That scene does not become a simulated population.

- Every non-`Again` answer succeeds. The result line may say that the
  elementals were occupied chasing other players while this route got through.
- `Again` is the attention failure already owned by Anki grading and is
  narrated as an elemental catch.
- Do not add a catch roll after a correct answer, a crowd-density selector,
  stored population, per-elemental target allocation, pathing, or background
  work. Those would duplicate the grading signal without adding a player
  decision.

This is a labeled AnkiScape abstraction, not a claim that every attentive
cutoff run succeeded.

## Entry gates

The four seasonal gardens retain exact Thieving gates `1/25/45/65`. Starting
the activity requires completion of `Diamond in the Rough` followed by its
one-time Osman/apprentice introduction state. The replacement gate is
owner-resolved as described above and indexed in
`activity-entry-gate-ledger-2026-07-18.md`.

## Implementation closure — 2026-07-20

The complete settled review loop is live in `sorceress_garden_data.py`,
`sorceress_garden_logic.py`, `runtime_actions.py`, and `ui.py`. Storage schema
55 persists the one-time introduction, season, harvest policy, juice policy,
fruit staging counts, and alternation state. The ordinary herb pool stops at
dwarf weed and deliberately excludes Dungeoneering herbs. Because the pinned
source provides no herb weights, the equal distribution remains the labeled
bounded abstraction recorded above rather than fabricated parity.

The item registry contains all four fruits and juices. Kept juice restores the
exact sourced run-energy percentage, applies its sourced temporary Thieving
boost, and leaves a beer glass. Automatic Osman hand-in awards the exact
Thieving XP. Review and direct commands use their established independent undo
paths, and the cadence ledger declares one complete route per successful
review without applying the foreground multiplier.

The Activities surface uses a compact selected card and a one-category pager;
Utilities remains separate. Kimi K3 and Fable reviewed both new surfaces. The
accepted fixes cover locked-row legibility, persistent mechanics/tradeoff copy,
fruit progress, visible-but-disabled juice policy, selection restoration,
content-measured height, false disclosure affordances, and accessibility.

Verification covers pure mechanics, runtime dispatch, migration, undo,
registry, cadence, reachability, focused real Qt, full non-Qt, full offscreen
Qt, and a fully restarted native Anki dark-mode smoke. The exact closure counts
and screenshot result live in
`status-updates/sorceress-garden-horizontal-mvp-results-2026-07-20.html`.
