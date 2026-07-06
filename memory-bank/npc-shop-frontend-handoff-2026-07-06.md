# NPC Shop Frontend Handoff

Date: 2026-07-06

Backend status: complete for the first source-backed NPC shop contract. The frontend should build the Shop surface from the backend modules below rather than inventing prices, stock behavior, or lock states.

## Backend Modules

- `shop_data.py`: generated runtime catalog from local Darkan shop JSON and 2011Scape item metadata. It includes shop visibility, row dispositions, currency state, source paths, services, vendor actions, aliases, and coverage summary.
- `shop_logic.py`: pure APIs for shop view models, search, buy/sell previews, buy/sell application, service/vendor actions, market-clock advancement, event history, and rollback.
- `shop_fixtures.py`: deterministic fixture bundle for frontend development and Qt tests.
- `storage_pure.py`: profile defaults/migration now seed `shop_data_version`, `shop_market_clock`, `shop_stock_state`, `shop_events`, and `shop_next_event_id`.
- `__init__.py`: answered review cards advance the market clock. Ten answered cards equals one market tick/hour, and Anki undo restores the changed shop clock/stock keys through the existing review snapshot stack.

## Fixture Keys

Use `shop_fixtures.build_shop_frontend_fixtures()` as the first UI contract. It returns:

- `normal_coin_stock_shop`
- `feather_multi_shop_search`
- `locked_read_only_shop`
- `locked_preview_error`
- `non_coin_locked_shop`
- `hidden_reward_shop`
- `shared_stock_shop`
- `player_sold_stock`
- `service_transaction`
- `vendor_action_transaction`
- `history`
- `search_after_transactions`

These fixtures deliberately cover visible, locked, hidden, shared-stock, temporary player-sold stock, direct vendor, processing service, error, search, and history states.

## UI Contract

- Render `shop_view_model_pure(player_data, shop_id)` rows as authoritative. Row `can_buy`, `can_sell_to_shop`, `visibility`, `lock_reason`, and `disposition` are backend-owned.
- Use preview APIs before committing a transaction:
  - `preview_shop_buy_pure`
  - `preview_shop_sell_pure`
  - `preview_shop_service_pure`
  - `preview_shop_vendor_action_pure`
- Use apply APIs only from explicit user commands:
  - `apply_shop_buy_pure`
  - `apply_shop_sell_pure`
  - `apply_shop_service_pure`
  - `apply_shop_vendor_action_pure`
- Do not show hidden shops in normal browsing. They exist for future reward/activity owners and explicit developer/debug views.
- Treat visible locked rows as inspectable but inert. Show the backend `lock_reason`; do not override it in frontend copy.
- General stores can show temporary player-sold stock. Specialist shops reject selling non-stock items.
- Non-coin shops are read-only until their currencies exist as implemented inventory systems.
- Services and vendor actions are not ordinary stock rows. Render them as command rows or a separate section.

## Frontend Test Targets

The first frontend slice should add Qt tests for:

- Shop tab/menu entry appears without replacing Bank/Stats/Skills.
- Search for `Feather` shows multiple locked source rows and does not allow purchase.
- A normal live shop row can preview and buy with enough Coins.
- Locked/non-coin/hidden cases render their backend lock states.
- A general-store sell creates visible temporary stock, then buying it back works.
- Tanning and direct vendor actions preview/apply correctly.
- History rows show recent transaction events and rollback events.

Manual QA after Qt wiring should use Pinchtab against Anki or the local UI surface because the backend currently has no browser-facing surface to drive.

## Frontend Implementation Result

Completed: 2026-07-06

- Added a top-level `Shop` tab in `ui.py` without replacing `Skills`, `Quests`, `Bank`, `Equipment`, `Stats`, `Achievements`, or `Settings`.
- The Shop tab renders search, shop selection, a selected-shop stock panel, Buy/Sell modes, RuneScape-style quantity controls, service/vendor action rows, shop-local history, and global recent activity.
- Qt rendering delegates prices, lock reasons, sell policy, stock mutation, service/vendor eligibility, search result visibility, and history rows to `shop_logic.py` APIs.
- Hidden reward/activity shops remain out of normal browse and item-first search through `include_hidden=False` and visible-shop filtering.
- Added targeted offscreen Qt coverage in `tests/test_main_menu_widget.py` for hidden-shop exclusion, Feather locked search, live stock buy, general-store sell/player-sold stock, service/vendor actions, and global history.

Verification:

- `python3 run_tests.py`: 743 tests passed, 140 skipped.
- `QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests`: 743 tests passed.

## Copy-Paste Frontend Prompt

```text
In the AnkiScape repo, implement the frontend for NPC Shops using the completed backend contract. Read memory-bank/npc-shop-design-grill-2026-06-24.md, memory-bank/source-audits/npc-shop-backend-audit-2026-07-06.md, and memory-bank/npc-shop-frontend-handoff-2026-07-06.md first. Do not invent shop prices, lock reasons, or stock behavior in Qt. Use shop_fixtures.build_shop_frontend_fixtures() and shop_logic.py view/preview/apply APIs as the contract. Add a Shop surface that can browse/search visible shops, inspect locked rows, buy live stock, sell to general stores, run service/vendor actions, show transaction history, and keep hidden reward shops out of normal browsing. Add targeted Qt tests and then run python3 run_tests.py plus QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests. Use Pinchtab for manual frontend QA after the UI is wired.
```
