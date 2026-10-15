# Gnome Restaurant delivery loop at the pre-EOC cutoff

Date: 2026-07-17

Status: **closed 2026-07-28.** The harvest, the conflicts it resolved and every
value the implementation ships now live in
`gnome-restaurant-harvest-2026-07-28.md`. The owner-settled abstraction below is
unchanged and still governs; the "still open" list at the end is answered there.

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
until it is delivered or deliberately declined. Under the owner ruling of
2026-10-14 at22:49 PDT, Again earns nothing and spends no delivery window.
Each successful answer on another target spends six minutes while an order
is open. A dish prepared and banked before assignment delivers on time.
Punctuality affects tip quality only: it never destroys the order, consumes
prepared food, or removes the source-authentic base delivery points.

The reducer stores the active order and bounded punctuality. It performs no
wall-clock expiry, background route simulation or per-minute replay.

Easy and hard orders retain their source-distinct customer pools, requirements,
base points, and reward tables. Cooking continues to own the gnome recipe
chains, and previously player-prepared banked items remain valid inputs exactly
as the period source permits.

The source tutorial remains a one-time eight-item checklist: its four prescribed
gnome dishes and four prescribed cocktails must each have been prepared by the
player. Ordinary Cooking production satisfies the checklist, including
qualifying production recorded before the player opens Gnome Restaurant. The
Activity must read durable player-production facts rather than duplicate the
recipes, consume eight tutorial-only reviews, or require an established player
to remake food solely to replay NPC instruction.

## Still open for source harvest or later grill — all answered 2026-07-28

Each line below is settled in `gnome-restaurant-harvest-2026-07-28.md`. The
tutorial line needed a correction rather than an answer: the pinned revision says
"four different gnome dishes" and "four different cocktails", so the count is
sourced and the prescribed list never existed. The presentation fork is queued as
design decision 3.19 with a recommendation, implemented.

- Corroborate the timer, point, token, customer, and reward claims against an
  independent period-lineage source.
- Identify and corroborate the exact four tutorial dishes and four cocktails.
- Transcribe the complete cutoff customer pools, route requirements, and reward
  tables, including customer-specific rewards.
- Resolve the source hard-order decline wait through the answered-card clock.
- Decide the Activity's compact order and reward presentation after the data
  surface is known.
