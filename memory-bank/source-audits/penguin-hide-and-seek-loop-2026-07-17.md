# Penguin Hide and Seek at the pre-EOC cutoff

Date: 2026-07-17

Status: **period structure pinned; search and travel abstraction owner-settled;
implementation corroboration and roster harvest remain open.**

## Pinned evidence

The literal wikitext of `Penguin Hide and Seek`, oldid `6569778`,
`2012-11-17T23:47:37Z`, establishes:

- the ordinary weekly activity tracks ten penguin spies;
- Larry, or Chuck after `Hunt for Red Raktuber`, supplies regional hints;
- the ordinary penguins use disguises and roam, while player clans and forum
  threads commonly publish sightings and help trap them;
- `Cold War` upgrades five ordinary penguins from one point to two;
- `Hunt for Red Raktuber` adds a one-point polar-bear agent;
- `Some Like It Cold`, together with the required `Desert Treasure` progress
  and ring of visibility, adds a three-point invisible penguin;
- the resulting weekly maxima are 10, 15, 16, or 19 points according to those
  quest unlocks;
- points may be redeemed for 6,500 coins each or chosen-skill XP equal to
  `25 × current skill level × points`; and
- Larry or Chuck stores at most 50 unspent points.

Source:

- <https://runescape.wiki/w/Penguin_Hide_and_Seek?oldid=6569778>

The revision was resolved and inspected as literal wikitext with
`tools/wiki_parity.py`. The values and cutoff roster still require an
independent period-lineage corroboration pass before implementation.

## Owner-settled AnkiScape abstraction

Penguin hunting is completely flattened. At each answered-card weekly reset,
the Activity creates the source-authentic eligible roster and exposes each
penguin's current source location directly. Selecting a roster entry abstracts
all travel and starts one atomic review action; the next successful Activity
review travels to the named location, spies that penguin, awards its points,
and marks it complete.

There are no Larry/Chuck hint deductions, broad-area searches, discovery rolls,
community-sighting mode, roaming NPCs, trapping, multiplayer simulation,
persistent player location, or transport legs. The result line names the
location and disguise so the flattened action still communicates what happened.
Inactive rosters perform no work.

The weekly roster, quest gates, point values, point cap, and redemption options
remain source-shaped. Weekly eligibility follows AnkiScape's answered-card
calendar and never the wall clock. Every successful spy and redemption remains
an atomic undoable delta.

## Still open for source harvest

- Corroborate the weekly counts, quest upgrades, point values, point cap, and
  redemption formulas against an independent period-lineage source.
- Transcribe the complete cutoff location and disguise pools.
- Reconcile any cutoff weekly-location dependency pages and historical
  templates used by the article.
- Map chosen-skill XP redemption through the shared reward-choice interface
  without changing the source formula.
