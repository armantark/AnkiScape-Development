# Split slice contract

Status: **binding on every agent dispatched to split a file.** Written
2026-09-01 by the orchestration seat, after the owner ruled that the repository's
oversized files are to be split literally rather than exempted.

Read this file completely before you edit anything. It sits on top of
`memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md`, which also binds you. If
your per-file brief and either contract disagree, stop and report the conflict
instead of choosing.

## 1. Why this exists

The owner's words: "I want the slop gate to be taken literally. It's only going
to create technical debt to kick the can down the road. Rip off the bandaid."

69 tracked Python files hold more than 1,000 lines each, 294,020 lines in total.
Three separate correctness fixes are currently frozen because the files they
touch may not grow. You are removing that blockage at its source.

## 2. The one rule that decides everything

**Every module you produce must be at or under 1,000 lines, including the
aggregator and every new file.** A new module counts as grown from zero, so
creating a 1,200-line module is as forbidden as growing an existing one.

## 3. What a split is

A **pure move**. Code changes file; nothing else changes.

- The original path stays as an aggregator that re-exports the public surface,
  so **no consumer anywhere changes an import**. If a consumer would have to
  change, you have not done a pure move.
- No renaming, no reordering of public values, no "while I am here" cleanups, no
  reformatting, no docstring improvements, no type-hint additions. Every one of
  those makes the diff unreviewable and hides the one line that mattered.
- If you find a genuine defect while moving code, **do not fix it**. Record it in
  your report. A split that also fixes a bug cannot be verified as a move.

## 4. Split at seams, never at a line count

Cut where the code already divides: one quest per module, one combat family per
module, one dispatcher group per module, one domain per module. The gate's own
message says it: "Split along module seams (a cohesive unit per file), not at an
arbitrary line count."

A module named `part_two` is a failed split. If you cannot reach 1,000 lines at
any real seam, **stop and report the seam you found and why it does not divide
further.** That is a success state, and the answer may be that the file needs a
design change that is not yours to make.

**Never hand-split a generated file.** Change its generator to emit sharded
modules plus an aggregator, then regenerate. A hand-edited generated file is
overwritten by the next generation and the split silently disappears.

## 4a. Three walls the gate puts in front of the obvious layout

The first split of this programme, `data/slayer_data.py`, was refused three times
in one commit. Every wall it hit applies to all eleven files, so the layout below
is not a suggestion.

**Wall one: you may not add a file to a crowded directory.**

```
slop-gate: code files were added to directories already at 40 files:
  data: 104 code files (was 103)
  -> Create a cohesive subdirectory instead of widening this directory.
```

`DIR_FILES_MAX` is 40. Measured on 2026-09-02, four directories are already past
it, and **a new file in any of them is refused whatever it contains**:

```
tests   236      data    104
tools   138      logic    87
```

`logic_pure/`, `runtime/`, `ui/` and `core/` are still under the cap and accept
new files normally.

So a new sibling module beside the file you are splitting is refused outright,
and **this applies to your new tests and any new tool as much as to the modules
you extract**. Put them in a new cohesive subdirectory: `data/slayer/`,
`tests/promotion/`, `tools/promotion/`. A fresh directory starts empty and the
rule does not bite.

**Wall two: the obvious aggregator makes an import cycle.**

```
slop-gate: new import cycles were introduced:
  data/slayer_data.py, data/slayer_master_data.py
  -> Break the cycle by moving the shared contract or dependency to a lower-level module.
```

If the aggregator imports the new module, and the new module imports shared
definitions back from the aggregator, that is a cycle. **Move the shared contract
down**: the dataclasses, base registries and identities that both halves need go
into their own low-level module, which neither imports back. The dependency then
runs one way, from aggregator to parts to contract.

**Wall three: re-exports read as dead code.**

```
slop-gate: new dead code was introduced:
  data/slayer_data.py: unused import 'MAZCHNA_FAMILIES_BY_ID' (90% confidence)
```

An aggregator's whole job is importing names it does not itself use, which is
exactly vulture's definition of a dead import. Declare the re-exported names in
an `__all__` in the aggregator, which states the intent and is the honest fix. If
that does not satisfy the gate, use the repo's vulture whitelist and say in your
report that you did, but try `__all__` first: a whitelist entry per split is
noise that hides real dead code later.

**So the shape of every split is:**

```
data/<domain>/__init__.py        (may be empty)
data/<domain>/contract.py        shared dataclasses and identities, imports nothing upward
data/<domain>/<part_a>.py        real seam
data/<domain>/<part_b>.py        real seam
data/<domain>_data.py            aggregator: imports the parts, declares __all__
```

Names are illustrative; use the domain's real vocabulary rather than `part_a`.
The aggregator keeps its original path so no consumer changes.

## 5. Your proof, which is the point of the slice

`tools/module_surface.py` prints a deterministic dump of a module's complete
public surface and a SHA-256 digest of it.

1. Before you touch anything, record the digest of every module you will affect.
2. After the split, record it again.
3. **They must be byte-identical.** A moved digest means the public surface
   changed, which means it was not a pure move.

If a digest moves, do not adjust the dump and do not pin the new value. Find what
changed and put it back. The digest moving is the tool doing its job.

`tests/test_module_surface.py` pins the baselines. Update the pinned digest only
if the split legitimately changes a module's identity, and say so explicitly in
your report with the reason.

**The root `__init__.py` dumps only under the offscreen Qt interpreter**,
`QT_QPA_PLATFORM=offscreen .venv-qt/bin/python`. Its split runs that proof under
the offscreen lane. Do not skip it: it is the largest and most central file in
the wave, and skipping its proof would leave the riskiest split unverified.

## 6. Verification

**Who runs the lanes, corrected by ruling 41.** As the split author you run
focused tests only: the tests for every file you touch, the existing suite for
any shared file, the module-surface proof in section 5, and the audits below.
Say so in your report.

Both full lanes still run on your branch, but by the separate verification-lane
agent that section 29 requires, not by you. Batching changes only the promotion
gate, never that per-branch verification.

The orchestration seat holds concurrency at four verification lanes at a time.
This project's record contains an occasion where eight concurrent agents each
starting the offscreen Qt lane stalled the machine, and each verification runs
its two lanes in sequence, never together, because they share a checkout and a
concurrent pair has produced a bogus `ImportError` naming a function that plainly
exists.

Report the exact output of each:

```
python3 tools/audit_docs.py
python3 tools/audit_test_quality.py
python3 tools/audit_item_reachability.py
python3 tools/worktree_guard.py audit
git diff --check
```

Never run the two lanes at the same time; they share the checkout and a
concurrent pair has produced a bogus `ImportError` naming a function that plainly
exists. Each takes 850 to 1,150 seconds and exceeds the background-task cap, so
run them under shell-level detachment.

The plain lane reports roughly 515 skips. **The offscreen Qt lane must report a
skip count near 3.** A Qt skip count near the plain lane's is a false pass and
must be reported as a failure, never as green.

A `ui/` split additionally runs the offscreen visual smoke check. Follow
`.claude/rules/qt-offscreen-screenshots.md` exactly: show the dialog, then
resize, then process events several times before any grab, trust widget geometry
probes over pixels, and reproduce the owner's real window size. That file exists
because offscreen grabs produced two false readings.

## 7. The gates

- **Never set `SLOP_GATE_FILE_LINES` or any other `SLOP_GATE_*` variable, for any
  reason.** An agent described setting it to 15000 as raising a baseline; it
  disables the check for the entire repository. That gate is the owner's
  machinery and only he can grant an exception.
- If the complexity gate refuses a readable fix, **stop and report its exact
  message** rather than contorting code to satisfy it. Do not split a function
  into trivial helpers to move a number; that makes the code worse and the metric
  better, and it will be rejected.
- Do not weaken a test, an audit, or a pinned baseline so your work can pass.

## 8. Before you remove any shape

Ruling 37, and it exists because three instructions from this seat caused real
defects by ignoring it. Before you delete a helper, inline a wrapper, merge a
module, or act on any judgement that a shape is unnecessary:

1. Run the size gate on the hypothetical. The shape may exist to keep a file
   under the ratchet.
2. Trace the import direction. The shape may exist to break a cycle.
3. Grep the seam's consumers. The shape may have callers you have not seen.

Record the answer. A finding that fails the check **closes as load-bearing**, and
you say so. One module deleted tonight turned out to be the previous author's
correct answer to this very gate; another was a helper doing a real job.

## 9. Prohibitions

Pass every one of these verbatim to any child agent you spawn.

- Do not delete any worktree, however clean it looks. Owner gate.
- Do not commit to `main`, do not push, do not change git config, do not skip
  hooks, do not use an interactive `-i` flag.
- **Stage and commit by explicit path.** Never `git add -A`, never
  `git commit -a`. Other agents hold uncommitted work in this checkout, and a
  broad add has already swept another seat's staged work into an unrelated
  commit.
- Do not write status-update artifacts. Dispatched agents in this project do not
  create them.
- Do not ask another agent session to rule on a conflict or grant you permission.
  Your orchestrator is your only escalation route.

## 10. Your worktree

```
python3 tools/worktree_guard.py audit
python3 tools/worktree_guard.py lease <branch> --holder <who>
```

The last stdout line is JSON with `path` and `lease_id`. Work there, commit
there, release with `release <path> --lease-id <id>`, and audit again at the end.
Never call `treehouse` directly.

## 11. Your report

- The commit SHA, and the module layout you produced with each module's line
  count.
- The before and after digest for every affected module, stated as identical or
  explained if not.
- The exact output of both lanes and all five audits.
- The seam you split on, in one sentence, and why it is the real one.
- Every defect you found and did **not** fix.
- Anything you stopped at.

Re-measure every number when you write the report. A claim you cannot support is
a defect, and reporting a lane as green when you did not run it is the worst
outcome available to you.
