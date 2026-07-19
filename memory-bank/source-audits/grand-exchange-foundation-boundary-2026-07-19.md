# Grand Exchange backend foundation boundary

Date: 2026-07-19

Status: **source-ready foundation implemented; period prices, buy limits,
matching, review ticks, and Qt remain open.**

## Authority

- `fake-grand-exchange-design.md:16-38` settles the local-only, optional,
  eight-slot product surface, confirmation thresholds, and Ironman lockout.
- `fake-grand-exchange-design.md:40-57` settles escrow, partial collection,
  cancellation, integer prices, and the no-tax boundary.
- `fake-grand-exchange-design.md:189-253` settles persisted order fields,
  deterministic review undo, backend-first sequencing, and required test seams.
- `fake-grand-exchange-design.md:272-280` narrows the live catalog from merely
  tradeable items to the cache's `exchangeable` subset.
- `ge-relitigation-2026-07-19.md:102-132` permits the cache `value` field as the
  period-authentic fallback anchor while Wayback prices are absent.
- `ge-relitigation-2026-07-19.md:134-149` still requires period-first price,
  buy-limit, and interface harvests before those rows are claimed complete.

## Source harvest

`tools/DumpDarkanItemValues.java` now extracts `ItemDefinitions.canExchange()`
from the same on-disk Darkan cache already used for values and stackability.
The cache has an intentionally empty Huffman index, so the extractor opens only
item index 19 instead of constructing an unrelated full Huffman service. The
generated table contains:

- 10,745 positive cache-value names;
- 1,119 stackable names;
- 3,271 directly exchangeable cache names; and
- 1,656 registered AnkiScape rows after intersecting exchangeability,
  tradability, non-Coin identity, and a positive cache/period price.

The plural-name bridge already required by AnkiScape storage also applies to
exchangeability, so registered forms such as plural arrows resolve to their
cache-singular identity without hand curation.

## Implemented boundary

- `grand_exchange_data.py` builds only registered, cache-exchangeable rows.
  Period price and buy-limit maps override the cache fallback without widening
  eligibility.
- `grand_exchange_logic.py` supplies eight persistent offer slots, stable order
  IDs, buy/sell escrow, configurable high/extreme-price confirmation, partial
  collection, cancellation refunds, collect-all, and the Ironman access toggle.
- Buy offers fail closed while their period buy limit is absent. The current
  generated catalog therefore makes no unsourced buy-limit claim.
- Save version 44 defaults and sanitizes the market seed/cursor, order list,
  buy-limit usage, trade history, settings, and Ironman state.

## Explicit omissions

This slice does **not** claim a live player-facing market. The following remain:

1. dated Wayback November-2012 price rows;
2. period buy-limit rows;
3. the pre-cutoff interface/trend harvest;
4. stochastic fills, price improvement, bounded player impact, guide updates,
   naturalized market texture, and review-undo integration;
5. offer editing and queue-age reset;
6. Bankstanding; and
7. the top-level eight-slot Qt surface plus manual Anki verification.

No owner-facing design gap emerged. These omissions are source or downstream
implementation work under already-settled contracts.

## Verification

- 50 focused GE, item-value, generator, alias, and storage tests pass.
- 226 adjacent storage-migration, registry, shop, inventory, and integration
  tests pass.
- The test-quality audit reports zero hard issues.
- Results:
  `status-updates/grand-exchange-foundation-results-2026-07-19.html`; mobile
  copy: `https://svzfn2ylt4dw.postplan.dev`.
- Read-only Workflow `1783f883-12d2-412a-be45-72d63c0fb64c` produced no review
  or repository writes. It was cancelled after the Codex provider failed before
  session creation with `failed to install system skills ... Directory not
  empty (os error 66)`; the primary independently reproduced every accepted
  finding.
