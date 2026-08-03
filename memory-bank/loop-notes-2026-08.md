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

## Iteration 2 — Dungeoneering guardian-room coin funding

- Result: already implemented on `main`; stale queue and Memory Bank status
  reconciled without duplicating product code.
- Existing implementation: commits `6ced27e8`, `dcf41c0d`, `c5eb86c8`,
  `6e07d1bc`, and `05016790` remove the resource-room cache and split the
  registered 1,010-coin placeholder across eligible critical-path guardian
  rooms. C1-C4, incomplete Druidic Ritual, Herblore below 5, and optional
  guardians receive no funding.
- Persistence: the eligible guardian-room ids survive reload; the migration
  distinguishes a legacy resource-cache save from pre-drop and post-drop saves
  so it neither loses funding nor grants it twice.
- Verification: the same product revision passed both full 3,785-test lanes in
  iteration 1. A fresh focused plain lane and fresh focused offscreen-Qt lane
  each passed all 54 Dungeoneering data, logic, and placeholder-register tests.
- Source status: the authentic guardian-room mechanism is settled; only the
  period coin magnitude remains the registered
  `PLACEHOLDER(dungeoneering.starter_guardian_coin_drops)` pending a decoded
  Frozen guardian drop table.

## Iteration 3 — 384-task Achievement Diary roster

- Result: complete. All eight regional families now expose four tiers of
  exactly twelve tasks, for 384 regional rows. The complete catalog has 474
  rows across ten families.
- Curation: every prior task identity remains stable. A short source tier first
  draws from unused authentic rows in its own family, preserving each row's
  original tier in both its durable ID and source note. The remaining 22 slots
  use visibly labelled progression anchors whose exact skill levels already
  occur in that family's period requirements; no tier uses more than three.
- Reachability: 317 regional rows have live predicates. The other 67 authentic
  rows remain visibly unavailable instead of becoming fabricated deeds. Three
  Miscellaneous activity deeds that already have live counters now resolve
  through those counters rather than remaining latent.
- Integrity: generation rejects an unknown quest, unknown skill, anchor level
  absent from the family source, duplicate authentic requirement, misplaced
  preferred source ID, tier above three anchors, or tier other than twelve
  rows. All 422 pre-change task IDs remain present and 52 rows were added.
- Verification: 128 focused pure/integration tests and 27 focused real
  offscreen-Qt tests pass. Deterministic regeneration is byte-identical. Full
  discovery passes 3,790 tests in both lanes: plain declares 460 expected
  skips; the real Qt interpreter declares 3.
- Depth debt: the v108 diary revalidation migration still needs a targeted
  regression test, and the generator's local `ITEMS_YML` source path remains
  non-portable. Neither changes the live 384-row mechanic.

## Iteration 4 — period-cache enum, struct, and param reader

- Result: implemented the first high-leverage depth tool. One read-only wrapper
  accepts an extracted cache or disk zip and exposes `count`, `dump`, and
  case-insensitive `find` for enum, struct, and param definitions.
- Evidence boundary: enum and struct decoding reuse Darkan core 2.0.5; param
  decoding follows the rev-727 client's opcodes 1, 2, 4, and 5 and rejects an
  unknown opcode. Output is deterministic and key-sorted. This is client data,
  never evidence for server-side rolls, rates, timers, or rewards by itself.
- Period coverage: count probes pass on all seven local caches. From build 652
  through 742, enum definitions grow 3,853→6,680, structs 1,793→14,527, and
  params 1,414→2,792. Exact rev-727 fixtures pin enum 3483 (1,096 entries),
  struct 0, and param 0.
- Delegation: GPT-family Workflows run
  `3c1610ec-a7ec-4dfc-93dd-a72bb33abd6e` exhausted both leaves' processed-token
  guards before a final response. Root reused the bounded tool evidence and did
  not rerun the leaves.
- Verification: the three real-cache integration tests pass. Full discovery
  passes 3,793 tests in both lanes: plain declares 460 expected skips; the real
  Qt interpreter declares 3. Shell syntax, Python compilation, documentation,
  and test-quality audits also pass.

## Iteration 5 — period-cache interface-definition reader

- Result: implemented the second high-leverage depth tool. One read-only
  wrapper accepts an extracted cache or disk zip and exposes deterministic
  `count`, `dump`, and client-label `find` modes for index-3 interfaces.
- Decoder: the tool reuses Darkan core 2.0.5 rather than copying the giant
  decompiled client component class. It reports stable `interface:component`
  identities, layout and hidden state, text/assets, actions, and principal
  client script hooks.
- Period coverage: count probes and interface 0 component 0 decode on every
  local cache from build 652 through 742. Rev 727 contains 1,321 interfaces and
  65,239 components; exact fixtures pin the Grand Exchange heading and travel
  action.
- Evidence boundary: interface definitions establish shipped presentation and
  client hooks only. They do not establish server validation, XP, rolls,
  timers, drops, or rewards.
- Delegation: GPT-family Workflows run
  `a5aff6a3-4f4a-4821-ba59-69edabad8e3a` exhausted its tool-output budget after
  dumping the decompiled client. Root recovered its bounded decoder evidence,
  found the existing core loader, and did not rerun the leaf.
- Verification: three real-cache integration tests pass. Full discovery passes
  3,796 tests in both lanes: plain declares 460 expected skips; the real Qt
  interpreter declares 3. Shell syntax, Python compilation, documentation,
  test-quality, diff, and worktree audits pass.
