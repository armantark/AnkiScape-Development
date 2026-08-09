# Trouble Brewing horizontal MVP harvest

Date: `2026-07-21`

Cutoff: RuneScape immediately before EOC, `2012-11-20`.

Status: **period gameplay and reward economy source-closed; horizontal
implementation verified on 2026-07-21.**

Superseded for catalog depth on `2026-08-09`: all 27 cosmetic and flag rows are
live. See `trouble-brewing-cosmetic-catalog-2026-08-09.md`; the historical
single-Blue-tricorn statements below describe the original breadth slice.

## Period evidence

The literal wikitext of `Trouble Brewing`, oldid `6579342`, timestamp
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
  ingredient, including boiler logs, up to `100`; and
- the complete reward-shop names and prices.

Source:

- <https://runescape.wiki/w/Trouble_Brewing?oldid=6579342>

`Honest Jimmy's House of Stuff`, oldid `6393015`, timestamp
`2012-10-13T04:08:35Z`, independently pins the reward shop, including a
50-Piece tricorn hat, 100-Piece shirt and slacks, flags at 200–600, The stuff
at 5, and red/blue rum at 2:

- <https://runescape.wiki/w/Honest_Jimmy%27s_House_of_Stuff?oldid=6393015>

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
horizontal slice therefore discloses these `provisional/oldid-6579342`
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

## Live implementation

- The complete sixteen-beat race is wired through the Activities registry,
  persistent activity ownership, schema-73 migration, Casual bottleneck and
  Advanced fixed-duty policies, two-way sabotage, forced repair, boilers,
  brewing, bottle loss, opponent scoring, leave/forfeit, review undo, and
  direct-action undo.
- Exact duty and packed-bottle XP is awarded on the review that performs the
  source action. Leaving therefore preserves already-earned skill XP while
  forfeiting only unfinished match state and its terminal Pieces-of-Eight
  settlement.
- The representative Blue tricorn hat is a reachable zero-stat head item with
  normalized period art, direct purchase, inventory/bank ownership, and live
  equipment registration.
- The compact paginated Activities card exposes the gates, policy, live score,
  duty progress, reward wallet/shop, selection, and explicit leave action.
- The runtime never reads wall-clock time. `Again` advances the shared brewing
  race and opponent pressure without performing a player duty or awarding
  player-duty XP.
- Kimi K3 remained quota-gated and the installed Claude CLI was not
  authenticated for Opus, so the required external taste passes could not be
  obtained. Root visual QA used the real dark-palette Qt renders at
  `/tmp/ankiscape-trouble-brewing-ui/`; this is an external-review availability
  note, not a product-design gap.
- Closure results are recorded at
  `status-updates/trouble-brewing-horizontal-results-2026-07-21.html` and
  <https://r8gg5tai8i28.postplan.dev>.

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
