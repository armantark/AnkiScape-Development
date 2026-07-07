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

267 live coin shops (2,695 priced rows), 4 processing services (Ellis tanning,
sawmill planks), 4 vendor purchases, and Death's Office reclaim
(100 Coins/item).

## Honest exclusions

- Items whose local `items.yml` marks `tradeable: false` stay unsellable even
  when 2011-era live-game behavior differed (e.g. `Chinchompa`); the local
  source is the authority.
- The registry's quest-catalog pseudo-items (scraped reward phrases, plurals,
  place names) are marked tradeable by default but are not real inventory
  outputs; they are outside the sellability guarantee. The guarantee is pinned
  to representative real outputs by
  `tests/test_shop_logic.py::test_primary_skill_outputs_sell_at_general_stores`.

## Verification

- `python3 -m unittest tests.test_shop_logic tests.test_shop_data`
- `tests/test_shop_logic.py::test_gather_sell_buy_coin_loop_end_to_end` proves
  the coinless gather → sell → buy loop with history events on both legs.
- Full suites re-run at the end of the integration pass.
