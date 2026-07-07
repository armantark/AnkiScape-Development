# Coin Economy Audit

Generated: 2026-07-06 (shop-economy integration pass, stage 2)

## Question

With 267 live coin shops spending coins, can a player actually earn them —
and does every legitimate income route resolve instead of failing closed?

## Income routes (all source-backed)

- **Combat drops:** 55 of 94 implemented combat targets carry `Coins` in their
  imported drop tables (goblins, guards, barbarians, humanoids broadly).
  Source: per-target local 2011Scape drop tables recorded in the combat source
  audits.
- **General-store sales:** general stores buy any tradeable item. Stocked
  items use their stock row's Shop.java sell price; **unstocked items resolve
  through the new generated `SHOP_PLAYER_SELL_PRICES` table** (6,736 names) —
  `ItemDefinitions.sellPrice` plus the coin sell enum override for every
  tradeable 2011 item, extracted by `tools/DumpDarkanShopPriceInputs.java`
  from the Darkan cache. Names shared by several item ids keep the lowest
  resolved price so aliasing can never inflate a payout.
- **Specialist-shop sales:** specialist shops still buy only their own stock
  (unchanged fail-closed policy).
- **Vendor sales:** `bartender_sell_beer_glass` (Darkan
  `BartenderUtils.sellBeerGlass`).

## The gap this pass fixed

Before this pass, `shop_logic._sell_price_for_item` resolved sell prices only
by scanning shop stock rows, so common gathered outputs that no shop stocks —
Oak/Willow logs, Bones, Iron bar, Leather, Cowhide, Wool, Flax, furs — were
denied with `sell_price_unresolved`. Income was effectively limited to items
that happened to appear in some shop's stock. The generated fallback table
closes that gap at the backend layer; Qt is unchanged.

## Spend routes

267 live coin shops (2,695 priced rows), 4 coin-paid Utility conversions
(Ellis tanning at 1/3 Coins per hide, sawmill planks at 100/250 Coins per
log), 4 instant vendor actions (Bartender, Benny, Karim), and Death's Office
reclaim (100 Coins/item).

## Pacing decision: conversions are review-paced, not shop services

The tanning/sawmill conversions briefly shipped as instant Shop-tab services
and were deliberately converted to no-XP `material_processing`
Utility/Activities (batch 28, coins consumed per unit): 2011 conversion runs
were inventory-bounded at 28 unstackable items per bank run, and the review
loop is AnkiScape's stand-in for that friction. An instant "Use x1000" button
would have deleted source pacing while every comparable conversion (smelting,
cooking, `make_soft_clay`) already runs through reviews. `SHOP_SERVICES` stays
as an empty fail-closed contract slot for future genuinely instant services.
Do not re-litigate this by moving conversions back into the Shop tab.

## Arbitrage guard

`SHOP_PLAYER_SELL_PRICES` is clamped at each name's cheapest live shop buy
price at generation time: the flat name-keyed inventory merges every item id
sharing a name, so a cheap custom-priced stock row (Rasolo's 1-coin Poison)
plus a high cache sellPrice on a same-named id would otherwise mint coins in
a buy/sell loop. Equality (zero-profit round trips) stays — that is what the
authentic Shop.java math produces for value-1 items and spirit shards.
Pinned by `tests/test_shop_data.py::test_no_strict_buy_sell_arbitrage_in_live_stock`.

## Honest exclusions

- Items whose local `items.yml` marks `tradeable: false` stay unsellable even
  when 2011-era live-game behavior differed (e.g. `Chinchompa`); the local
  source is the authority.
- The registry's quest-catalog pseudo-items (scraped reward phrases, plurals,
  place names) are marked tradeable by default but are not real inventory
  outputs; they are outside the sellability guarantee. The guarantee is pinned
  to representative real outputs by
  `tests/test_shop_logic.py::test_primary_skill_outputs_sell_at_general_stores`.

## Alchemy relationship (for the future noncombat Magic slice)

All shop prices key off the same cache `value` field that alchemy uses:
buy price = `value` (+ coin enum override), high alch = `value x 0.6`, low
alch = `value x 0.4` (2011Scape `magic/alchemy/alchemy.plugin.kts`
`coinModifier`), and the shop-pays `sellPrice` usually sits below low alch
(Swordfish: 400 buy / 240 high / 160 low / 120 shop). Alchemy is therefore
the item-value floor and the reason the parked GE design is "alch-anchored".
Nature runes are already live shop stock at 372 Coins (Baba Yaga's,
Lundail's, Magic Guild), which makes alching low-value items a coin sink —
authentic. **Guard required when alch ships:** the payout is `0.6 x value`,
but custom-priced stock rows can sell far below value (Rasolo's 1-coin
Poison), so alch payouts must be clamped or verified against live shop buy
prices exactly like `SHOP_PLAYER_SELL_PRICES`, or buy-to-alch mints coins.

## Verification

- `python3 -m unittest tests.test_shop_logic tests.test_shop_data`
- `tests/test_shop_logic.py::test_gather_sell_buy_coin_loop_end_to_end` proves
  the coinless gather → sell → buy loop with history events on both legs.
- Full suites re-run at the end of the integration pass.
