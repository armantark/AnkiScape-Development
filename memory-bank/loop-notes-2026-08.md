# AnkiScape grind-loop notes — 2026-08

## Iteration 20 — Crucible target-level matching

- Evidence: Crucible oldid `6538845`; its complete pre-cutoff article and talk
  histories; rev-727 interfaces and scripts; and Darkan's complete Crucible
  history from `53122a021` onward.
- Result: the exact server matching band and its frequencies remain
  source-blocked. The old registered `-8/0/+8/+20` cycle could not reproduce
  the period criticism it cited: a minimum-eligible combat-60 entrant could
  reach only level 80, never a maxed level-138 opponent. The fourth offset is
  now `+78`, clamped to the real 3–138 combat range. The first three targets
  remain near-level, while the documented severe mismatch is reachable. Its
  one-in-four cycle position is explicitly a reachability abstraction, not a
  period frequency. No design gap surfaced.
- Verification: 39 focused Crucible/register tests pass. Full discovery runs
  3,858 tests in both lanes: plain has 3,379 ordinary passes and 479 expected
  skips; offscreen Qt has 3,855 ordinary passes and 3 expected skips. Test
  quality audits 3,824 methods across 176 files with 0 hard issues. A bounded
  GPT-family no-tools checker (`8b16c106-cd75-4e23-a51b-37e0d1792af3`)
  independently agreed that no numeric period band survives; root reproduced
  the reachable-boundary defect. Documentation, diff-hygiene, and worktree
  audits pass. This merge is GPT-family verified.
- Next: Crucible event interval.

## Iteration 19 — Crucible bounty-fee scale

- Evidence: Crucible oldid `6538845`; complete cutoff talk history through
  oldid `5909709`; launch-day report oldid `5778707`; the immutable
  `Crucible_bounty_fee_interface.png` revision uploaded
  `2012-06-24T20:37:44Z`; rev-727 interface 1298; Darkan history commit
  `684c25528`.
- Result: the old curve was an order of magnitude below every surviving period
  observation. The registered reachability curve now anchors level 60 at
  500,000 coins and level 138 at 531,200 coins: a 450,000 risk baseline,
  400 per combat level above 60, and a 50,000 abandonment component. This is
  explicitly not claimed as the unrecovered server formula. No design gap
  surfaced.
- Verification: 38 focused tests pass. Full discovery passes 3,804 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. Documentation
  audits 515 Markdown and 428 HTML files; test quality audits 3,770 tests with
  0 hard issues. Diff-hygiene and worktree audits pass.
- Next: Crucible target-level offsets.

## Iteration 18 — Crucible Trophy-bone awards

- Evidence: launch-update oldid `5778674`; the complete Crucible history through
  cutoff oldid `6538845`; Trophy bones oldid `5971782` and its complete
  29-revision pre-cutoff history; rev-727/741/742 item 24444; rev-727 scripts
  and interface 1297:125; Darkan history commit `684c25528`.
- Result: ordinary kills demonstrably award Trophy bones, but no source exposes
  the amount, so the two-bone reachability value remains registered. The four
  tutorial awards are exactly one each, so that stale placeholder is retired.
  Darkan's non-stackable metadata container is recorded as a later loot-key
  reconstruction, not period amount evidence. No design gap surfaced.
- Verification: 37 focused tests pass. Full discovery passes 3,803 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
  test-quality, diff-hygiene, and worktree audits pass.
- Next: Crucible risk-expectation amount per combat level.

## Iteration 17 — Crucible ordinary-kill rank points

- Evidence: launch-update oldid `5778674`, the complete pre-cutoff Crucible
  article history through oldid `6538845`, the cutoff talk history, Darkan
  `CrucibleController.java` and history commit `684c25528`, and rev-727 script
  6288.
- Result: ordinary target kills demonstrably award rank points, but no source
  exposes the amount. The one-point value remains a registered reachability
  placeholder and is not inferred from the separate champion-hit rule. No
  gameplay changed and no design gap surfaced.
- Verification: 37 focused tests pass. Full discovery passes 3,803 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
  test-quality, diff-hygiene, and worktree audits pass.
- Next: Crucible Trophy bones per ordinary kill.

## Iteration 16 — Crucible rank-point thresholds

- Evidence: Darkan `CrucibleController.java:28-33`,
  `Crucible.java:86-122`, history commit `684c25528`, rev-727 scripts 6284/6288,
  Crucible oldid `6538845`, and launch-update oldid `5778674`.
- Result: no source exposes the six promotion boundaries. The registered
  1/3/6/10/15/25 ladder remains, with the complete negative caller chain now
  recorded. No gameplay changed and no design gap surfaced.
- Verification: 37 focused tests pass. Full discovery passes 3,803 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
  test-quality, diff-hygiene, and worktree audits pass.
- Next: ordinary Crucible rank points per kill.

## Iteration 15 — Daily Challenge assignment weighting

- Evidence: Challenge System oldid `6579729` states one-in-four for the desired
  skill when four skills remain. Cutoff talk oldids `6555739` and `6539307`,
  Darkan, and rev-741/742 expose no within-skill selector.
- Result: replace the biased flat row draw with equal skill intervals followed
  by a within-skill draw, while consuming one RNG value. Rename the placeholder
  so only the genuinely unknown within-skill task weights remain registered.
- Regression: every eligible skill owns one equal interval even though Mining
  and Cooking have more breadth rows. No design gap surfaced.
- Verification: 47 focused unit/integration tests pass. Full discovery passes
  3,803 tests in both lanes, with 460 expected plain skips and 3 Qt skips.
  Documentation, test-quality, diff-hygiene, and worktree audits pass.
- Next: Crucible rank-point thresholds.

## Iteration 14 — Tears of Guthix green-tear probability

- Evidence: Darkan `TearsOfGuthix.kt:477-510` and its frozen target contract;
  activity oldid `6579712`; cutoff talk oldid `6539293`; rev-727/742 cache
  evidence already recorded in the source audit.
- Result: no source exposes stream rotation or catch probability. The registered
  `0.055` value remains, now explicitly described as a weak reachability anchor
  rather than an authentic rate. No gameplay changed and no design gap surfaced.
- Verification: 26 focused tests pass. Full discovery passes 3,802 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
  test-quality, diff-hygiene, and worktree audits pass.
- Next: Daily Challenges eligible-pool assignment weights.

## Iteration 13 — Bork Ork-legion style classification

- Evidence: Darkan `Bork.kt:110-111,184-205` selects melee within one tile and
  ranged otherwise.
- Result: the settled stand-near pressure route continues to use the exact
  adjacent melee branch. `bork.ork_legion_attack_style` is retired because this
  is a disclosed distance-collapse abstraction, not an unknown period value.
- Verification: 28 focused tests pass. Full discovery passes 3,802 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. GPT-family verified.

## Iteration 12 — Duellist's cap threshold closure

- Evidence: oldid `6579418`, dated `2012-11-18T23:11:12Z`, is the pre-cutoff
  parent of the previously cited post-cutoff cap page and already states all six
  ranges.
- Result: live minimums remain `0/10/100/500/2,000/5,000`, now period-pinned;
  `duel_arena_cap_thresholds` is retired from the placeholder register.
- Verification: 16 focused tests pass. Full discovery passes 3,802 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. GPT-family verified.

## Iteration 11 — Skeletal Horror phase identities

- Evidence: rev 727, rev 742, Darkan's generated NPC list, and its four
  `nostats` combat definitions agree on the form mapping 320=`9176/9177`,
  260=`9178`, 180=`9179`, and 100=`9180`.
- Result: the live weakening sequence is corrected from the shifted
  `9176 → 9177 → 9178 → 9179` to `9176 → 9178 → 9179 → 9180`.
- Honest limit: all four core-stat blocks remain registered placeholders. The
  client exposes combat level, and the authentic server definitions explicitly
  omit stats; no value was derived from combat level.
- Delegation: GPT-family Workflows run
  `5a1447db-96b4-47f7-9b47-b52860ce2f07` exhausted its tool-output budget after
  two calls and produced no synthesis. Root independently reproduced every
  accepted finding and did not rerun it.
- Verification: 20 focused tests pass. Full discovery passes 3,802 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. GPT-family verified.

## Iteration 10 — Daily Challenges reward-XP re-walk

- Rev 741 and 742 contain identical client structs for representative combat,
  Cooking, and Fishing challenges. The rows carry the full client-facing task
  definition but no XP payout field.
- Rev 742 interface 1343 is the Daily Challenges panel. Its decoded labels and
  hooks reveal no static reward amount; the two reward item definitions prove
  only the lamp and bag identities and actions.
- The interface search no longer dies on the first legacy IF1 archive. It
  reports all fifteen unsupported rev-742 interface IDs on standard error and
  continues searching the decoded remainder, making negative evidence honest.
- Result: `daily_challenges.reward_xp` remains registered at 100 XP per required
  level. A period server payout routine or independently stated amount is still
  required to replace it. No gameplay value changed.
- Verification: 51 focused Daily Challenges, real-cache reader, and placeholder
  tests pass. Full discovery passes 3,802 tests in both lanes, with 460 expected
  plain skips and 3 Qt skips. Documentation, test-quality, diff, and worktree
  audits pass.

## Iteration 9 — Frozen boss combat-level closure

- Tooling: the exact NPC definition reader now emits combat levels for requested
  IDs.
- Evidence: rev 727 and rev 742 agree on all 144 definitions in the six Frozen
  boss series. Astea's 57 rows encode three NPC forms for each of 19 levels; the
  other series encode one row per level.
- Result: every live ladder was already numerically correct. The registered
  ladder placeholder is retired; server tier selection and combat definitions
  remain honest placeholders.
- Coordination: the canonical Darkan/AnkiScape source ledger records the pinned
  cache result so the Darkan restoration loop need not repeat it.
- Verification: 13 focused cache/data/register tests plus documentation,
  test-quality, shell-syntax, diff, and worktree audits pass. Full discovery
  passes 3,801 tests in both lanes, with 460 expected plain skips and 3 Qt
  skips. GPT-family verified.

## Iteration 8 — Achievement Diary depth closure

- Generator: the Diary catalog generator now requires an explicit
  `--items-yml` source path. The hard-coded developer checkout is gone, and a
  real rev-667 regeneration remains byte-identical.
- Migration: the v108 regression already covered removal and re-earning. It now
  proves an unrelated unmet completion survives, closing the selective
  revalidation boundary without adding a duplicate test.
- Delegation: GPT-family Workflows run
  `c48d7907-2f2e-4e3c-a365-7ba95b3aec2a` stopped both read-only leaves when they
  exceeded their tool-output budgets. Root independently reproduced the two
  findings and did not rerun the leaves.
- Verification: the focused Diary/storage lane passes 168 tests; explicit-path
  regeneration is byte-identical. Full discovery passes 3,800 tests in both
  lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
  test-quality, diff, and worktree audits also pass. GPT-family verified.

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

## Iteration 6 — client-side blocked-row re-walk

- Result: the Conquest Foot Soldier cost placeholder is retired. Interface
  1015 renders squad costs from NPC param 1138, CS2 script 486 maps the Foot
  Soldier to NPCs 12202/12205, and both rev-727 rows contain 50. The live value
  was already conservative, so this is an evidence correction rather than a
  gameplay change.
- Tooling: the NPC/object definition reader now supports deterministic
  `--params` output for exact IDs. A real-cache integration test pins both Foot
  Soldier variants and the period cost.
- Honest limits: no diary-lamp minimum-level table, Conquest battlefield grid,
  or starting/passive command-point rule appeared in the decoded interface,
  CS2, or definition data. Those server-owned values remain registered
  placeholders rather than inferred conventions.
- Delegation: GPT-family Workflows run
  `f6e5b815-9ee4-43ca-8d9c-f20032ac1d79` exhausted both leaves' processed-token
  guards. Root salvaged their bounded client leads, independently reproduced
  every accepted claim, and did not rerun the leaves.
- Verification: 34 focused tests pass. Full discovery passes 3,797 tests in
  both lanes: plain declares 460 expected skips; the real Qt interpreter
  declares 3. Documentation, test-quality, shell-syntax, diff, and worktree
  audits pass.

## Iteration 7 — exact item-definition depth

- Tooling: `query_openrs2_cache.sh --id` now emits deterministic exact model,
  recolour, texture, sprite-recolour, bonus, stackability, exchangeability, and
  option fields for requested item IDs.
- Temple Trekking: rev-727 model `14131` leaves item `7774` in its original
  yellow/ochre colours, recolours `7775` into the red hue band, and recolours
  `7776` into the blue band. The live blue/yellow mapping was reversed and is
  corrected to blue `7776`, yellow `7774`, red `7775`.
- Goblin Raids: rev-741 pins Goblin cower shield and Raider axe/chainbody/shield
  as `25350-25353`. All four are non-exchangeable and carry nonzero combat
  bonuses. The unrelated `202xx` identities, tradeable Raider rows, and zeroed
  bonuses are corrected.
- Placeholder result: `temple_trekking.token_color_item_ids` and
  `goblin_raids.raider_set_bonuses` are retired. Dominion Tower reward IDs stay
  source-blocked because exact-name cache searches found no identities to query.
- Delegation: GPT-family Workflows run
  `20dc70c5-2a6c-490f-8d35-25550d5659af` exhausted both bounded leaves before a
  final response. Root reused only their narrow file leads, independently
  reproduced every cache claim, and did not rerun them.
- Verification: 152 focused cache/data/registry/equipment tests and two real
  offscreen equipment-stat UI tests pass. Full discovery passes 3,799 tests in
  both lanes, with 460 expected plain skips and 3 Qt skips. Documentation,
  test-quality, shell-syntax, diff, and worktree audits also pass.
