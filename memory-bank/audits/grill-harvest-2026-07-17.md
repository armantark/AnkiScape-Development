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

## Accepted batch — Farming replacement and whole-farm presets

Finding: the approved post-closure amendment had no live owner. Mature
regrowth crops could not be deliberately removed, the farm sheet had only
per-patch plans, planned gardener intent still followed the old immediate-pay
path, and full-run omissions were not reportable.

Resolution:

- `Dig up` is a one-review, zero-reward, Spade-gated verb for healthy mature
  regrowth crops. A differing full-run plan queues `Dig up` then `Plant`; the
  manual action queues only `Dig up`.
- User-named presets snapshot selected patch plan policies without transient
  paid-protection or Fertile Soil state. Selection is inert; apply is atomic;
  save/update/rename/duplicate/delete remain compact under one management menu.
- Plans now carry explicit gardener, watering, and item-cure policy. Full runs
  pay selected gardeners while building the queue and report whole-patch skips
  when payment is missing.
- Newly paid gardener goods are validated escrow on the planting step.
  Removing, clearing, or skipping that step refunds them; successful planting
  consumes them.
- Storage v39 adds preset/order/selection/skip defaults while preserving
  unknown state.

Checker findings:

- The first escrow implementation stranded payment when a paid step was
  removed, cleared, reordered into failure, or skipped. The primary reproduced
  it and added exact refund semantics.
- Duplicating a 60-character preset could sanitize back to the original name.
  Duplicate suffixes now fit inside the 60-character limit and remain unique.

Regression proof:

- Focused logic/storage/integration: 176 methods passed.
- Final focused real offscreen Qt Farming/HUD/dispatcher: 84 methods passed.
- Full core: 1,363 methods, 1,164 ordinary passes, 196 environment skips, and
  three declared XP-parity expected failures.
- Full real offscreen Qt: 1,363 methods, 1,360 ordinary passes, no skips, and
  the same three expected failures.
- Test quality: zero hard issues across 67 files.
- Compile/diff/worktree checks passed.
- Checkpoint: `9b65f45`.

## Slayer source batch — Turael/Spria pool

Finding: the cutoff master pages were not complete enough to certify even the
smallest Slayer master. They omitted both 2012 families, contained an anonymous
Troll-row insertion contradicted elsewhere, exposed no weights, and disagreed
on the Icefiend count.

Resolution:

- Reconciled a 23-family functional Turael/Spria pool.
- Recovered Gelatinous abominations from the cutoff creature, Troll Warzone,
  and Spiked-gauntlet pages; recovered Grotworms from all three cutoff monster
  pages plus Darkan.
- Rejected Turael Trolls from the cutoff cross-master table and Darkan
  convergence.
- Closed Icefiends at 10–20 and recorded every hidden weight as provisional.
  Darkan's raw ratios, game-main's percentages, and the recovered 30-weight
  Gelatinous family close one 355-point denominator exactly.
- Kept the role runtime-inactive because six families and two special
  kill/protection effects remain baseline blockers.

Concrete implementation repair:

- The source pass found that live Cave slime combat had dropped
  `poisonDamage = 3` from its pinned game-main definition.
- The row now carries that value, and a deterministic Combat regression proves
  the poison reaches persistent player status.

Evidence and verification:

- Source record:
  `source-audits/slayer-turael-spria-pool-2026-07-17.md`.
- Read-only workflow `d1d846df-f0f1-44f7-ad7a-6533ee2e02b3` supplied separate
  emulator and period-history surveys; the primary independently found the two
  omitted 2012 families and synthesized the accepted pool.
- Focused Cave slime poison regressions: 2 passed.
- Combat logic, runtime-action, and integration holdouts: 336 passed.
- Test quality: zero hard issues across 67 files and 1,364 methods.
- Documentation, compilation, diff, JSON, and worktree-safety checks passed.
- No owner-level design gap emerged.

## Slayer source batch — Mazchna/Achtryn pool

Finding: no single local source contained the whole second functional master
pool. Cutoff Mazchna had an anonymous `40–85` count mutation, Achtryn omitted
Cyclopes and Grotworms, Darkan could not instantiate Mogres or Wall beasts, and
game-main explicitly left ten families unfinished.

Resolution:

- Reconciled 27 ordinary families and a provisional 325-point hidden-weight
  denominator.
- Restored Mogres and Wall beasts from cutoff master, cross-master, and
  individual-monster evidence. Their 10-point weights are explicit
  common-baseline abstractions because the hidden values did not survive.
- Rejected `40–85`: the earlier edit described as a Jagex Knowledge Base task
  correction, cutoff Achtryn, and Darkan all converge on `40–70`.
- Preserved Cyclopes at `30–60` and Wall beasts at `10–20`; the repaired
  cutoff row span closes Grotworms at `40–70` over Darkan's conflicting
  `20–40`.
- Kept the role runtime-inactive because ten families have no Combat target,
  Banshee/Cockatrice/Hobgoblin remain mechanically incomplete for Slayer, and
  the stable assignment-family registry does not exist.

Concrete implementation repair:

- The source pass found that live Cave crawler combat had dropped
  `poisonDamage = 8` from its pinned game-main definition.
- The row now carries that value, and a deterministic Combat regression proves
  the 80-LP initial poison reaches persistent player status.

Evidence:

- `source-audits/slayer-mazchna-achtryn-pool-2026-07-17.md`.
- Read-only workflow `8ea520db-346c-4d41-a37f-414e9e373929` supplied separate
  emulator/runtime and period-history surveys; the primary independently
  resolved the anonymous count mutation and complete period family union.
- Focused poison/schema regressions: 2 passed.
- Combat logic, runtime-action, and integration holdouts: 336 passed.
- Full core: 1,364 methods, 196 environment skips, and three declared
  XP-parity expected failures.
- Test quality: zero hard issues across 67 files; the duplicated Cave
  slime/Cave crawler poison checks were consolidated into one data-driven
  behavioral regression.
- Documentation, compilation, diff, JSON, and worktree-safety checks passed.
- No owner-level design gap emerged.

## Slayer source batch — Vannaka pool

Finding: cutoff Vannaka contains 35 families, while Darkan contains 34
executable rows totaling 450, adds Trolls, and cannot instantiate Mogres or Sea
snakes because those family enums are comments. The cutoff Grotworm row records
one observed assignment of 69 rather than a range.

Resolution:

- Reconciled 35 ordinary families and a provisional 460-point hidden-weight
  denominator.
- Rejected Darkan's Troll row from cutoff master and cross-master convergence.
- Restored Mogres and Sea snakes with explicit 10-point common-baseline
  abstractions. game-main's explicit 2.17% ordinary-family values independently
  round from `10 / 460`, but its active input table remains deliberately
  incomplete.
- Used Darkan's ordinary `60–120` Grotworm range as the smallest labeled count
  abstraction rather than converting a single observed 69 into a fixed task;
  period talk history also reports 78.
- Kept Vannaka runtime-hidden because 23 families have no Combat target and the
  family registry, player gates, routes, protective equipment, lures, and
  special kill methods remain incomplete.

Concrete implementation repair:

- The live Stronghold Shade copied game-main's conflicting 4.2 Slayer XP and
  granted ordinary damage XP.
- It now uses the cutoff 3.5 Slayer XP and the existing 0.25 NPC XP multiplier.
  A deterministic Combat regression proves both ordinary combat and
  Constitution damage XP are quartered.

Evidence:

- `source-audits/slayer-vannaka-pool-2026-07-17.md`.
- Read-only workflow `f3f3ff2a-db8d-424f-8f1b-498eea5c914a` supplied separate
  emulator/runtime and period-history surveys; the primary independently
  resolved the accepted 35-family union and Shade correction.
- The emulator survey also found and the primary corrected the earlier Turael
  audit's false statement that game-main had no active assignment generator.
- Focused Shade/schema regressions: 2 passed.
- Combat logic and enemy-roster holdout: 180 passed.
- Combat logic, enemy-roster, runtime-action, and integration holdout: 341
  passed.
- Full core: 1,365 methods, 196 environment skips, and three declared
  XP-parity expected failures.
- Test quality: zero hard issues across 67 files.
- Documentation, compilation, diff, JSON, and worktree-safety checks passed.
- No owner-level design gap emerged.
