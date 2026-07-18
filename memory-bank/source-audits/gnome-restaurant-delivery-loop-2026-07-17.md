# Gnome Restaurant delivery loop at the pre-EOC cutoff

Date: 2026-07-17

Status: **period structure pinned; deadline translation owner-settled;
implementation corroboration and reward-table harvest remain open.**

## Pinned evidence

The literal wikitext of `Gnome Restaurant`, oldid `6491107`,
`2012-10-28T20:51:36Z`, establishes:

- the introductory tutorial asks the player to prepare four gnome dishes and
  four cocktails before the delivery service opens;
- the player chooses an easy or hard order;
- easy orders stay around the Tree Gnome Stronghold and have a six-minute
  source limit, while hard orders may go anywhere in Gielinor and have an
  eleven-minute source limit;
- declining a hard order imposes a five-minute source wait before another hard
  order;
- delivered food must be player-prepared, but it may be prepared and banked
  before the order is assigned;
- fast deliveries improve the chance of a good tip;
- easy deliveries award one point and hard deliveries award three; and
- each twelve points grants a reward token, after which subsequent twelve-point
  thresholds add another delivered food item, banked up to ten.

Source:

- <https://runescape.wiki/w/Gnome_Restaurant?oldid=6491107>

The revision was resolved and inspected as literal wikitext with
`tools/wiki_parity.py`. These source-stated values still require an independent
period-lineage corroboration pass before implementation. The hard-order
customer requirements and complete period reward tables also remain to be
transcribed rather than inferred from the modern page.

## Owner-settled AnkiScape abstraction

The six- and eleven-minute source deadlines do not become literal wall-clock
timers or one- and two-review hard expirations. An accepted order persists
until it is delivered or deliberately declined. Each `Again` answered while
the order is outstanding lowers a bounded, clamped punctuality state used only
to determine the eventual tip quality. It never destroys the order, consumes
the prepared food, or removes the source-authentic base delivery points.

This makes the established `Again`-as-AFK world-time rule visible without
making a short source timer depend on frantic UI interaction. The reducer
stores only the active order and its bounded punctuality state; it performs no
background route simulation or per-minute replay.

Easy and hard orders retain their source-distinct customer pools, requirements,
base points, and reward tables. Cooking continues to own the gnome recipe
chains, and previously player-prepared banked items remain valid inputs exactly
as the period source permits.

## Still open for source harvest or later grill

- Corroborate the timer, point, token, customer, and reward claims against an
  independent period-lineage source.
- Transcribe the complete cutoff customer pools, route requirements, and reward
  tables, including customer-specific rewards.
- Resolve the source hard-order decline wait through the answered-card clock.
- Decide the Activity's compact order and reward presentation after the data
  surface is known.
