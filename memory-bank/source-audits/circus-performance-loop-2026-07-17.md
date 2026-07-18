# Big Top Bonanza at the pre-EOC cutoff

Date: 2026-07-17

Status: **period structure and quest gates pinned; atomic performance grouping
owner-settled; success and costume-score harvest remains open.**

## Pinned evidence

The literal wikitext of `Balthazar Beauregard's Big Top Bonanza`, oldid
`6554790`, `2012-11-14T06:58:34Z`, establishes:

- the Circus is a safe weekly activity with three base performances: Magic,
  Ranged, and Agility;
- `The Firemaker's Curse` unlocks two additional Firemaking performances,
  fire-breathing and flaming poi;
- `Some Like It Cold` unlocks the Thieving magic-tricks performance;
- Magic, Ranged, Agility, and Thieving allow ten tricks per weekly performance,
  while each Firemaking performance contains six;
- tricks have suggested level bands rather than hard requirements, may fail,
  and award zero XP on failure;
- XP and Circus score are distinct: XP favors successful level-banded tricks,
  while costume score also responds to entertainment factors such as variety,
  audience requests, emotes, and costume;
- Balthazar awards circus costume pieces according to performance score; and
- abandoning a performance closes only that skill's performance for the week,
  while unplayed performances remain available.

Source:

- <https://runescape.wiki/w/Balthazar_Beauregard%27s_Big_Top_Bonanza?oldid=6554790>

The revision was resolved and inspected as literal wikitext with
`tools/wiki_parity.py`. The article contains conflicting summary totals for at
least the Agility routine, and its score discussion explicitly leaves some
factors unconfirmed. Derived totals and rumored equipment effects are therefore
not parity evidence.

## Owner-settled AnkiScape grouping

Each whole skill performance resolves in one successful review, not one review
per trick. The atomic reducer evaluates only the source-bounded routine for that
performance: at most ten tricks, or six for either Firemaking act. A complete
weekly visit therefore takes three reviews before quest unlocks and up to six
after both quest families are available, rather than 30–52 reviews.

Before each performance, the player selects one of three strategies:

- **Max XP** prioritizes the source trick levels and success profile;
- **Entertain for costume** prioritizes variety, requests, and score; or
- **Balanced** compromises between the two.

Casual exposes those three strategies and builds the bounded routine
automatically. Advanced may edit the exact trick lineup, but the lineup still
resolves as one atomic performance review. The result names notable tricks and
failures, then reports total XP, Circus score, and any costume reward. It does
not simulate an audience, persist individual spectators, or run background
work.

Selecting a performance configuration merely arms it. Only the successful
review commits and consumes that weekly performance; an `Again` before
resolution advances ordinary world state but is not reinterpreted as logging
out of the Circus. Undo restores the performance eligibility and every XP,
score, and reward delta together.

The two Firemaking performances use the ordinary `The Firemaker's Curse` quest
gate. Thieving uses the ordinary `Some Like It Cold` quest gate. These entries
exist as normal source-backed performances and begin working automatically when
their quest completion facts exist; no substitute unlock is invented.

Weekly availability follows AnkiScape's answered-card calendar and never the
wall clock. The rotating city is named as scene context, while ticket collection
and travel are flattened into entry and create no persistent location system.

## Still open for source harvest

- Transcribe and independently corroborate every cutoff trick, level band, and
  XP value for all six performances.
- Resolve the success curves, barely-success behavior, repeat-XP rules, audience
  requests, and the complete costume-score model through the evidence hierarchy.
- Transcribe the complete costume catalog and score thresholds, separating
  confirmed effects from period rumors.
- Reconcile the article's conflicting per-performance and weekly XP totals.
- Map the atomic source routine through cadence without treating one grouped
  review as ten unrelated skilling reviews.
