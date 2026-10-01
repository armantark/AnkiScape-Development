# Grill decisions: remove recurring work from AnkiScape

Date: 2026-09-21. Source questions: `fable-grill-papercuts-2026-09-19.md`.
The owner answered Q1, Q2, Q3, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13, Q14 and Q15. The owner delegated Q4 to the
grill with one criterion: a working product that is maintainable and pleasant to
read.

This file records decisions. It does not authorize a push. The owner stated on
2026-09-21 that the implementation goal is running again in an Astra thread on
Codex; the paused status in the memory bank is stale.

## Facts verified during the grill

- `core/constants_parts/skill_catalog.py:56` lists the tree image folder at
  import. Top-level "file exists" checks at import: `core/constants.py` 7,
  `activity_assets.py` 47, `activity_updates.py` 51, `skill_assets.py` 22,
  `skill_catalog.py` 4. None under `logic/`, `logic_pure/` or `data/`.
- `/Users/ArmanTarkhanian1/Downloads/game-main` is not a git checkout. It has no
  revision to record.
- Generators that read outside the repository: `generate_equipment_data.py`,
  `generate_smithing_data.py`, `generate_summoning_catalog.py` (game-main);
  `generate_construction_data.py`, `generate_npc_shop_data.py` (Darkan).
  `generate_ge_period_data.py` reads a checked-in source file.
- `tools/run_remote_tests.py` labels "worktree sync" and "remote Qt interpreter
  link" but records no elapsed time for them. Only the unittest `Ran ... in`
  line carries a duration.
- No product module imports `pickle` or `marshal`. The save is JSON under the
  Anki collection config key `ankiscape_player_data` (`core/storage.py:12`).
  The module-surface rule in `codex-briefs/SPLIT-SLICE-CONTRACT.md` section 5a
  justifies defining-module identity by "a consumer that unpickles a saved
  object". No such consumer exists.
- `logic/shop_logic.py:107-111` already rewrites `__module__` on five moved
  functions to satisfy the digest. The Magic candidate `a8137bab` moved three
  functions without that rewrite and failed two digest pins.
- Five current files state the paused status: `activeContext.md:7`,
  `pause-checkpoint-2026-09-18.md:3`, `loop-queue.md:4-6`,
  `goal-priority-matrix.md:9`, `memory-bank/archive/progress-2026-09.md:1459`. No tool reads any of them.
  `memory-bank/GOAL-BLOCKED.md` does not exist.

## Decision list

| # | Problem | Selected | Rejected and why | Caller step removed | Contract kept | Proof needed |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Core constants need image folders on disk at import. | Leave it. | Provenance-driven paths: removes 1 of 131 checks. Constants split: broad rewrite for one archive incident. | None. | Runtime unchanged. | None. |
| 2 | Generated rows drift when an external source folder changes. | Each generated file records a digest of every source file it read. The generator refuses to run when a digest differs, unless the caller passes `--accept-source-change`. | Vendored source copy: large third-party file, licence unknown. Leave it: keeps the diagnosis step. | "Which source produced these rows." | Count pins unchanged. | Regeneration from the same source is a no-op. A changed source refuses without the flag and succeeds with it, and the header line changes in the diff. |
| 3 | Nobody knows where remote test time goes. | The runner records elapsed seconds for sync, remote preparation and test execution in its summary on every run. | Pick a cache now: no invalidation rule. Accept the cost: keeps the guess. | Diagnosis before any speed change. | Full lanes, floors, mirror lock, serial ownership unchanged. | A real run prints three durations. |
| 4 | Moving a function to a new file fails the module-surface digest, because the digest embeds the defining module name. | Drop the defining module from a published object's identity in `tools/module_surface.py`. Identity becomes the published path plus the qualified name. Rule 5a is amended: a move must keep a re-export at the old path, and nothing else. Remove the five `__module__ = __name__` rewrites in `logic/shop_logic.py`. | Never move: keeps large files large, fails the maintainability criterion. Move and regenerate pins: pins come from the remote lane, so every move pays a full run before commit. Rewrite `__module__` per move: existing practice, boilerplate on every move. | The failed-full-run-then-diagnose loop, and the per-move rewrite. | Old import paths keep working through re-exports. Data files still prove byte-for-byte equality (rule 5b). All other pins and validators unchanged. | Digest on an unchanged tree equals the once-regenerated pin. Digest on candidate `a8137bab` shows no mismatch beyond its intended changes. Full plain and Qt lanes pass. |
| 5 | Five files state a paused status that is no longer true. The owner resumed the implementation goal in an Astra thread on Codex. | Remove the paused status from `activeContext.md`, `loop-queue.md`, `goal-priority-matrix.md` and `pause-checkpoint-2026-09-18.md`. Record the resume date and the thread in the active context. Create no blocker file. The progress log stays as history. | A blocker file as owner: would tell the next agent to stop work in progress. Leave it: stale status in four files. | Reconciling stale status against a running thread. | Resume is an owner act; agents do not restart a goal. | One grep for "paused" in current files finds history only. |
| 6 | Four more generators drift the same way as equipment. | One shared digest helper, applied to all five external-source generators. | Equipment only: leaves four generators with the diagnosis step. | Same as 2, four more times. | Same as 2. | Same as 2, per generator. |

Decision 4 reopens the module-surface rule. The grill did this because the
hazard the rule names does not exist in this product, and the owner's criterion
is maintainability. The change is reversible: restore the module name in the
identity function and regenerate the pins.

| 7 | The memory bank and the running thread disagree on goal status. | Same as 5. The owner is the only actor who pauses or resumes. | None. | Same as 5. | Same as 5. | Same as 5. |
| 8 | Offscreen Qt tests do not settle native reviewer behaviour. The owner finds reviewer bugs in play and writes pass notes. | The implementing thread runs a native check in real Anki for each slice it lands, through Codex computer use: review five cards, check the HUD, one level-up, one bank run, one undo. The owner's play notes stay the backstop. | A per-landing checklist file: the owner declined new process; the check belongs to the slice. Nothing: the owner stays the test rig. | The owner as first tester of each slice. | Full lanes and the landing gate unchanged. | The slice record names the Anki revision loaded and what the check saw. |

| 9 | The handoff competes with the gameplay queue for the running thread. | Superseded by decision 14: the module-surface change goes first, then the rest of the handoff, then gameplay. | All four first: delays visible work for changes the owner never sees. Gameplay first: every later slice keeps paying the recurring cost. | None; this is ordering. | Unchanged. | None. |
| 10 | Slice results are written for agents, not the owner. | One plain sentence per landed slice, in the owner's words, appended to a running results artifact for the block. When the owner explicitly pauses the goal, the thread wraps up with a status artifact of what the run completed at gameplay level, plus any high-level architectural change that supported it. | Commit messages only, or thread messages only: nothing the owner can read in one place. | The owner reads git log or code to learn what the game gained. | The artifact rule: one plan artifact, one results artifact per block. | The artifact exists and each sentence names a gameplay change. |
| 11 | The record demanded MacBook lanes for every step, stricter than the gate. | Step 1 lands as a docs-only commit with no gate. Step 2 lands through the gate on this Mac. Steps 3 and 4 land through the gate with the MacBook lanes. | MacBook lanes for all: two remote runs for changes that cannot alter gameplay. | Two remote runs. | Both full suites still run for every code change; the gate's own flag is the only tier. | Gate receipts for steps 2 to 4. |

| 12 | A slice commits raw logs, canaries, diffs and screenshots, plus a bespoke runner and checker per slice. Evidence grew from 33 MB to 147 MB in two weeks and agents write then re-read it. | A slice commits its gate receipt and a summary of at most 30 lines: what ran, the exact command, the digest of each raw artifact. Raw artifacts go to the out-of-tree evidence directory the gate already uses, named by commit hash. No per-slice runner or checker scripts; a new check becomes a test. | Compress and cap in-tree: still written and re-read. Leave it: the largest token sink stays. | Writing, committing and re-reading raw evidence. | Provenance: every raw artifact is reachable by digest and commit hash. The gate's receipt is unchanged. | A landed slice shows one summary file and no new file under `memory-bank/evidence/` or `tools/combat/run_*`. |
| 13 | Every session reads the full progress log (13,591 lines) and kanban (2,259 lines) before work. | Rotate. The progress log keeps the current month; earlier months move to dated archive files that nothing reads by default. Shipped kanban cards older than 30 days move to an archive card file. The active context names the archives. Rotation happens on the first session of each month. | Leave whole and skim: the cost is paid by every agent every wake. | About 16,000 lines of reading per agent start. | No record is deleted. | Session-start files total under 3,000 lines after rotation. |
| 14 | The priority-0 extraction is blocked on the module-surface identity rule. | Handoff step 4 runs first. | Keep the order: nothing at priority 0 lands. | The block. | Same as decision 4. | Same as decision 4. |
| 15 | Weekly commit counts punish the calendar, because the owner cannot run the loop for days at a time. | The pace meter is product landings per active orchestrator day, from the landing receipts, target 10, reported in the results artifact at each pause. | Weekly counts: measure the owner's availability, not the process. | Guessing whether the process got faster. | None. | The pause artifact carries the number. |

## Ordered implementation handoff

Run in this order (decision 14): step 4, then step 1, then steps 5 and 6 below, then steps 2 and 3, then return to the gameplay queue.

1. Decisions 5 and 7. Remove the paused status from the four current files and
   record the resume in `activeContext.md`. Create no blocker file.
2. Decision 3. Add elapsed-seconds capture around the three phases in
   `tools/run_remote_tests.py` and print them in the summary. No behaviour
   change to acceptance.
3. Decisions 2 and 6. Write one helper in `tools/` that hashes a list of source
   paths, writes the digests into a generated header, reads them back, and
   refuses on mismatch unless `--accept-source-change` is passed. Apply it to
   the five generators. Regenerate each file once to add the header, and prove
   that no data row changed.
4. Decision 4. Change `_qualified_object` and `_qualified_type` in
   `tools/module_surface.py` to omit the defining module. Regenerate the pins in
   `tests/test_module_surface.py` from the remote lane once. Remove the five
   rewrites in `logic/shop_logic.py`. Amend section 5a of
   `codex-briefs/SPLIT-SLICE-CONTRACT.md`. Run the digest against candidate
   `a8137bab` as evidence only; do not merge it.

5. Decision 12. Move every file under `memory-bank/evidence/` and the raw
   artifacts under `memory-bank/source-audits/` into the out-of-tree evidence
   directory, keyed by the commit that produced them, and leave one summary
   file per slice in their place with the digests. Delete the per-slice
   `tools/combat/run_*_remote.py` and `check_*_guards.py` scripts after
   confirming their checks exist as tests, or convert each into a test first.
6. Decision 13. Move progress-log sections dated before 2026-09-01 into
   `memory-bank/archive/progress-2026-05-to-08.md` and shipped kanban cards
   older than 30 days into `memory-bank/archive/kanban-shipped-2026.md`. Name
   both in `activeContext.md`. Add the monthly rotation rule to the matrix's
   authority section.

## Unresolved owner choices

- After step 4, merge the Magic candidate as it stands, or rework it first.
  The grill did not inspect its content beyond the digest failure.
- Whether the amended module-surface rule needs a fresh owner ruling line in
  the rulings ledger, or whether this record is enough.

## Copy this prompt into the Astra thread

```text
<context>
The owner ran a design grill with Fable on 2026-09-21. The decisions are in /Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/memory-bank/handoffs/fable-grill-papercuts-2026-09-21-decisions.md. Read that file first, then the facts it cites, before you change anything. The implementation goal is running in this thread; the paused status in the memory bank is stale and step 1 corrects it.
</context>

<task>
Implement the steps under "Ordered implementation handoff" in the order that section states: step 4 first, then 1, 5, 6, 2, 3, one commit per step, on the working branch, then return to the gameplay queue. Each step lists the proof it needs; produce that proof and record it in the commit message and in memory-bank/progress.md. Step 4 runs the digest against candidate a8137bab as evidence only; do not merge, rebase or rework that candidate, because that is an owner choice. For every landed slice, gameplay or handoff, append one plain sentence in the owner's words to the running results artifact under memory-bank/status-updates/, naming what the game gained; no test counts, no file names. When the owner explicitly pauses the goal, wrap up with a status artifact of what the run completed at gameplay level, plus any high-level architectural change that supported it, and open it in Zen.
</task>

<constraints>
Work only in the canonical checkout or in a worktree leased through python3 tools/worktree_guard.py lease; never create a worktree under addons21 and never call treehouse directly. Never pass --no-verify, never amend, never push, never set any SLOP_GATE_ variable. Steps 1 and 6 are docs-only and land without the gate. Steps 2 and 5 land through tools/promotion_gate.py on this Mac. Steps 3 and 4 land through the gate with --remote-lanes. From now on a slice commits only its gate receipt and a summary of at most 30 lines with the digest of each raw artifact; raw logs, canaries, diffs and screenshots go to the out-of-tree evidence directory keyed by commit hash, and no slice writes its own runner or checker script. Both full suites run for every code change; a focused run is not acceptance. Do not change any user interface. Do not loosen a pin, floor or validator to make a step pass; if a step cannot pass under the constraints, stop and report why.
</constraints>

<completion_check>
Before you report done, confirm all six steps each have a commit hash, a gate receipt where the step requires one, its proof recorded, and its sentence in the results artifact. Name any step you did not finish and why. Do not describe work you have not committed as done.
</completion_check>
```
