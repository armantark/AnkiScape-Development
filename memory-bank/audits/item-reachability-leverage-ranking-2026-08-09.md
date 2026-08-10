# Item reachability leverage ranking — 2026-08-09

## Purpose

`tools/audit_item_reachability.py --rank-roots N` ranks genuine root-orphan
acquisitions by the transitive product graph they would recover. It replaces
intuition-driven BFS selection with a deterministic report from the same graph
that owns the orphan ledger.

## Semantics

For each root orphan, the audit adds one synthetic source for that item, closes
the complete action graph, and compares the result with the unchanged baseline.
Each row reports:

- newly reachable items, including the candidate root itself;
- newly runnable actions;
- the exact newly reachable item list in JSON output.

The simulation does not claim that an acquisition route exists or that a value
is period-correct. It only measures the leverage of source-harvesting and
implementing that one root. Multi-input actions can correctly remain blocked,
so a candidate may add one reachable item and zero runnable actions.

The default audit output remains unchanged. `--json` adds the stable
`root_orphan_leverage` field, while `--rank-roots N` prints only the bounded
human-readable ranking after the normal summary.

## First live ranking

After the Blue-dragon-scale closure, the top candidates are:

1. Potato cactus: +20 items, +19 actions.
2. Wyvern bones: +12 items, +16 actions.
3. Uncut onyx: +11 items, +11 actions.
4. Fellstalk seed: +8 items, +5 actions.

This is prioritization evidence, not source evidence. The next slice must still
follow the pre-EOC source hierarchy and may reject or defer a candidate if its
authentic acquisition route is blocked.

## Verification

- Two focused reachability tests pass, including deterministic ordering,
  complete root coverage, and transitive count/list agreement.
- Full plain discovery passes 4,007 tests in 406.573 seconds with 488 expected
  skips.
- Full real offscreen Qt discovery passes 4,007 tests in 792.761 seconds with
  three intentional skips.
- No runtime, save, UI, or content data changed in this tooling slice.
