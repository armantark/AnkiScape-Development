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
