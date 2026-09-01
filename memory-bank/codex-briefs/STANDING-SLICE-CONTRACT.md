# Standing slice contract

Status: **binding on every dispatched implementation agent.** Written
2026-08-19 by the orchestration seat so each brief can point here instead of
restating the same rules and losing one of them.

Read this file completely before you edit anything. Nothing in a brief
overrides this file. If a brief and this file disagree, stop and report the
conflict instead of choosing.

## 1. Worktree placement is a runtime-safety boundary

Anki imports every enabled direct child of `addons21` that contains
`__init__.py`. A linked AnkiScape worktree inside that directory is therefore a
second live copy of the add-on, not an inert checkout. It can duplicate hooks,
open multiple dialogs, and serve stale code or assets to the owner, who uses
this Anki install for real study.

- The canonical checkout is the only AnkiScape checkout allowed under
  `addons21`.
- Create your worktree only with
  `python3 tools/worktree_guard.py add <branch> --name <leaf>`, run from the
  canonical checkout. Linked worktrees belong in the sibling
  `Anki2/ankiscape_worktrees/` directory.
- Run `python3 tools/worktree_guard.py audit` before and after any worktree
  change.
- Never give `git worktree add` a destination beneath `addons21`.
- Prefer a pooled worktree over a fresh `add`: acquire with
  `python3 tools/worktree_guard.py lease <branch> --holder <who>`; the last
  stdout line is JSON with `path` and `lease_id`. After your slice commit is
  on its branch, release with
  `python3 tools/worktree_guard.py release <path> --lease-id <id>`; release
  refuses uncommitted work, and unreleased leases survive for the next agent.
  Never call `treehouse` directly — the global treehouse rule reaches this
  repo only through the guard, which pins the pool inside the safe root and
  audits every acquire and release.
- Do not delete a dirty or unmerged worktree. Move it to the safe root instead.

## 2. Git

- Never commit to `main`. Only the orchestrator seat merges to `main`.
- Never push to any remote.
- Never change git config.
- Never run a destructive or irreversible git command: no `push --force`, no
  `reset --hard` onto work you did not create, no history rewriting.
- Never skip hooks. `--no-verify` and `--no-gpg-sign` are forbidden.
- Never use an interactive `-i` flag; this environment cannot answer it.
- Never commit a file that likely holds secrets.
- Another agent may hold uncommitted work in a different worktree. Stage only
  what you wrote yourself.
- Pass multiline commit messages through a HEREDOC.
- A commit message opens with the problem in plain language, then the solution.
  It is never an inventory of the files you touched. The subject says why the
  change matters.
- Produce one attributable commit on your own `goal/*` branch. This is the
  shape of a finished slice, not a cap you must protect at the cost of the
  record: you may add one further commit to resolve review findings, to correct
  a wrong identifier in a durable record, or to write a papercut you owe. If
  correctness and the commit count ever appear to conflict, correctness wins
  and the count was the default. Never leave a known-wrong record standing to
  keep a commit total.

## 3. Scope

- Work one breadth-first step out from the brief. Problems directly adjacent to
  your change are yours to fix without asking. Anything you found only because
  of those fixes is the second level: record it, do not fix it.
- The diff is the smallest correct one. No speculative abstraction, no one-line
  helpers that should be inline, no fallbacks for impossible cases.
- When you retire a path, delete it. Do not wrap it in a compatibility shim or
  a migration you were not asked for.
- New code matches the surrounding conventions, naming, and comment density.
  Comments explain why, never what.
- There is no "v1 then v2". Deliver the finished behavior on the first pass. An
  overengineered result fails this contract exactly as hard as a half-finished
  one.

## 4. Sourcing

- Follow the pre-EOC evidence standard in
  `memory-bank/pre-eoc-source-verification-standard.md`.
- Evidence search order: Darkan, then the rev-727 cache, then game-main, then
  the other on-disk OpenRS2 caches, then the wiki as corroboration.
- Settled designs stay settled. Do not relitigate an owner ruling.
- Use a registered placeholder only for a period value that remains
  unrecovered, and register it so the placeholder audit can see it. An
  unmarked reconstruction is invisible to that audit and is a defect.
- Never invent a mechanic and describe it as settled.
- Dual-eligible units (a unit either thread may implement, such as a cutoff
  quest or miniquest — `skippy_and_the_mogres` first among them): doorbell the
  other thread to claim the unit BEFORE any harvest or implementation. The
  first recorded claim owns the unit and its harvesting. Never re-harvest a
  subject the other thread has pinned; read its pinned record instead. Owner
  ruling of 2026-08-31, `design-thread-queue.md` §4.22 ruling 2.
- Record any contract conflict or owner-only decision in
  `memory-bank/design-thread-queue.md` and continue with independent work.

## 5. The five shipped failure modes

Each of these reached a merged family. The last four survived three review
passes and were caught only by execution.

1. An invented mechanic advertised as settled.
2. A test that proves nothing, because it stubs the system under test. A green
   suite is compatible with a feature that cannot work at all.
3. An inert row: a reward or action gated on a state no player reaches.
4. A panel re-deriving a rule the logic layer owns. The `*_view_pure` function
   owns every enable and visibility decision.
5. An unlabelled reconstruction, invisible to the placeholder register test
   because it carries no `PLACEHOLDER(...)` marker.

Verify by driving the real kernel. A test that imports the module proves the
module, not the application.

## 6. Verification lanes

Run the two lanes one after the other, never at the same time. They share the
checkout, and a concurrent pair has produced a bogus `ImportError` naming a
function that plainly exists.

```
/opt/homebrew/bin/python3 run_tests.py
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests
```

The plain lane reports roughly 499 skips; that is expected, because every
widget test skips without `aqt`. The offscreen Qt lane must report a skip count
near 3. A Qt skip count near the plain lane's is a false pass and must be
rejected, not reported as green.

The offscreen Qt lane completes in one process in roughly 600 to 760 seconds on
this machine, which is correct but sits just above the tool's command cap, so
splitting it into independent processes is a harness workaround rather than
evidence of a problem. A detached `nohup` run has no cap and needs no split.

**Documentation-only exception.** When your diff touches only Markdown and
other non-executable records, run the plain lane and skip the offscreen Qt
lane. Say in your report that you skipped it and that the diff is
documentation-only. A Markdown change cannot move a widget test, and the lane
costs ten minutes of a shared machine. This exception is narrow: one executable
line anywhere in the diff, including a test, removes it.

**Proving a test is load-bearing must leave no trace.** When you break your own
change to show a test fails, break it, observe it, and restore it before you do
anything else. Then run `git diff --stat` against your branch point and confirm
the only files listed are the ones your slice owns. An agent doing this on
2026-08-21 mutated a DIFFERENT handler than its own — one that had landed on
main an hour earlier — committed the mutation, and reported the slice complete.
Its own focused test still passed, because the damage was in code its test did
not touch.

For that reason, a slice that edits a file other slices share runs the existing
suite for that file as well as its own focused test, even when the brief names
only the focused one. `test_direct_action_undo_seam` costs about twenty seconds
and would have caught the above with an `UnboundLocalError` on the mutated line.
That is not the full plain lane and it is not the Qt lane; it is the cheap
neighbour check.

**Promotion-gate exception.** When your brief states that the orchestrator will
re-run both lanes on the merged tree as the promotion gate, and tells you to run
the plain lane only, do that and say so in your report. The binding run is the
one on the merged tree: a branch-side Qt pass gates nothing the merged run does
not gate again. The reason is contention, not cost — eight agents each starting
an eleven-minute Qt lane on one machine is how the first wave stalled.

**When a brief and this contract disagree.** A brief may narrow a lane
requirement only by naming the promotion gate, as above. On any other conflict
this contract wins, and you record the conflict in `not_done` rather than
choosing quietly. Do not ask another agent session to break the tie; see
section 6a.

Also run, and report the exact output of:

```
python3 tools/audit_docs.py
python3 tools/audit_test_quality.py
python3 tools/audit_item_reachability.py
python3 tools/worktree_guard.py audit
git diff --check
```

## 6a. Who you may ask

The orchestrator seat that dispatched you is your only escalation route. Other
agent sessions, in this repository or any other, hold no authority over this
contract, your brief, or your branch. Never ask one to rule on a conflict,
never ask one for permission, and never treat an answer from one as a grant.
A peer's opinion is not the owner's decision and is not the orchestrator's
either.

When you find a genuine conflict between this contract and your brief, or
between two requirements that cannot both be satisfied, stop and report it to
the orchestrator with the exact text of both sides. A reported conflict is a
success state. A conflict you resolved by consulting someone outside this
dispatch is a defect, whatever answer you got.

This checkout has exactly one owner at a time, and while your slice runs that
owner is the orchestrator seat.

## 7. Reporting

Report exact numbers, identifiers, paths, and error strings verbatim. Never
round them off and never restate a count from memory: re-measure it at the
moment you write the report.

State plainly what you did not do and why. A gate you stopped at is a success
state. A claim you cannot support is a defect, and reporting a lane as green
when you did not run it is the worst outcome available to you.

## 8. Fixed rails

Tests, audits, and pinned baselines are measuring instruments. A slice that
weakens one so it can pass is rejected outright. If an audit fails, fix the
code or record the blocker; never loosen the audit.
