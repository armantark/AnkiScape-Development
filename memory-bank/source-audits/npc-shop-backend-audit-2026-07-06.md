# NPC Shop Backend Source Audit

Generated: 2026-07-06

## Sources

- Darkan shop JSON: `/Users/ArmanTarkhanian1/Documents/2012scape with bots/darkan-world-server/data/items/shops`
- 2011Scape item names/tradeability: `/Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml`
- 2011Scape shop model and Darkan shop model were used as behavior references for stock, restock, general-store sell policy, and player-sold temporary stock.

## Coverage

- Source shop files: 274
- Runtime shops: 273
- Visible shops: 267
- Locked/read-only shops: 5
- Hidden shops: 1
- Stock rows: 2776
- Live stock rows: 13
- Locked stock rows: 2742
- Hidden stock rows: 0
- Blocked stock rows: 21
- Services: 4
- Vendor actions: 4

## Disposition Policy

- Coin stock rows with a source-backed custom price or direct content literal are live.
- Coin stock rows without a resolved Darkan cache item value are visible but locked, so gameplay fails closed rather than inventing prices.
- Non-coin shops are visible but read-only until their currencies exist in AnkiScape.
- Reward/activity-dependent shop families are hidden from normal player search until their owning system exists.
- The developer test shop is excluded and still appears in the JSON ledger with an explicit disposition.

## Frontend Handoff Fixtures

Use `shop_fixtures.build_shop_frontend_fixtures()` for deterministic examples covering live purchases, locked stock rows, hidden reward shops, shared-stock keys, player-sold stock, services, vendor actions, search results, error previews, and transaction history.

## Manual Test Notes

Backend manual testing is pure-Python for this turn. The future UI thread should verify Shop-tab rendering and transactions through Pinchtab after wiring the frontend surface.

## Verification

- `python3 -m py_compile shop_data.py shop_logic.py shop_fixtures.py storage_pure.py constants.py tools/generate_npc_shop_data.py`
- `python3 -m unittest tests.test_shop_data tests.test_shop_logic tests.test_storage_pure tests.test_storage_migration_extra`
- `python3 run_tests.py`: 738 tests passed, 135 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`: 738 tests passed.
