# Grill decisions: remove recurring work from AnkiScape

Date: 2026-09-21. Source questions: `fable-grill-papercuts-2026-09-19.md`.
The owner answered Q1, Q2, Q3, Q5 and Q6. The owner delegated Q4 to the grill
with one criterion: a working product that is maintainable and pleasant to read.

This file records decisions. It does not authorize implementation, a push, or a
resume of the paused implementation goal.

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
  `goal-priority-matrix.md:9`, `progress.md:13576`. No tool reads any of them.
  `memory-bank/GOAL-BLOCKED.md` does not exist.

## Decision list

| # | Problem | Selected | Rejected and why | Caller step removed | Contract kept | Proof needed |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Core constants need image folders on disk at import. | Leave it. | Provenance-driven paths: removes 1 of 131 checks. Constants split: broad rewrite for one archive incident. | None. | Runtime unchanged. | None. |
| 2 | Generated rows drift when an external source folder changes. | Each generated file records a digest of every source file it read. The generator refuses to run when a digest differs, unless the caller passes `--accept-source-change`. | Vendored source copy: large third-party file, licence unknown. Leave it: keeps the diagnosis step. | "Which source produced these rows." | Count pins unchanged. | Regeneration from the same source is a no-op. A changed source refuses without the flag and succeeds with it, and the header line changes in the diff. |
| 3 | Nobody knows where remote test time goes. | The runner records elapsed seconds for sync, remote preparation and test execution in its summary on every run. | Pick a cache now: no invalidation rule. Accept the cost: keeps the guess. | Diagnosis before any speed change. | Full lanes, floors, mirror lock, serial ownership unchanged. | A real run prints three durations. |
| 4 | Moving a function to a new file fails the module-surface digest, because the digest embeds the defining module name. | Drop the defining module from a published object's identity in `tools/module_surface.py`. Identity becomes the published path plus the qualified name. Rule 5a is amended: a move must keep a re-export at the old path, and nothing else. Remove the five `__module__ = __name__` rewrites in `logic/shop_logic.py`. | Never move: keeps large files large, fails the maintainability criterion. Move and regenerate pins: pins come from the remote lane, so every move pays a full run before commit. Rewrite `__module__` per move: existing practice, boilerplate on every move. | The failed-full-run-then-diagnose loop, and the per-move rewrite. | Old import paths keep working through re-exports. Data files still prove byte-for-byte equality (rule 5b). All other pins and validators unchanged. | Digest on an unchanged tree equals the once-regenerated pin. Digest on candidate `a8137bab` shows no mismatch beyond its intended changes. Full plain and Qt lanes pass. |
| 5 | Five files own the paused status. | `memory-bank/GOAL-BLOCKED.md` owns it, per the global goal-pause convention. The current checkpoint content moves into it. Active context, loop queue and priority matrix each keep one pointer sentence and no status. The progress log stays as history. | Active context as owner: prose that agents rewrite often. Leave it: five-file update on resume. | Four edits on resume. | The goal stays paused. Resume is manual. | After the move, one grep for "paused" in current files finds the owner and pointers only. |
| 6 | Four more generators drift the same way as equipment. | One shared digest helper, applied to all five external-source generators. | Equipment only: leaves four generators with the diagnosis step. | Same as 2, four more times. | Same as 2. | Same as 2, per generator. |

Decision 4 reopens the module-surface rule. The grill did this because the
hazard the rule names does not exist in this product, and the owner's criterion
is maintainability. The change is reversible: restore the module name in the
identity function and regenerate the pins.

## Ordered implementation handoff

Each step is independent. Smallest and safest first.

1. Decision 5. Load the `goal-pause` skill for the file format. Move the
   checkpoint content into `memory-bank/GOAL-BLOCKED.md`. Replace the status
   sentences in the three current files with pointers. Do not resume the goal.
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

## Unresolved owner choices

- Resume the implementation goal or leave it paused.
- After step 4, merge the Magic candidate as it stands, or rework it first.
  The grill did not inspect its content beyond the digest failure.
- Whether the amended module-surface rule needs a fresh owner ruling line in
  the rulings ledger, or whether this record is enough.
