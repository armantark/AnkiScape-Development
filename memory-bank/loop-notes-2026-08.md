# AnkiScape grind-loop notes — 2026-08

## Iteration 1 — pass 6 B.15 skill-selector hybridization

- Result: complete and cross-lineage verified.
- Scope: per-skill target selectors only. Combat retains its tree-specific live
  filter and empty-state machinery; D.1 behavior remains outside this slice.
- Behavior: `<25` rows render flat; `>=25` grouped rows render as a tree; an
  ungrouped row set remains flat. Both forms use alternating rows, exact
  30-pixel item height, green current-target highlighting, and bold current
  text.
- Regression coverage: real Qt builders at the 24/25 boundary, the 25-row
  ungrouped fallback, renderer type, striping flag, row geometry, highlight,
  font weight, and the affected short Agility and Thieving surfaces.
- Verification: full plain discovery passed 3,785 tests with 459 declared
  skips in 238.080 seconds. Full offscreen-Qt discovery passed the same 3,785
  tests with 3 declared skips in 520.229 seconds from the real `.venv-qt`
  interpreter. The test count increased by two from the 3,783-test baseline.
- Independent review: Kimi K3 found no material defect. The implementation
  incorporated its concrete notes to correct four stale return annotations and
  pin the 30-pixel geometry instead of asserting only relative equality.
- Workflow note: read-only Codex Workflows run
  `3a1ea34f-0acd-467a-9cc0-bde476372763` exhausted its tool-byte budget while
  loading project memory and produced no actionable result; root independently
  reproduced the complete scope.
