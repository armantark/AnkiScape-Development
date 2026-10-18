# Gnome Restaurant and gnome cooking: implementation harvest

Date: 2026-07-28
Cutoff: `2012-11-20T00:00:00Z`

Status: **harvest closed.** This record supersedes the open items in
`gnome-restaurant-delivery-loop-2026-07-17.md` and supplies every value the
breadth-one build ships. Values that no source states are registered
placeholders, listed at the end and in `memory-bank/placeholder-values.md`.

## Pinned sources

| id | what it settles | reference |
| --- | --- | --- |
| `GR` | delivery loop, order pools, points, token thresholds, complete tip tables | `Gnome Restaurant` oldid 6491107 (2012-10-28T20:51:36Z) |
| `GC` | equipment, ingredient routes, per-dish ingredient lists, the two-stage bake | `Gnome cooking` oldid 6438943 (2012-10-18T22:02:41Z) |
| `COOK` | the complete twenty-row level/XP/healing table | `Cooking` oldid 6548144 (2012-11-11T16:17:12Z) |
| `TOKEN` | reward-token semantics, meal accrual, reclaim, random food type | `Reward token (Gnome Restaurant)` oldid 6117402 (2012-08-20T10:58:52Z) |
| `BOX` | the delivery box reminder item | `Aluft aloft box` oldid 6082000 (2012-08-12T22:30:44Z) |
| `SNR` | the dish tutorial and the 100 free Gianne dough | `Aluft Gianne snr.` oldid 6221695 (2012-09-09T19:18:08Z) |
| `BLUR` | the cocktail tutorial range, fruit blast up to short green guy | `Blurberry` oldid 6222077 (2012-09-09T19:34:38Z) |
| `GM` | gnome food healing values and live item ids | `game-main` (2011Scape rev 667) `content/items/food/Food.kt`, `api/cfg/Items.kt` |
| `ITEMS` | every item id and exact period item name | `game-main` `data/cfg/items.yml` |
| item pages | per-dish level, XP, healing, cocktail stat effects | individual oldids cited in `data/cooking_data.py` |

Darkan carries no Gnome Restaurant or gnome cooking implementation: its
`skills/cooking/Foods.java` holds only heal rows, and several of those are for the
retired `22xx` item generation rather than the live one. game-main has no gnome
cooking action either. Both were searched; the absence is recorded, not assumed.

## Exact values shipped

**Recipes.** `GC` and `GR` agree row for row on all twenty ingredient lists,
including which ingredients go into the mould, tin, tray or shaker first and which
are added to the part-baked dish. AnkiScape collapses the period's multi-click
assembly into one Cooking action whose requirements are the union of both stages,
exactly as the existing pie and pizza prep bridges collapse their assemblies.
The period's intermediate items (`Half made batta`, `Unfinished bowl` and friends)
are therefore not modelled; that is deferred depth, disclosed here and in the
Cooking data source strings.

**Levels, XP, healing.** `COOK` is the only source that covers all twenty rows,
and its XP column is monotone in level (50, 70, 100, 100, 100, 100, 110, 120,
150, 152, 154, 156, 158, 170, 160, 170, 175, 180, 185, 190). Levels are
6/8/10/12/14/16/18/20/25/26/27/28/29/30/32/33/35/37/40/42.

**Healing** comes from `GM`'s `Food.kt`, which lists the live `21xx`/`22xx` item
ids with 120/70/80/70 for the crunchies, 110 for every batta, 120/120/150/150 for
the gnomebowls. Every one of those agrees with the dedicated item page.

**Cocktail effects**, each from its own item page: Wizard blizzard +6 Strength
−4 Attack, Short green guy +4/−3, Drunk dragon +7/−4, Choc saturday +7/−4,
Blurberry special +7/−5. Fruit blast and Pineapple punch are non-alcoholic and
carry no effect.

**Delivery loop.** Easy jobs stay in and around the Grand Tree with a six-minute
limit; hard jobs go anywhere in Gielinor with an eleven-minute limit; declining a
hard job costs a five-minute wait; delivered food must be player-prepared and may
be banked in advance; every easy delivery pays one point and every hard delivery
three; twelve points pays a Reward token and each further twelve adds one banked
food item up to ten; activating the token resets the banked count to zero and the
token can be reclaimed free if lost.

**Order pools.** Nineteen easy customers and twenty hard customers, both
complete. Hard access requirements are exact: Troll Romance for Brambickle,
Fishing Contest for Captain Ninto, Monkey Madness progress for Garkor, The Grand
Tree progress for G.L.O. Caranock, The Giant Dwarf for Professor Manglethorp, and
Magic 66 for Professor Imblewyn.

**Tips.** Easy deliveries pay 10-500 coins. Hard deliveries pay from six sourced
groups with exact quantity ranges, and five of those rows are customer-locked:
Gnome goggles and Gnome scarf only from Captain Ninto and Captain Daerkin, Snake
charm only from Wingstone, Gold ore and Coal only from Professor Manglethorp, Raw
oomlie only from Penwie, and the seven runes plus Pure essence only from Professor
Imblewyn and Professor Onglewip.

## Conflicts and their resolution

1. **Batta XP.** `COOK` gives 150/152/154/156/158 across the five battas. The
   Vegetable batta page says 161 and the Cheese and tomato batta page says 150,
   which would make XP fall as the level requirement rises. `COOK` wins: it is
   internally monotone, it is the newest pre-cutoff revision, and the two item
   pages contradict each other rather than the table alone.
2. **Chocchip crunchies XP.** `COOK` says 100 for all four crunchies; the item
   page itemises 30 + 30 + 46 = 106. `COOK` wins for the same reason, and the
   106 breakdown is recorded here rather than shipped.
3. **Healing.** `COOK`'s healing column says Toad crunchies heal 80 and Fruit
   blast heals 90. The item pages say 120 and 80, and `GM` independently
   confirms 120 for Toad crunchies. So healing takes the item pages plus `GM`
   while XP takes the table. The split is deliberate: for XP the table is the
   consistent witness, for healing it is the outlier.
4. **The tutorial checklist.** The 2026-07-17 audit read the tutorial as four
   *prescribed* dishes and four *prescribed* cocktails. `GR` says "four different
   gnome dishes" and "four different cocktails", and `SNR` describes a succession
   rather than a fixed list, so the count is sourced and the list is not. The gate
   ships as four distinct dishes and four distinct cocktails. `BLUR` corroborates
   that the cocktail half runs from Fruit blast up to Short green guy, which is
   the four lowest-level cocktails and exactly what a player below level 32 can
   make anyway.
5. **Item generation.** Two item generations share these names. `GM` uses the
   `21xx`/`22xx` ids for every live gnome dish, so those are the ids recorded.
   The `94xx`/`95xx` block holds the Restaurant's own additions: Reward token
   9474, Mint cake 9475, Gnome scarf 9470, Gnome goggles 9472, Aluft aloft box
   9477.

## AnkiScape translations, disclosed

- **One review is one delivery.** Fixed earlier by
  `activity-cadence-reconciliation-2026-07-18.md`: delivery is one no-skill-XP
  activity action. The 2026-10-14 owner rule makes Again idle; successful reviews
  on other targets spend their card's time budget (six ticks per unit of game
  speed, owner assumption 4 of 2026-10-15) from the persistent delivery window.
  The delivering review also accepts the next job, so the loop does not need
  a direct action between deliveries.
- **The six- and eleven-minute limits become a punctuality budget, not an
  expiry.** The owner settled in 2026-07-17 that an order never expires. The
  order carries the source's own minutes as a bounded counter of game ticks
  (600 and 1,100). Under the 2026-10-14 owner ruling, each successful review on
  another target spends its card's ticks, so the easy window is ten cards at
  x10. Again and delivery spend none. At zero, the tip is at its worst;
  the order, prepared food and source base points remain intact.
- **The five-minute hard-order decline wait is 500 ticks**, spent by every
  answered card's time budget.
- **Declining an easy job is free.** Only the hard-order wait is sourced; the
  page's own advice to take an easy job while waiting for a hard one implies easy
  jobs can be swapped freely.
- **Requests are not level-filtered.** No source restricts the requested dish by
  Cooking level, and `COOK` attests that the tutorial itself assigned dishes the
  player could not yet cook, so the draw covers all twenty items and the player
  declines what they cannot make.
- **Cocktail stat effects use a flat-level drink consumable** rather than beer's
  percentage model, because the sourced values are flat levels.

## Registered placeholders

| id | stands in for |
| --- | --- |
| `gnome_restaurant.request_weights` | which of the twenty items an order asks for; the period weights are unstated and item pages call some orders "semi-rare" |
| `gnome_restaurant.tip_weights` | the roll inside a tip group, and the quantity inside each sourced range |
| `gnome_restaurant.good_tip_curve` | how punctuality converts into the chance of the good-tip group |
| `gnome_restaurant.token_food_weights` | the token's food draw, where the only sourced fact is that drinks are rarer than dishes |

## Art

Every sprite this family fetched is a pre-cutoff upload, recorded in
`assets_provenance.json`, and the Cooking fetcher now resolves against the
full upload history before the cutoff rather than the newest file. Two gaps
remain and neither is fixable from the wiki: `Bird's nest` has no pre-cutoff
upload under any of its titles, so that tip row ships without art, and
`Choc saturday` has none either.

One pre-existing condition is worth naming rather than hiding. A few gnome items
already had shop sprites fetched in 2021 without the cutoff check, and
`EXTRA_ITEM_IMAGES` merges the shop images after the Cooking ones, so those items
display the older post-cutoff sprite even though a pre-cutoff file now sits in
`cookingitems/`. That merge order is shared by every family and is the measured
post-cutoff art condition recorded as design-queue item 5.2; it is not changed
here.

## Deferred depth

The period intermediate assembly items; the Gnome Restaurant tutorial as a
playable NPC sequence rather than a production checklist; per-customer travel
routes, teleport requirements and the quests that only make a delivery *faster*;
premade shop food remaining unusable for deliveries (already true, since premade
items are separate items); and the Chocchip crunchies step-XP breakdown.
