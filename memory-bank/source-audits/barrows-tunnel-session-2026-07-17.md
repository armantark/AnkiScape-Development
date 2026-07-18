# Barrows tunnel session at the pre-EOC cutoff

Date: 2026-07-17

Status: **source shape pinned; bounded nine-room review-native graph
owner-settled.**

## Pinned evidence

The literal wikitext of `Barrows`, oldid `6555680`,
`2012-11-14T21:42:58Z`, establishes:

- the crypt is a three-by-three grid of nine rooms;
- the player begins in a randomly chosen outer corner room;
- locked routes and the one usable central-room door vary by run;
- the central door presents a puzzle, and a wrong answer rearranges the
  catacombs;
- aggressive crypt monsters occupy the tunnels;
- undefeated brothers may appear when doors or the chest are opened;
- the player may loot early with reduced Barrows-item odds;
- leaving before taking the reward preserves brother and creature kill counts
  so the player can return later; and
- leaving during a brother fight resets that brother fight.

Source:
<https://runescape.wiki/w/Barrows?oldid=6555680>, inspected as literal wikitext
with `python3 tools/wiki_parity.py content "Barrows"`.

## Owner-settled AnkiScape shape

Generate one bounded nine-node graph for the run. Persist only consequential
state: current room, revealed and usable doors, central-door access, slain
brothers, tunnel kill count, active encounter, chest state, and reward claim
state.

One successful review resolves the current room transition and any attached
encounter through the existing Combat cadence. Casual automatically chooses a
route toward the central chest. Advanced chooses among currently revealed
doors. Inactive runs do not advance, and there are no autonomous monsters,
background traversal, or per-room worker loops.

The source puzzle survives only as narrated scene detail. Reaching the usable
central door resolves it automatically inside the successful room transition.
There is no puzzle interface, separate command, answer choice, failure roll, or
reshuffle consequence in either mode. The graph's door topology still supplies
the route uncertainty that matters to the review-native session.

The source explicitly supports leaving and returning before claiming the chest,
so this session may suspend with its exact consequential state. A brother fight
interrupted by leaving still resets in accordance with the source.

This graph follows
`memory-bank/simulation-computation-budget-contract-2026-07-17.md`: it is a
small persisted state machine, not a hidden dungeon simulation.
