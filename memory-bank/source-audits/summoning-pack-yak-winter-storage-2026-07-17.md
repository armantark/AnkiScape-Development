# Pack Yak Winter Storage source audit (2026-07-17)

Scope: pin the pre-EOC special-move behavior and isolate the remaining AnkiScape
automation choice. Cutoff is 2012-11-20.

## Pinned period source

**Pack yak**, oldid
[6462316](https://runescape.wiki/w/Pack_yak?oldid=6462316),
2012-10-24 00:27:15 UTC.

The literal wikitext records a level-96 familiar with a 30-slot Beast-of-Burden
inventory, a 58-minute lifetime, and Winter Storage. The scroll row gives 4.8 creation XP,
4.8 use XP, and a 12-point special cost. The move is used on an item in the player's
inventory and instantly banks it without visiting a Bank. The page explicitly describes
this as extending time in an area. A scroll used on noted items banks only one item, not
the whole stack.

## Existing AnkiScape constraints

Summoning contract decision 8 already settles that an eligible special:

- fires only on a successful answer;
- consumes one matching deliberately carried scroll and exact special-move points;
- awards exact use XP; and
- is configured more precisely in Advanced without becoming a free direct UI command.

Target route/rate metadata must also declare whether Pack Yak or Winter Storage is already
assumed. The special cannot independently discount a rate that already includes it.

## Settled AnkiScape trigger

The source defines what one activation does but not when Casual should spend it in a
review-driven target:

1. **Proactive:** bank each configured eligible target output as it is produced.
2. **Full-pack boundary:** carry outputs normally, then bank one configured eligible item
   on the successful review where the pack would otherwise force a Bank trip.

The owner selected the full-pack boundary. Casual does not proactively bank every output.
On the successful review where the carried pack would otherwise force a Bank trip, it uses
one carried scroll and 12 special points to bank one configured eligible item, awards 4.8
use XP, and continues the target action atomically. If no configured eligible item, scroll,
or points are available, the ordinary Bank trip occurs.

Advanced may configure item priority and an earlier threshold. Both modes retain the exact
one-scroll/one-item source transaction, and target route metadata declares whether Winter
Storage is already assumed to prevent a second trip-rate discount.
