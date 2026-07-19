# UI asset normalization audit — 2026-07-19

## Scope

This pass audited every top-level PNG family that is reachable from an
AnkiScape UI, not only the new Herblore sprites. The repository contains 3,273
PNGs across 29 such directories.

The normalization rule is deliberately about source canvases, not displayed
widget dimensions:

- sprites at or below 256 pixels on each axis must be tightly cropped to their
  meaningful alpha bounds;
- pixels with alpha `<= 8` are treated as export noise;
- the original pixel art, aspect ratio, and relative internal scale are
  preserved;
- no transparent square is reintroduced after trimming; and
- larger banners, panels, bars, and other full-frame art remain untouched.

The 65 larger/full-frame assets are therefore intentional exceptions to the
small-sprite rule, not forgotten icons.

## Findings and repair

Before normalization, 1,747 small sprites carried avoidable transparent
padding. The padding made identical Qt icon boxes produce visibly inconsistent
art sizes and was especially obvious in Herblore, Combat, Bank, and Shop rows.

`tools/trim_icons.py` now covers the exact 29-family UI corpus. Running it
trimmed all 1,747 padded sprites; a second dry run reports zero remaining
changes. A separate base-blob comparison proves that all 1,745 modified tracked
PNGs are byte-for-byte pixel-identical to the expected alpha-bounds crop of
their prior version: the batch contains no resize, recolor, or replacement.
The other two normalized sprites are the newly added Herblore assets.

The fetching path had a second defect: `tools/fetch_assets.py` trimmed an image
and then centered it back onto a transparent `size × size` canvas. It now
normalizes alpha noise, crops first, and uses `size` only as a maximum
dimension. New downloads therefore cannot silently recreate the repository-wide
padding problem.

`tests/test_ui_asset_normalization.py` audits the complete family set and every
small PNG. It runs with either Pillow or Qt's `QImage`, so a missing Pillow
installation cannot turn the full-corpus invariant into a skip.

## Independent taste review

Both required visual reviewers returned `SHIP`:

- Fable found no family that should retain small-sprite padding and identified
  the fetcher's trim-then-repad defect, the missing mass rewrite, stale help
  text, and the need for a consistent weak-alpha threshold.
- Kimi K3 found no family exception and identified the test-oracle skip as a
  closure blocker. The audit now uses the repository's available image backend
  rather than skipping.

The first Kimi max call produced no usable output and was stopped after 30
minutes; the bounded Kimi high recheck completed. Workflow runs
`ce4f327f-5313-49c2-825c-d63b79959367` and
`7b705f05-2f24-4031-866a-4808e087a4ca` never established usable provider
sessions, so the primary reproduced the corpus findings directly and used the
quota-aware direct reviewer paths instead.

## Runtime verification boundary

Offscreen Qt is retained as a regression gate, not as proof of macOS Anki
rendering. A fully quit and freshly relaunched Anki process was inspected with
the real compositor after the mass rewrite. Representative Skills, Combat,
Shop, Bank, and Equipment surfaces all retained crisp, legible icons with
consistent visual occupancy and no cropping damage.

The new Herblore assets finish at their meaningful native bounds:

- `shrink_me_quick.png`: `20 × 29`;
- `shrunk_ogleroot.png`: `23 × 29`.

Final verification passes all 1,760 repository tests in the non-Qt runner
(1,536 ordinary passes and 224 environment skips) and all 1,760 tests in the
offscreen Qt runner (one expected optional-backend skip). The focused
all-corpus Qt audit, the 220-test main-menu suite, test-quality audit,
documentation audit, compile, JSON, diff, and worktree checks also pass.

No widget geometry or layout was changed in this pass. No owner-facing design
gap remains.
