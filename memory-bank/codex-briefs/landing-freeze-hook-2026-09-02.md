# Slice brief — the landing freeze becomes machinery

Date: 2026-09-02. Author: the orchestration seat. Consumer: one dispatched
implementation agent.

Fold this file into `memory-bank/codex-briefs/` when the current landing window
closes; it lives in `pending/` because ruling 38 forbids touching tracked files
during an open window.

## 0. Read first

`memory-bank/codex-briefs/STANDING-SLICE-CONTRACT.md` binds you. Read it
completely. If it and this brief disagree, stop and report the conflict.

## 1. The problem, in plain terms

Landing a slice on `main` is a fast-forward, so it refuses if `main` moves while
the gate runs. A gate cycle costs about forty minutes, and every refusal costs
another one.

Tonight that happened three times. Twice the offending commit was the
orchestrator's own, once twenty minutes after it had asked another seat to hold.
The rule was understood, agreed, written down, and then broken by reflex, which
is the signature of a rule that needs machinery rather than another reminder.

## 2. What to build

A tracked hook, `tools/landing_freeze_hook.py`, that refuses any commit on
`main` in the canonical checkout while a promotion gate holds a live landing
lock.

The lock already exists; you are not inventing state. `tools/promotion_gate.py`
writes a landing lock record during both `run` and `land`, through
`claim_landing_lock`, carrying the pid, the operation and the commit. Read that
function and use what it already records rather than adding a parallel
mechanism.

Requirements:

1. **Refuse only what needs refusing.** A commit on `main` in the canonical
   checkout, while a lock exists whose pid is alive. Commits on any `goal/*`
   branch, in any linked worktree, or when no gate is running, must pass
   untouched. Slice agents commit constantly during a gate and must not be
   blocked.
2. **A stale lock must not wedge the repository.** If the recorded pid is dead,
   the lock is stale: say so and allow the commit. A hook that blocks forever
   after a crashed gate is worse than no hook.
3. **The message must tell the reader what to do.** Name the gate's commit and
   pid, and state the ruling-38 practice: during an open window, write ledger
   sections, papercuts, briefs and harvests as new untracked files under
   `memory-bank/pending/`, and fold them into their tracked homes in one
   path-scoped commit after the land. Someone hitting this at midnight should
   not have to find a ruling to know the next step.
4. **No override.** No environment variable, no flag, no escape hatch. An
   overridable freeze is the gate that was disabled earlier tonight by an agent
   who believed it was raising a threshold.
5. **Install it through the tool.** Add `promotion_gate.py install-hook`, which
   installs it as the repo-local `.git/hooks/pre-commit`. The fleet's global
   pre-commit chains a repo-local hook first, so the two coexist; confirm that
   by reading the global hook rather than assuming it.
6. **Make its absence visible.** `tools/worktree_guard.py audit` should report
   when the hook is not installed. A safety device nobody notices is missing is
   not a safety device.

## 3. Verification, which is the interesting part

Do not test this by reasoning about it. Prove each behaviour by driving it, and
show the output:

- With a live lock, a commit on `main` in the canonical checkout is refused, and
  the message names the commit and pid.
- With the same live lock, a commit on a `goal/*` branch in a linked worktree
  succeeds.
- With a lock whose pid is dead, a commit on `main` succeeds and the staleness
  is reported.
- With no lock at all, nothing changes.
- `worktree_guard.py audit` reports the hook missing when it is, and is quiet
  when it is not.

Manufacture the lock states rather than waiting for a real gate. **Never start a
real promotion gate to test this**; one is running now and a second concurrent
pair of lanes produces bogus failures.

Run your focused tests plus the existing suites for anything you touch. Do not
run either full lane.

Also report the exact output of `python3 tools/audit_docs.py`,
`python3 tools/audit_test_quality.py`, `python3 tools/worktree_guard.py audit`
and `git diff --check`.

## 4. Constraints

Pass all of these verbatim to any child agent you spawn.

- Never set `SLOP_GATE_FILE_LINES` or any other `SLOP_GATE_*` variable. Every
  new file must be at or under 1,000 lines, and you must not grow a file already
  above it. If the gate refuses you, stop and report its exact message.
- Never change git config. Installing a repo-local hook file is not a config
  change; if you find yourself reaching for `git config`, stop and report.
- Stage and commit by explicit path. Never `git add -A`, never `git commit -a`.
- Do not commit to `main`, do not push, do not skip hooks, do not use an
  interactive `-i` flag.
- Do not delete any worktree. Owner gate.
- Do not weaken any test or audit. Do not write status artifacts.
- Before you remove or simplify any existing shape, apply ruling 37: run the
  size gate on the hypothetical, trace the import direction, grep the consumers,
  and record the answer. Three defects tonight came from skipping that check.

## 5. Report

The commit SHA, the five driven behaviours with their actual output, how you
confirmed the global hook chains the repo-local one, the audit outputs, and
anything you stopped at.
