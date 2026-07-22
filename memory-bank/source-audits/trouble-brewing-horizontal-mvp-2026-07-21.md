# Trouble Brewing horizontal MVP harvest

Date: `2026-07-21`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period gameplay and reward economy source-closed; the owner-settled
bounded race is ready for horizontal implementation.**

## Period evidence

The literal wikitext of `Trouble Brewing`, oldid `6573931`, timestamp
`2012-11-18T20:43:05Z`, establishes:

- the `Cabin Fever` and level-40 Cooking entry gates;
- a non-combat twenty-minute team race with three boilers, ingredient stores,
  repair state, a score, and a source requirement of three players per team;
- one rum batch consuming one bitternut, one sweetgrub, five buckets of water,
  three bowls of coloured water, one scrapey bark, and three lit boilers with
  at least three logs each;
- bottle packing, including the loss of an uncollected bottle when another
  reaches the end of the line;
- two-way torch sabotage and the hopper, pipe, pump, tree, and bridge repair
  loop;
- exact task XP, two Pieces of Eight and `100` Crafting / `250` Cooking / `150`
  Firemaking XP per packed bottle, plus one Piece of Eight per contributed
  ingredient up to `100`; and
- the complete reward-shop names and prices.

Source:

- <https://runescape.wiki/w/Trouble_Brewing?oldid=6573931>

`Honest Jimmy's House of Stuff`, oldid `6399561`, timestamp
`2012-10-13T04:08:35Z`, independently pins the reward shop, including a
50-Piece tricorn hat, 100-Piece shirt and slacks, flags at 200–600, The stuff
at 5, and red/blue rum at 2:

- <https://runescape.wiki/w/Honest_Jimmy%27s_House_of_Stuff?oldid=6399561>

The dated Tip.It shop database says its prices were confirmed on `2012-05-16`
and lists the same catalog and prices:

- <https://www.tip.it/runescape/shops/view/312-honest-jimmys-house-of-stuff>

OpenRS2 rev-742 corroborates the representative live identities: Pieces of
Eight `8951`, Blue tricorn hat `8959`, Bitternut `8976`, Scrapey bark `8977`,
Sweetgrubs `8981`, and The stuff `8988`.

## Disclosed AnkiScape translation

The owning contract in `trouble-brewing-race-model-2026-07-18.md` already
settles a bounded duty race against a simulated opponent with two-way sabotage.
The source does not publish an opponent production curve, sabotage frequency,
or a discrete count of consequential decisions in twenty minutes. The
horizontal slice therefore discloses these `provisional/oldid-6573931`
parameters rather than claiming them as historical values:

- sixteen answered-card beats per game;
- opponent progress of one or two pips per beat, one rum at ten pips;
- a one-in-six opposing sabotage opportunity after the opening beats; and
- player sabotage removing three progress and suppressing two opponent beats.

Each successful review performs one complete source duty. `Again` performs no
player duty but the live brewing line and simulated opponent still advance.
Pending sabotage forces the next productive review into one repair duty. Casual
chooses the current bottleneck; Advanced selects the ordinary duty, while the
forced repair remains source-owned.

All temporary ingredients and equipment remain session state. This is the
same closed-temporary-economy boundary as Stealing Creation: the source's empty
inventory/head-slot requirement is represented by making global carried items
unavailable to the reducer rather than destructively moving the player's real
pack. Leaving clears the temporary race and forfeits its result.

The breadth reward catalog contains Blue tricorn hat only. It proves the exact
currency, direct purchase, bank, item-registry, asset, and equipment seams with
an authentic zero-stat wearable. The remaining colours, outfit pieces,
flags, rum teleport, medium clue purchase, and The stuff's mature-ale effect are
catalog or cross-feature depth, not omitted Trouble Brewing state transitions.

## Explicit omissions

- No wall clock, pathing, individual teammate, head-slot mutation, or global
  inventory transfer is added.
- The hidden sweetgrub, disease, monkey-fight, torch-extinguish, and object burn
  rolls remain later data depth; the owner-settled bounded race does not require
  fake exact rates.
- There is no invented winner currency bonus. The cutoff source pays from
  contribution and packed rum; win/loss remains a visible race result.
- Pirate implings and their `Rocking Out` gate are a later optional data family.
- No owner-facing design gap remains in this slice.
