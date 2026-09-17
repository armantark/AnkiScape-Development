# Goal blocked — 2026-09-16 20:10 PDT

## What is blocked

Promotion of `goal/bar-crawl-2026-09-16` to canonical main, and promotion of
any other slice, because canonical main does not pass its own gate.

## What is blocked by what

`tests/test_promotion_gate.py::test_promotion_docs_explain_tree_owned_reachability_pins`
fails on canonical main `038157f6` with a clean working tree:

```
AssertionError: 'supersedes' not found in <memory-bank/systemPatterns.md>
```

That test arrived in the owner's commits `d450deba` ("docs: make progress.md the
only dated log so the memory bank stops drifting", 2026-09-16 19:18) and
`038157f6` ("docs: keep systemPatterns.md to invariants so rollout history stops
going stale", 2026-09-16 19:19). The same pair rewrote
`memory-bank/systemPatterns.md`, which is now 887 lines and contains neither the
word `supersedes` nor the date string `2026-08-22 05:52`.

The test requires four things:
1. a `systemPatterns.md` paragraph mentioning reachability that contains both
   `pin` and `gated tree`;
2. the literal word `supersedes` in `systemPatterns.md`;
3. the literal date `2026-08-22 05:52` in `systemPatterns.md`;
4. a `papercuts.md` paragraph containing `superseded`, `pin` and `gated tree`.

## What I tried

The Barcrawl slice itself is finished and green. Both lanes passed on the branch
before the merge, on the remote MacBook host: plain `Ran 5650 tests in 558.534s`,
`OK (skipped=1364)`; Qt `Ran 5650 tests in 1081.671s`, `OK (skipped=5)`.

Main moved from `8283ad9d` to `038157f6` during the slice. I merged main into the
branch at `fdb1c41c`; `git merge-tree` reported no conflicts and the merge was
clean.

The eight-check gate on the merged tree then failed in `1701s` with exactly one
failing test, the one above, in both lanes: `Ran 5651 tests in 1091.093s`,
`FAILED (failures=1, skipped=5)`.

I then ran that single test against the canonical checkout at `038157f6` with a
clean tree. It fails there identically. The merged branch's `systemPatterns.md`
is byte-identical to main's; `git diff main -- memory-bank/systemPatterns.md`
returns no output. The slice is therefore not the cause.

## The single thing that would unblock it

Your decision on `memory-bank/systemPatterns.md`. Either add the passage the new
test requires, naming the superseded `2026-08-22 05:52` papercut and stating that
reachability pins come from the gated tree, or amend the test to match the file
you intended to write.

I did not edit `systemPatterns.md` or the test. You rewrote that file
deliberately minutes earlier, and inventing wording for a rule you had just
authored would be a repair made on a guess.

The slice waits on branch `goal/bar-crawl-2026-09-16` at `fdb1c41c`, nine commits
ahead of main, zero behind, fast-forwardable. Delete this file when main is green
and the landing will proceed.
