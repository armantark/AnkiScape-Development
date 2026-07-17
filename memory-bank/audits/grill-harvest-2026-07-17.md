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

## Slayer source batch — Chaeldar pool

Finding: the cutoff master and cross-master tables contain 32 families, but
direct cutoff Grifolapine and Grifolaroo pages restore two stale-table
omissions. Darkan has 32 executable rows totaling 368 but instead omits Shadow
warriors and Mutated zygomites.

Resolution:

- Reconciled 34 ordinary families and a provisional 388-point hidden-weight
  denominator.
- Restored Shadow warriors and Mutated zygomites with explicit 10-point
  common-baseline abstractions.
- Closed Elves at `60–90`, preserved Grotworms' `72–109` only as an observed
  history envelope, and restored the internally consistent 10/50/150 point
  schedule over the cutoff master's anonymous `100` typo.
- Corrected the accepted family gates where Darkan conflicts with cutoff
  evidence: Regicide for Elves, Rum Deal route access for Fever spiders, Magic
  50 for Fungal magi, Magic 60 for the two Grifo families, and Slayer 67 plus
  Branches of Darkmeyer for Vyrewatch.
- Kept Chaeldar runtime-hidden at 0/34 end-to-end family readiness. Three
  ordinary Combat targets are complete, Banshee and generic Baby dragon cannot
  certify their families, and 29 families are absent.

Concrete implementation repair:

- The live level-8 Crawling hand copied game-main's conflicting 12 Slayer XP.
- It now uses the cutoff level/LP/XP tuple `8/160/16` and cites Crawling-hand
  oldid `6530506`; a focused regression pins the contract.
- Banshee's protection consequence and Baby-blue identity remain complete
  implementation blockers rather than receiving partial max-hit/name patches.

Evidence:

- `source-audits/slayer-chaeldar-pool-2026-07-17.md`.
- Read-only workflow `d951e516-fbf0-4aa7-b087-7dd96c786115` supplied separate
  emulator/runtime and period-history surveys; the primary independently
  resolved the accepted union, gate conflicts, point arithmetic and Crawling
  hand correction.
- Focused Crawling-hand/schema regressions: 2 passed.
- Combat logic and enemy-roster holdout: 181 passed.
- Combat logic, enemy-roster, runtime-action, and integration holdout: 342
  passed.
- Full core: 1,366 methods, 196 environment skips, and three declared
  XP-parity expected failures.
- Test quality: zero hard issues across 67 files.
- Documentation, compilation, diff, JSON, and worktree-safety checks passed.
- No owner-level design gap emerged.

## Slayer source batch — Sumona pool

Finding: cutoff Sumona contains 37 families, while Darkan has 35 executable
rows totaling 387 and leaves Scabarites and Terror dogs as comments. The
cross-master table is stale for Black demons and three later ordinary
families, and Darkan conflicts with the cutoff Black-demon and Gargoyle counts.

Resolution:

- Reconciled 37 ordinary families and a provisional 407-point hidden-weight
  denominator.
- Restored Scabarites and Terror dogs with explicit 10-point common-baseline
  abstractions over their commented Darkan stubs.
- Kept Black demons, Grifolapines, Grifolaroos, and Mutated jadinkos from the
  master-specific and individual-family evidence despite cross-table
  omissions.
- Corrected Black demons and Gargoyles to `120–185`, preserved unusual
  historical maxima as observation envelopes, and left the exact
  higher-Combat within-family selection formula `source_blocked`.
- Closed Combat 85, Slayer 35, Smoking Kills, and the 12/60/180 point schedule.
  Preserved the Kalphite Queen challenge's 15,000 Slayer XP, 30 bonus points,
  and one-task credit while leaving its exact offer rule source-blocked.
- Kept Sumona runtime-hidden at 0/37 end-to-end family readiness. Only four
  ordinary candidates are complete, and the family registry, assignment
  generator, task-credit path, Smoking Kills, most targets, and required
  special mechanics do not exist.

Concrete implementation repair:

- Temporary Death spawns incorrectly granted 60 Slayer XP.
- The row now grants no Slayer XP and cites cutoff Death-spawn oldid `6327456`;
  a focused regression pins the no-credit contract.

Evidence:

- `source-audits/slayer-sumona-pool-2026-07-17.md`.
- Read-only workflow `0b971b55-f68c-42a7-bef6-46cd66c215d3` supplied separate
  emulator/runtime and period-history surveys; the primary independently
  reconciled the accepted pool, denominator, gates, count conflicts, challenge,
  and runtime blockers.
- The 37-row ledger is unique and totals 407 points mechanically.
- Combat logic, enemy-roster, runtime-action, and integration holdout: 343
  passed.
- Full core: 1,367 methods, 196 environment skips, and three declared
  XP-parity expected failures.
- Test quality: zero hard issues across 67 files.
- Documentation, compilation, diff, JSON, and worktree-safety checks passed.
- No owner-level design gap emerged.

## Slayer source batch — Duradel/Lapalok pool

Finding: cutoff Duradel/Lapalok contains 35 families. Darkan has 34 executable
rows totaling 324 and omits Scabarites. The cutoff overview tables are stale
for four later families, while several Darkan count/gate rows reflect copied
Kuradal or post-cutoff behavior.

Resolution:

- Reconciled 35 ordinary families and a provisional 334-point hidden-weight
  denominator.
- Restored Scabarites at the explicit 10-point common-master abstraction and
  closed its observed count at `40–79` from direct revision history.
- Restored Ganodermic creatures, Grifolapines, Grifolaroos and Mutated
  jadinkos from direct family/Darkan convergence despite overview omissions.
- Corrected Kalphites to `130–200`, kept four late-family generator ranges
  explicitly provisional, and rejected post-cutoff reconstructed counts where
  cutoff evidence or the pinned emulator disagrees.
- Closed Combat 100, Slayer 50, Shilo Village access, 15/75/225 points and
  Duradel-to-Lapalok succession after While Guthix Sleeps.
- Pinned the 69-kill Slayer Tower challenge, rejecting stale master-page XP
  arithmetic in favor of the dedicated cutoff challenge page: no individual
  Slayer XP, 20,000 XP and 35 bonus points on hand-in.
- Kept Duradel/Lapalok runtime-hidden at 0/35 end-to-end readiness. Three
  ordinary candidates are complete; the family registry, assignment and
  task-credit runtime, most targets, special mechanics, quests, succession and
  challenge ledger do not exist.

Concrete implementation repair:

- Abyssal demon Blood/Law/Nature/coin drops now use the source's exact
  discrete/ranged quantities, and its missing 16/1024 global Rare-table branch
  is live.
- The generic Abyssal-demon target no longer exposes Kuradal's Dungeon-only
  Ferocious ring. The removed branch remains a nothing slot so all other
  probabilities stay stable.

Evidence:

- `source-audits/slayer-duradel-lapalok-pool-2026-07-17.md`.
- Read-only workflow `edac15ac-4a8d-4b97-b7ac-ab30160eb335` supplied separate
  emulator/runtime and period-history surveys; the primary independently
  reconciled the accepted family union, counts, gates, succession, challenge
  conflict and runtime blockers.
- Focused deterministic regressions cover the exact quantity choices/range,
  global Rare-table branch and context-specific ring exclusion.
- Combat logic, enemy-roster, runtime-action and integration holdout: 345
  passed.
- Full core: 1,369 methods, 196 environment skips and three declared
  XP-parity expected failures.
- Test quality: zero hard issues across 67 files.
- Documentation, compilation, diff, JSON and worktree-safety checks passed.
- No owner-level design gap emerged.

## Slayer source batch — Kuradal pool

Finding: cutoff Kuradal contains 36 ordinary families. Darkan has 35
executable rows totaling 312, names the ordinary TzHaar row Volcanic
creatures, and omits Terror dogs. Its count calibration conflicts with nine
direct cutoff rows.

Resolution:

- Reconciled 36 ordinary families and a provisional 322-point hidden-weight
  denominator.
- Mapped Darkan's 70–110 Volcanic-creatures row to ordinary TzHaar and restored
  Terror dogs at the explicit 10-point common-master abstraction.
- Used the direct cutoff master ledger for nine conflicting counts, including
  Jungle strykewyrms `90–160`, Steel dragons `40–108` and Vyrewatch `60–170`.
- Closed Combat 110, Slayer 75, Ancient Cavern access, 18/90/270 points,
  Aquanite's 50-point assignment unlock and the fire-cape-or-2,000-point ice
  strykewyrm route.
- Kept Kuradal's Dungeon as a target-local Combat context with its eight-family
  roster, cannon restriction, Ferocious-ring drops, fixed +40 successful-hit
  bonus, emergency retreat and five-charge teleport behavior.
- Pinned the separate 280-kill Fight Cave challenge: 25,000 Jad bonus XP,
  12,000 stated completion XP, ordinary task points and no bonus challenge
  points.
- Kept Kuradal runtime-hidden at 0/36 end-to-end readiness. Four ordinary
  candidates are complete; the family registry, assignment and task-credit
  runtime, 29 absent families, special mechanics, reward gates, contexts and
  Fight Cave do not exist.

Concrete implementation repair:

- The live level-149 TzHaar-Ket omitted the cutoff assignment's 136 Slayer XP.
  A failing regression reproduced the missing field before the row and source
  note were repaired.

Evidence:

- `source-audits/slayer-kuradal-pool-2026-07-17.md`.
- Read-only workflow `033a9a66-8eb3-4b16-85ce-3cff1eb57c1a` supplied the
  emulator/runtime matrix. Its networked period-history leaf was canceled
  after six minutes with zero tools or progress; the primary independently read
  Kuradal oldid `6588106`, its talk/revision history and the pinned emulator.
- Combat logic, enemy-roster, runtime-action and integration holdout: 345
  passed.
- Full core: 1,369 methods, 196 environment skips and three declared
  XP-parity expected failures.
- Test quality: zero hard issues across 67 files.
- Documentation, compilation, diff, JSON and worktree-safety checks passed.
- No owner-level design gap emerged.

## Slayer implementation batch — Cockatrice protective equipment

Finding: the live Cockatrice target ignored the Mirror shield entirely. A
player could fight without it and receive only ordinary accuracy-rolled melee
damage, omitting the cutoff fixed eye-beam hit and rapid stat drain.

Resolution:

- Pinned Cockatrice oldid `6579848`, Mirror-shield oldid `6283470`, rev-742
  item `4156`, Darkan's fixed maximum-LP/6 hit, and 2011Scape's repeated
  25%-of-base stat drain.
- Recorded the implementation conflicts rather than silently selecting a
  reconstruction. The accepted labeled mapping caps Darkan's level-scaled
  fixed hit at the period-proven 110 LP and stops the five corroborated stat
  drains at the period-proven one-quarter floor.
- Added an exact-slot Mirror-shield check, a guaranteed fixed hit that bypasses
  ordinary accuracy/protection-prayer reduction, persistent current-level
  drains, and aggregate result telemetry.
- Exposed the missing-shield consequence in the existing Combat target tooltip
  without converting a legal dangerous encounter into a lock.
- Kept Banshee unimplemented. Its protection set and affected stats are known,
  but Darkan and 2011Scape conflict on the drain magnitude/selection rule and
  the period effect includes Summoning, which remains outside this program.

Evidence:

- `source-audits/slayer-protective-equipment-cockatrice-banshee-2026-07-17.md`.
- Read-only workflow `79096d5a-3642-428f-84f1-721b0202d4d4` was canceled after
  two overlong attempts failed to produce bounded final reports; none of its
  unverified conclusions were used. The primary independently inspected every
  accepted source and reproduced the runtime defect.
- Regression-first proof: six focused tests reproduce fixed damage, prayer
  bypass, repeated drain/floor behavior, same-review combat impact, exact-slot
  protection, preview state, tooltip warning, and schema.
- Combat logic, enemy-roster, target-metadata, runtime-action and integration
  holdout: 383 passed.
- Real offscreen Qt Combat-picker check: 1 passed.
- Full core: 1,374 methods, 196 environment skips and three declared XP-parity
  expected failures.
- Test quality: zero hard issues across 67 files. Documentation, reachability,
  compilation, diff, JSON and worktree-safety checks passed.
- No owner-level design gap emerged.

## Slayer implementation batch — finisher-item acquisition metadata

Finding: every Slayer finisher supply was purchasable, and each shop stock row
contained its source item ID and stackability, but the generated
`shop_extra_items_as_dict()` projection discarded both. The consolidated item
registry therefore treated Rock hammer and Fungicide spray 10 as stackable and
gave all four supplies no source identity.

Resolution:

- Preserved `source_item_id` and `stackable` from the first canonical stock row
  while building shop-only item metadata.
- Applied the same logic to the generator template and its checked-in output.
- Pinned Bag of salt 4161, Rock hammer 4162, Ice cooler 6696, and Fungicide
  spray 10 7421 through both catalog and registry regressions.
- Kept the finisher engine and all four enemy rows hidden. None is yet a
  complete reachable slice: reconciled Combat/drop rows and enemy assets are
  missing, with additional period/reconstruction conflicts for Rockslug and
  Gargoyle.

Evidence:

- `source-audits/slayer-finishing-blows-2026-07-15.md`.
- Read-only workflow `6c3706e6-f7be-408f-a3bf-217c23d23d3e` certified the
  item/shop facts and family blockers. Its separate Combat-seam leaf timed out
  before a final report; the primary did not rely on that partial output.
- Regression-first proof failed on all eight catalog/registry assertions before
  the repair and passed afterward.
- Shop, shop-logic, registry, and integration holdout: 167 passed.
- Real offscreen Qt shop flows: 3 passed.
- Compilation passed; reachability remains at 1,200 actions / 273 known
  orphans.

## Program closure

The design-settled queue is closed:

- Magic Charge, Bank Discard X/carried ordering, Agility risk packs, and
  Farming Dig up/presets/full run are implemented and committed.
- Every functional cutoff Slayer-master pool is source-reconciled.
- Source-ready live defects found during the harvest were repaired:
  Shade/Crawling-hand/TzHaar Slayer XP, Death-spawn XP exclusion,
  Abyssal-demon drops, Kuradal-context Ferocious-ring exclusion, Cockatrice
  protection, and shop-only item identity/stackability.
- Remaining Slayer runtime is dependency- or source-blocked, not waiting on an
  unstated implementation decision. No master can be exposed without
  renormalizing around missing families; finishers lack a jointly certified
  target/runtime/asset slice; Banshee still crosses the excluded Summoning
  boundary; required quests, contexts, challenge ledgers, and reward routes are
  incomplete.

Closure verification:

- Core discovery: 1,376 methods; 1,177 ordinary passes, 196 environment skips,
  and three declared XP-parity expected failures.
- Real offscreen Qt discovery: 1,376 methods; 1,373 ordinary passes, no skips,
  and the same three expected failures.
- Test-quality audit: zero hard issues across 67 files.
- Documentation audit: 245 Markdown and 301 HTML files, clean.
- Reachability: unchanged at 1,200 actions and 273 known orphans (110 root,
  163 cascade).
- Compilation, JSON, diff, and worktree-safety checks passed.
- No new owner-level design gap emerged. The two pre-existing ranked questions
  were subsequently resolved and are preserved in
  `archive/2026-07/resolved-queues/design-gaps-grill-harvest-2026-07-17.md`.
- Results artifact:
  `status-updates/grill-harvest-results-2026-07-17.html`; mobile copy:
  <https://co9e6hzqn0pd.postplan.dev>.

## Post-closure follow-up — Mage Arena and Farming cure policy

The owner approved the recommended Mage Arena alignment/attunement abstraction
and selected an ordered two-option Farming cure policy.

Accepted implementation:

- Mage Arena's final form requires a chosen god and grants that first matching
  cape, staff, and spell attunement. Other god spells consume one explicit
  attunement review after their shop-bought staff is owned.
- Instant statue actions preserve the one-cape limit and direct-action undo.
  Mismatched god cape/staff equipment is rejected.
- Charge's +100 LP maximum-hit effect now reaches preview and live combat only
  for the matching attuned god spell and worn loadout.
- Farming plans and presets store `Plant cure first` or `Cure Plant first`.
  Queued cure steps snapshot the choice and try the other route atomically when
  the preferred resource path is unavailable.
- Config v40 migrates Mage Arena alignment/attunements and sanitizes the new
  Farming preference without invalidating completed legacy arenas.

The implementation review also caught and repaired three concrete integration
defects before closure:

- The first cape transcription zeroed its sourced 1/1/2 melee defence bonuses.
- God staves were not registered as magic weapons, so Combat preview silently
  used melee math.
- The cape item rows inherited generic defaults, losing their cache IDs and
  incorrectly becoming stackable and tradeable.

The equipment generator, magic staff registry, and canonical item manifest now
carry those fixes with regression coverage.

Follow-up verification:

- Focused Mage Arena, Farming, equipment, registry, runtime, integration, and
  migration coverage: 192 methods passed.
- Focused real offscreen Qt controls: two methods passed.
- Full core discovery: 1,388 methods, 1,189 ordinary passes, 196 environment
  skips, and three declared XP-parity expected failures.
- Full real offscreen Qt discovery: 1,388 methods, 1,385 ordinary passes, no
  skips, and the same three expected failures.
- Test quality: zero hard issues across 67 files. Documentation, compilation,
  JSON, reachability, asset provenance, diff, and worktree-safety checks pass.
- Reachability remains at the established 1,200-action / 273-known-orphan
  baseline.
- Follow-up results artifact:
  `status-updates/mage-arena-farming-cure-results-2026-07-17.html`; mobile
  copy: <https://q0wso578s42a.postplan.dev>.
