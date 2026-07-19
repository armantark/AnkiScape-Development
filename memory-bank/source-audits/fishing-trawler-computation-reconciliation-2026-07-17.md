# Fishing Trawler Computation Reconciliation

Date: `2026-07-17`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

## Pinned period evidence

`Fishing Trawler` oldid `6288357` (`2012-09-24T04:51:16Z`) establishes a
level-15 safe team minigame with a twelve-minute trip, swamp-paste leak repair,
rope net repair, reusable bailing buckets, water and sinking pressure, an
activity requirement, a level-shaped catch on success, Fishing XP equal to 40%
of the catch's ordinary XP, and no haul after sinking:

<https://runescape.wiki/w/Fishing_Trawler?oldid=6288357>

The broader period audit remains
`memory-bank/source-audits/gap-grill-13-fishing-provenance-2026-07-10.md`.

## Reconciled AnkiScape contract

Fishing Trawler remains a finite persistent activity because water, leaks, net
damage, supplies, remaining phases, and haul quality all affect later duties,
costs, success, or rewards. One successful review resolves one useful duty and
one bounded pressure transition. A sunk trip awards no haul, matching the
pinned source.

The crew is deliberately not simulated as state:

- every trip automatically receives one competent public-crew baseline;
- crew help is a fixed pressure offset applied inside the same atomic review
  reducer as the player's duty;
- there is no crew-size selector, per-crew-member state, crew contribution
  meter, background loop, or wall-clock work;
- Casual automatically selects the most urgent useful duty its carried supplies
  permit;
- Advanced may save the player's own duty preferences and carried layout, but
  never asks the player to recruit, size, or manage a crew.

This retains the source's cooperative pressure fantasy without spending
computation on actors that the player cannot meaningfully inspect or influence.
All transitions remain answered-card-driven and undoable.

## Trip granularity (owner-settled 2026-07-18)

A trip is **event-scaled**, not duration-scaled. Mapping the source
twelve-minute trip literally through `R = 1000` would cost ~200 eligible
reviews per haul — most of a 240-card day for one payout with sinking risk
throughout — so the trip length is instead the count of consequential source
pressure events: leak clusters, net rips, and bailing junctures, harvested
from oldid `6288357` and emulator evidence, expected on the order of ten duty
reviews. This compression is a labeled AnkiScape abstraction following the
Pyramid Plunder room-budget and Fish Flingers six-review precedents; the
source timer was wall-clock presentation, and the consequences it produced
(pressure, supplies, haul, the 40% XP rate) survive the compression.

- The haul and its 40%-of-ordinary Fishing XP pay out at trip end, scaled so
  XP per review preserves the source rate through the cadence kernel.
- Sinking remains a real outcome: unrepaired pressure across the trip's events
  can sink it for zero haul, matching the pinned source.
- The exact event count is harvest work, not a further owner question. If the
  period record cannot attest per-trip event counts, derive them from the
  pinned pressure cadence and record the derivation as
  `provisional/<source>`; never present the count as historically closed.
