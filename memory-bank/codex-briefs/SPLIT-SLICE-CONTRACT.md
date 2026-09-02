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

Run on your branch and report the exact output of each:

```
/opt/homebrew/bin/python3 run_tests.py
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests
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
