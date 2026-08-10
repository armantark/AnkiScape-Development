# NPC Shop Backend Source Audit

Generated: 2026-07-06

## Sources

- Darkan shop JSON: `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/shops`
- Darkan cache price inputs: `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-cache`
- 2011Scape item names/tradeability: `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`
- 2011Scape shop model and Darkan shop model were used as behavior references for stock, restock, price policy, general-store sell policy, and player-sold temporary stock.

## Coverage

- Source shop files: 274
- Runtime shops: 273
- Visible shops: 270
- Locked/read-only shops: 2
- Hidden shops: 1
- Stock rows: 2771
- Period-source-excluded stock rows: 5
- Live stock rows: 2721
- Locked stock rows: 37
- Hidden stock rows: 0
- Blocked stock rows: 13
- Services: 83
- Vendor actions: 4

## Disposition Policy

- Coin stock rows with a source-backed custom price, Darkan cache value, or direct content literal are live.
- Darkan cache prices mirror `Shop.java`: custom prices override buy price only; otherwise buy price uses ItemDefinitions.value plus coin/Tokkul enum overrides, while sell price uses ItemDefinitions.sellPrice plus sell enum overrides.
- Shops whose currencies do not exist in AnkiScape are visible but read-only; Coins and Tokkul are live inventory currencies.
- Reward/activity-dependent shop families are hidden from normal player search until their owning system exists.
- The developer test shop is excluded and still appears in the JSON ledger with an explicit disposition.

## Frontend Handoff Fixtures

Use `shop_fixtures.build_shop_frontend_fixtures()` for deterministic examples covering live purchases, locked stock rows, hidden reward shops, shared-stock keys, player-sold stock, services, vendor actions, search results, error previews, and transaction history.

## Manual Test Notes

Backend contract testing is pure-Python. Qt frontend passes should verify Shop-tab rendering and transactions through offscreen Qt tests plus a local visual smoke check.
