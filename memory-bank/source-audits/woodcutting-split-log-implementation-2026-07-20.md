# Woodcutting Split Log Implementation — 2026-07-20

Cutoff: 2012-11-20, immediately before EOC.

Status: **implemented processing slice; Arctic-pine log acquisition remains
source-blocked.**

## Period evidence

- RuneScape Wiki `Split log`, oldid `5505475`, dated 2012-04-18, establishes
  the separate level-54 Woodcutting action: use one Arctic pine log on the
  Neitiznot stump, receive one tradeable Split log, and gain 42.5 Woodcutting
  XP.
- OpenRS2 cache rev 742 identifies unnoted Arctic pine logs as item `10810`
  and unnoted Split log as item `10812`; their noted forms are `10811` and
  `10813`.
- RuneScape Wiki `Exchange:Split log`, oldid `6563176`, timestamp
  `2012-11-16T05:34:45Z`, pins the cutoff guide price at 30 coins, the
  four-hour buy limit at 1,000, item ID `10812`, and cache value 90.
- RuneScape Wiki `File:Split log.png` has an upload revision timestamped
  `2011-11-29T01:43:04Z`. The checked-in sprite is fetched from that revision,
  alpha-trimmed, and recorded in `assets_provenance.json`.
- The owner-settled Woodcutting contract in
  `gap-grill-decisions-2026-07-10.md` and
  `source-audits/gap-grill-10-woodcutting-provenance-2026-07-10.md` requires
  the split target to unlock once The Fremennik Isles starts, not only after
  completion.

## Live behavior

- `Split Arctic pine logs` is a distinct level-54 Woodcutting processing
  target. Each successful review consumes one carried Arctic pine log,
  produces one carried Split log, and awards 42.5 Woodcutting XP.
- The action requires no hatchet, never rolls a bird nest, never invokes the
  Inferno adze, and does not count as a chopped log or charge a Woodcutting
  urn.
- The shared carried-inventory wrapper recognizes this target as processing:
  it packs real Arctic pine log inputs, consumes them from the carried view,
  reconciles the Bank atomically, and uses the normal review-driven bank-run
  model.
- The generic target-unlock engine now supports `quest_started`. Both this
  target and the existing Arctic-pine Firemaking row honor the newer
  quest-start contract while completed quests continue to satisfy the gate.
- The Skills row shows the exact material count, output, XP, quest-start lock,
  and period icon. Its prompt is now `Select what to Chop or Split`, avoiding
  the false claim that every Woodcutting row selects a tree.
- Split log is registered as a non-stackable, tradeable log item with cache ID
  `10812`, period GE price 30, and period buy limit 1,000.

## Explicit boundary

Arctic pine chopping is not implemented by this slice. Its level, 140.2 XP,
output, and access gate are known, but the exact success, depletion, and
respawn mechanics remain source-blocked. The reachability ledger therefore
truthfully reports Arctic pine logs as a root orphan and the split action as
blocked. No fallback odds or substitute acquisition route were invented.

The live cadence declaration remains `source_blocked` because no compatible
pre-cutoff XP/hour rate is pinned for the one-review split action. In the
cadence kernel this is an auditable passthrough, not a disabled target.

No owner design gap emerged.

## Verification

- The complete non-Qt universe passes all 1,936 tests with 252 intentional
  environment skips. The complete real offscreen-Qt universe also passes all
  1,936 tests with its one intentional skip.
- The focused source, registry, quest-gate, metadata, runtime, Grand Exchange,
  and Woodcutting suites pass 195 tests; the real offscreen-Qt row check and
  the two global asset-normalization checks also pass.
- Documentation (438 Markdown and 382 HTML files), test quality (zero hard
  issues), compilation, JSON parsing, diff whitespace, reachability, and
  worktree-safety audits pass. Reachability reports 1,413 actions, 2,081
  reachable items, 168 orphan inputs (76 root and 92 cascade), and 189
  unresolved actions.
- Kimi K3's taste pass approved the row hierarchy and period icon weight. Its
  three concrete polish findings are resolved: the prompt now follows sibling
  title casing, the tooltip renders the configured output quantity, and the
  material lock reads as a missing-item reason. A fresh screenshot from the
  final tree confirms the corrected copy and preserves separate Utilities and
  Activities categories.
- The required Fable taste pass remains externally blocked because its live
  quota probe cannot read Claude Code OAuth from macOS Keychain (`security`
  exit 51). This is an external review blocker, not a product or design gap.

Results artifact:
`memory-bank/status-updates/woodcutting-split-log-results-2026-07-20.html`;
mobile copy: `https://g5v7ucswdk1k.postplan.dev`.
