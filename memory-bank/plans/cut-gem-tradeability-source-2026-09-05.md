# Cut-gem tradeability source plan

Date: 2026-09-05. Branch: `goal/cut-gem-tradeability-source-2026-09-05`.
Baseline: `1932b3c07b5dd8bdb598889f2f503607ac92b791`.

## Scope and acceptance

Resolve only the ordinary cut Jade item 1611 and cut Red topaz item 1613.
Bind each historical identity to the current `Jade` or `Red topaz` storage key.
Establish player tradeability from a literal non-beta item record before
`2012-11-20T00:00:00Z`. Keep GE eligibility, guide prices, and buying limits as
separate claims. Do not infer direct tradeability from a cache GE flag or a
name set. Missing proof stays source-blocked.

## Source sequence

1. Read the retained cohort, source contracts, generated mappings, and cached
   period records. Record exact source paths and content hashes.
2. Reconcile dated item identities and retained reconstruction evidence.
   Darkan remains read-only; the driver owns cross-project coordination.
3. Retrieve only missing item and Exchange historical records through the
   MediaWiki API with curl and bounded retries. Keep exact response bytes,
   oldids, timestamps, literal fields, and any beta or identity conflicts.
4. Compare each retained global buy-limit row with any recovered per-item
   Exchange limit. Qualify guide prices by their historical snapshot date.
5. Freeze a source audit, bounded raw evidence, and provenance manifest for
   independent review. State the smallest supported future implementation.

This pass changes no product code, generated data, tests, pins, UI, or source
checkout. It runs no product tests and does not use the MacBook mirror or Anki.
It creates no HTML artifact and makes no commit before independent review.
