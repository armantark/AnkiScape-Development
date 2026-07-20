# Item reachability: Cooking byproduct correction — 2026-07-20

## Finding

The live reachability graph falsely classified `Fish offcuts` as a root orphan.
All three shipped gut-leaping-fish actions already produce the item at their
source-backed probabilities:

- `gut_leaping_trout`: `1/2`;
- `gut_leaping_salmon`: `3/4`;
- `gut_leaping_sturgeon`: `5/6`.

The runtime and pure Cooking tests already exercise those outputs. The defect
was confined to `tools/audit_item_reachability.py`: `_outputs()` recognized the
plural `byproducts` mapping used by other action families but not Cooking's
singular `byproduct_item` field.

## Correction

The graph now includes `byproduct_item` alongside the existing output shapes.
No recipe, acquisition action, probability, item definition, UI, or save state
changed. `Fish offcuts` resolves through
`Cooking:gut_leaping_trout`, the first reachable producer in deterministic
action order.

The live graph moves from 1,997 to 1,998 reachable items and from 239 to 238
orphan inputs (96/143 to 95/143 root/cascade). The action and unresolved-action
counts remain 1,343 and 250.

## Verification

- The new route assertion fails before the correction with
  `KeyError: 'Fish offcuts'`.
- `tests.test_item_reachability_audit`, `tests.test_logic`,
  `tests.test_runtime_actions`, and `tests.test_fishing_data` pass all 284
  focused tests afterward.
- Complete non-Qt discovery passes all 1,905 tests with 250 expected
  environment skips. The documentation audit passes 432 Markdown and 379 HTML
  files, the test-quality audit reports zero hard issues across 83 files, and
  diff-whitespace and guarded-worktree checks pass.
- No new UI or owner design gap is involved.
