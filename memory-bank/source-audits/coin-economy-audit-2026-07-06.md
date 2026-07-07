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
- **General-store sales:** general stores buy any tradeable item at the
  generated `SHOP_PLAYER_SELL_PRICES` price (6,820 names) — Shop.java
  `getSellPrice` for each name's canonical item id, extracted by
  `tools/DumpDarkanShopPriceInputs.java` from the Darkan cache (see the sell
  parity section below for the canonical-id rule).
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

## Sell parity (supersedes the earlier arbitrage clamp)

Owner decision, 2026-07-06 (later the same day): sell mechanics follow Darkan
`Shop.java` exactly. `SHOP_PLAYER_SELL_PRICES` / `SHOP_PLAYER_BUY_PRICES` are
`getSellPrice` / `getBuyPrice` for each name's canonical item id (the id live
shop stock uses, else the lowest tradeable id) — cache price floored 0->1,
coin enum override wins, identical at every shop. The earlier name-minimum
rule, live-buy clamp, and vendor divide-by-3 buyback heuristic are removed as
inventions. Additional engine behaviors implemented for parity: the currency
item itself cannot be sold (`currency_item`), general-store player-sold stock
occupies a 40-minus-main-stock slot pool that refuses new items when full
(`shop_full`), sold-into-main-stock overstock decays toward the row's default
rather than zero, and player-sold stock buys back at the engine's
`getBuyPrice`. The feared Poison flip does not exist under true parity: the
canonical Poison id is the one Rasolo stocks, and its own cache sellPrice is
1, so the buy-1/sell-1 round trip pays nothing. Pinned by the parity tests in
`tests/test_shop_data.py` and `tests/test_shop_logic.py`.

## Alchemy relationship (for the future noncombat Magic slice)

All shop prices key off the same cache `value` field that alchemy uses:
buy price = `value` (+ coin enum override), high alch = `value x 0.6`, low
alch = `value x 0.4` (2011Scape `magic/alchemy/alchemy.plugin.kts`
`coinModifier`), and the shop-pays `sellPrice` usually sits below low alch
(Swordfish: 400 buy / 240 high / 160 low / 120 shop). Alchemy is therefore
the item-value floor and the reason the parked GE design is "alch-anchored".
Nature runes are already live shop stock at 372 Coins (Baba Yaga's,
Lundail's, Magic Guild), which makes alching low-value items a coin sink —
authentic. **Decision needed when alch ships:** the payout is `0.6 x value`,
and custom-priced stock rows can sell far below value (Rasolo's 1-coin
Poison), so buy-to-alch can profit. In the real engine that loop exists too,
bounded by stock per restock interval — under the absolute-parity stance the
bound is the review-paced market clock, but audit the worst custom-price rows
before accepting it.

## Verification

- `python3 -m unittest tests.test_shop_logic tests.test_shop_data`
- `tests/test_shop_logic.py::test_gather_sell_buy_coin_loop_end_to_end` proves
  the coinless gather → sell → buy loop with history events on both legs.
- Full suites re-run at the end of the integration pass.
