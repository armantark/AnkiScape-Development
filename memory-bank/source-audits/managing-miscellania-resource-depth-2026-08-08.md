# Managing Miscellania resource-family depth

Date: `2026-08-08`

Status: **source harvest complete; implemented on the existing collection kernel.**

Authority:

- RuneScape Wiki `Managing Miscellania`, oldid `6500793`,
  `2012-10-30T06:29:55Z`;
- `memory-bank/source-audits/managing-miscellania-loop-2026-07-18.md`; and
- `memory-bank/source-audits/managing-miscellania-horizontal-implementation-2026-07-21.md`.

Immutable source:
<https://runescape.wiki/w/Managing_Miscellania?oldid=6500793>.

This record supersedes only the older three-family catalog boundary. It does
not change the settled coffer, approval, worker-allocation, collection-time,
review-clock, persistence, or undo model.

## Exact cutoff catalog

The source table has six productive resource families and one idle row:

- Mining: `546 Coal` and `3 gems`;
- Wood: `892 Maple logs`, with
  `floor(accumulated Maple logs / 100)` bird nests;
- Flax/Herbs: either `1,250 Flax` and `2 herb seeds`, or exactly `61` grimy
  herbs inside the listed nine item ranges plus one seed from Guam through
  Torstol;
- Fishing: `440 Tuna`, `131 Swordfish`, `4 Caskets`, `4 gems`, and assorted
  extras, with a player choice between raw and cooked fish at the same count;
- Hardwood: `301 Teak logs`, `204 Mahogany logs`, or `121` of each;
- Farming: the complete allotment, hops, flower, herb, bush, and special seed
  ranges, plus one Willow/Maple/Yew/Magic seed and one Apple/Orange tree seed;
  and
- Idle: nothing.

The complete Farming category totals are `248–250` allotment, `104–106` hops,
`58–62` flower, `19–24` herb, `38–40` bush, `3–4` special, one tree, and one
fruit-tree seed. Tests pin both every item range and every category total.

## Recovered and unresolved boundaries

The exact family names, player-selectable variants, fixed quantities, item
ranges, category totals, and Maple-nest equation are live. The source does not
expose several server selectors:

- generic gem identities and weights;
- bird-nest identities and weights;
- the herb-seed identities for Flax and Herbs;
- the exact 61-herb composition distribution;
- the within-range Farming composition and tree-seed choices; and
- Fishing's assorted-extra quantities and selector.

The first five boundaries use visible registered placeholders under
`managing_miscellania.*`. Each deterministic composition stays inside every
source range and exact total. Fishing's assorted extras remain omitted because
the page gives examples but no count. Zero or an invented count would be a false
period claim, and the core Fishing row is complete without it.

## Integration result

The existing family-driven sanitizer adds the three missing allocation keys to
old saves at zero workers and selects the first valid variant. No schema bump is
needed. The same atomic collection command converts production credit, banks
the payout, clears only the claimed credit, and returns the exact output map.

The activity panel separates kingdom status from allocation through `Kingdom`
and `Resources` tabs. The six worker rows use two compact pages of three inside
`Resources`. Single-choice output fields remain visible but disabled so both
pages keep stable columns. The pager wraps, reports hidden-page assignments,
and retains accessible names, descriptions, tooltips, pips, spin boxes, variant
selectors, and Max controls. Long Farming payouts show five lines plus the
remaining count; the full preview remains in the tooltip and accessibility
description.

Kimi K3 and Opus 5 independently found no blocker. Their reproduced findings
closed pager discoverability, focus stability, column alignment, hidden-page
state, player-facing copy, tooltip duplication, and accessibility feedback.
The Codex Workflows simplification leaf failed before a model turn when its
single diff read exceeded the declared byte guard; root performed the required
diff-only deletion pass and removed redundant widget-state writes and dynamic
pager-tooltip construction.

Focused plain verification passes 338 tests; focused real offscreen-Qt UI and
asset verification passes 4 tests. Full plain and full real offscreen-Qt
discovery each pass 3,876 tests, with 479 and 3 intentional skips respectively.
Documentation audits 521 Markdown and 431 HTML files; test quality reports zero
hard issues across 3,842 tests in 176 files. Compilation, JSON, diff,
asset-normalization, and worktree audits pass. Reachability records 1,499
actions, 2,234 reachable items, 168 orphan inputs, and 188 blocked actions.

## Remaining data depth

- Fishing assorted-extra quantities and the complete selector;
- authentic gem, nest, herb-seed, herb-mix, and Farming-mix selectors;
- additional approval chores and recognition rolls;
- the source storage ceiling, Fremennik-task modifiers, and flatpack coffer
  values; and
- independent period-lineage corroboration beyond the immutable cutoff page.

None of these rows changes the shipped six-family mechanic or requires owner
design input.
