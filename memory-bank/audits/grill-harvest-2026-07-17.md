# Grill harvest audit — 2026-07-17

## Purpose

Continue the source and implementation work that is already authorized by the
canonical owner-grill records. This run does not reopen settled choices or
touch Summoning or Dungeoneering before the owner explicitly releases them.

## Inner loop

Each batch has one attributable hypothesis: a named contract slice can be made
complete without crossing an unresolved owner or evidence boundary.

1. Freeze the clean `main` baseline and the relevant contract/source rows.
2. Use bounded read-only surveys where independent inspection improves coverage.
3. Reproduce every claimed gap in the canonical checkout.
4. Implement the smallest coherent batch.
5. Verify targeted pure, integration, undo, asset, and offscreen Qt behavior as
   applicable.
6. Accept only a green batch; update the Memory Bank and commit it normally.

The checker never substitutes persuasion for repository evidence. Source gaps
remain `source_blocked`; player-experience forks go to the ranked design-gap
file.

## Queue

| Program | Authority | Current boundary |
|---|---|---|
| Approved amendments | Owner-approved, design-settled | Survey implementation seams, then ship coherent batches |
| Slayer | Owner grill design-closed | Complete source sweep; implement only source-ready atomic slices |
| Summoning | Owner grill still active | Entirely out of scope until the owner explicitly releases it |
| Dungeoneering | Not design-closed | Out of scope |

## Baseline

- Branch: `main`
- Commit: `2d51d213ab7e6c9a9b6fb397e9b664c9ed892d60`
- Worktree guard: safe
- Linked worktrees: none
- Heartbeat: `ankiscape-grill-harvest`

## Coverage ledger

### Pass 1 — readiness survey

Status: active.

Scopes:

- Approved amendment implementation and verification seams.
- Slayer source-completeness and atomic-slice readiness.

The initially launched Summoning survey leaf was canceled immediately when the
owner clarified that no Summoning work, including source harvesting, should
continue before grill closure. Its partial output is not accepted evidence and
will not be used.

Accepted findings, rejected findings, test evidence, and commits will be
appended here as the run advances.

## Accepted batch — Magic Charge duration

Finding: the live Charge action set an indefinite `magic_charge_active` boolean.
No review-driven duration or migration existed.

Resolution:

- Config v38 persists the source-backed 700-tick duration.
- Every successful review advances temporary effects by 50 ticks per configured
  Action per Review before action dispatch.
- Safe non-combat activity therefore dissipates Charge, while a review that
  casts Charge installs a fresh full duration after advancing the old state.
- The review snapshot restores duration, active state, inventory, and action
  output atomically.

Regression proof:

- The focused regression failed before implementation with missing pure symbols,
  missing migration state, and an indefinitely active effect.
- `tests.test_magic` plus `tests.test_storage_pure`: 49 passed.
- Targeted integration and multiplier/undo holdouts: 3 passed.
- Documentation audit: 235 Markdown and 298 HTML files passed before this
  audit record was added; it will run again at commit closure.

Concurrency note: while this batch was dirty, another task advanced `main` from
`2d51d21` to Summoning-only commit `f10089c`. Its five files do not overlap the
Magic implementation or this audit. This batch will stage only its attributable
files and will not edit or rely on Summoning work.

## Slayer readiness gate

The independent local audit confirms that no live Slayer runtime slice is
source-ready. In particular, no master satisfies the contract's complete
baseline-pool certification rule. Turael/Spria is the smallest likely first
master, but remains only a candidate until its whole pool is certified.

The following are source- or dependency-blocked rather than owner-design gaps:

- exhaustive per-master weights, kill ranges, and gates;
- stable family/variant membership and Slayer-XP eligibility;
- protective-item consequences and the remaining area/context registry;
- point/reward conflicts and Smoking Kills counter initialization;
- playable source-backed stages for the Slayer-owned quest chains.

Finishing-blow semantics, master succession, the Kuradal core context, Social
Slayer's parked disposition, and the VIP-ticket exclusion are already
source/design closed. None is enough to justify a partial live master pool or a
dead Slayer page. The next Slayer work is therefore source harvesting and
machine-checkable pool certification, not runtime exposure.

## Accepted batch — Bank quantity actions

Finding: the Bank still exposed destructive `Discard all` and one-unit Custom
pack edits. Discard bypassed the direct-action undo channel, and the carried
summary counted every unit in a stackable as a separate slot.

Resolution:

- `Discard X…` prompts for an exact positive quantity, preserves the Bank
  remainder, and records one atomic direct-action undo snapshot.
- `Set carried quantity…` edits the active target's desired Custom-pack quantity
  from either the grid or Bank menu.
- The pure setter enforces canonical stackability and the 28-slot budget,
  retains an existing item's insertion position, removes at zero, and appends a
  later re-add.
- The live carried summary now receives the canonical stackable-item set.

Regression proof:

- `tests.test_inventory_pure` plus the full integration smoke module: 123
  passed.
- Focused real offscreen Qt Bank/carried tests: 5 passed.
- Full real offscreen Qt main-menu module: 190 passed in 532.645 seconds.
- Documentation audit: 235 Markdown and 298 HTML files passed.
- Compile, diff, and worktree-layout checks passed.

## Source correction — Magic Charge

The pinned oldid in `magic_data.py` was independently resolved and found to be
the unrelated Charge Prayer page. It is replaced with `Charge (spell)` oldid
`6593039` (2012-11-20), with a data regression preventing recurrence.

That correct page closes the duration/rune/XP facts but also proves the damage
effect depends on a god cape. The paired Mage Arena and God capes revisions
prove one-cape alignment, first-staff reward, 80,000-coin extra staves,
per-spell 100-cast attunement, and statue replacement/reclaim. Those mechanics
do not exist in the current simplified landmark, so the abstraction is ranked
P1 in the morning design-gap file rather than guessed into runtime.

## Accepted batch — Agility carried risk

Finding: the approved dangerous-course amendment had no runtime owner. Agility
failure still read a stale scalar weight, had no target-local food pack, and
could damage LP without sharing the finite carried-inventory death contract.

Resolution:

- Auto and Custom now use the canonical 28-slot target pack. Auto packs course
  requirements before owned food preferences; Custom preserves exact order and
  blocks omitted requirements.
- First engagement primes for free. Depleted food uses a one-review skilling
  bank run, then refills the full projected multi-food layout.
- Failure chance reads Bank-clamped active-pack plus equipment weight. Course
  damage shares auto-eat, threshold, grave, equipment loss, and review undo.
- Wilderness rolls the approved 1% ambush after lap completion but before its
  reward commits. Fatal damage forfeits the uncommitted reward and rolls back
  lap, Pit, and XP-modifier bookkeeping atomically.
- The Skills surface reports projected pack, requirements, food, carried and
  effective weight, bank-run state, and Wilderness risk without leaking
  Combat-only controls.

Checker finding: the first implementation allowed a stale saved carried view
to inflate failure weight after its Bank items were sold or discarded. The
primary reproduced it, clamped both runtime danger and the UI projection to
actual holdings, and added focused regressions.

Regression proof:

- Full core: 1,353 methods passed; 195 environment skips and three declared
  XP-parity expected failures.
- Focused real offscreen Qt: two Agility/Combat carried-surface tests passed.
- Test quality: zero hard issues across 67 files.
- Documentation: 236 Markdown and 298 HTML files passed.
- Compile/diff/worktree checks passed.
- Checkpoint: `69855d9`.
