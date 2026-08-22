# Another writer committed to main — 2026-08-21

Recorded by the orchestration seat under the standing rule: on an
another-writer collision on main, stop and record it, and attempt no repair.
Nothing here has been reverted or rewritten.

## What happened

At 19:37:19 PDT a second Claude session committed directly to `main`:

```
87bf57a2  Independent audit of the ox-alpha window finds the loop sound and one green gate unclaimed
author=armantark <chuck67322@berkeley.edu>   committer=armantark
 memory-bank/oxalpha-audit-2026-08-21.md | 153 ++++++++++++++++++++++++++++++++
```

The session identified itself over the cross-session socket
`uds:/tmp/cc-socks/74560.sock` as `ankiscape-fork-80`, "Independent Fable audit
seat, read-only", running in bypass mode. It described itself as read-only in
the same message in which it reported committing to `main`. That contradiction
is the reason this record exists; a seat that believes it is read-only and is
not cannot be relied on to stay out of the way.

The commit itself is benign as far as this seat can measure. It adds one new
Markdown file and changes nothing else. `main` still passes the documentation
audit afterwards — `Audited 586 Markdown and 437 HTML files. Documentation audit
passed.` — and no tracked file this seat holds was touched.

## Why it still matters

Promotion to `main` in this project is gated: a slice lands only after both
verification lanes and the repository checks pass on the MERGED tree, because
the owner runs this Anki install live. Commit `87bf57a2` did not pass through
that gate. It is documentation-only, which the standing contract exempts from
the offscreen Qt lane, so the practical risk is very low — but the property
being protected is that `main` never advances except through the gate, and that
property is now broken for one commit.

The second effect is mechanical. Every promotion gate measures a specific merged
tree, and any commit landing on `main` invalidates every gate then in flight.
This seat invalidated two of its own gates that way earlier today (recorded in
`papercuts.md`). A second writer committing to `main` on its own schedule makes
that failure mode unavoidable rather than avoidable.

## State at the moment of the collision

`goal/undo-wave3` work is accepted and fully gated but NOT landed:

- promotion tree `promote-undo4/2026-08-21` at `9e53aa83`
- plain lane `Ran 4271 tests in 231.120s` / `OK (skipped=502)`
- offscreen Qt lane `Ran 4271 tests in 325.466s` / `OK (skipped=3)`
- `1598 actions; 2369 reachable items; 38 orphan inputs; 37 blocked actions`
- documentation audit passed; `4236 tests across 207 files`, hard issues 0;
  worktree layout safe; `git diff --check` clean

That gate ran against `778f5e88` and therefore does not include `87bf57a2`.

Holding it turned out to be right for an unrelated reason: `tests/test_undo_seam_circus.py`
carries only two tests where every sibling carries three, and it cannot detect a
real defect. This seat measured it directly — changing `__init__.py:3225` from
`return updated, ok` to `return updated, True` leaves the focused suite green at
`Ran 2 tests ... OK` and the neighbour suite green at `Ran 48 tests ... OK`.
That mutant makes the seam commit a change the pure function refused, while the
player is still told the action failed, so refused state is written silently. A
refusal-path test is in progress on that branch.

## What this seat is doing

- Not landing anything on `main` until the owner rules on whether a second
  writer is sanctioned there.
- Not reverting, amending or otherwise repairing `87bf57a2`.
- Continuing work that does not touch `main`: branch-level fixes, authoring and
  review.
- Treating the other seat's findings as data to verify, not as direction. Both
  claims it made were checked here against the tree and the logs before any
  action was taken, and both held.

## The other seat's account of why it committed

Added after the fact. This is that seat's claim, relayed over the same socket,
and this seat cannot verify it. A peer's report of an owner instruction is not
the owner's instruction, so nothing below is treated as authority — it is
recorded because provenance matters when the owner rules.

It states the commit was owner-instructed and one-shot, quoting its dispatch
brief verbatim:

> Write your findings to memory-bank/oxalpha-audit-2026-08-21.md and commit ONLY
> that file (path-scoped: git add that file, then `git commit -- <that file>`)

Its session branch at dispatch was `main`, so that instruction produced
`87bf57a2`. It claims no authority beyond that single deliverable, says its
audit is complete and that no further writes of any kind will come from it, and
accepts that describing itself as read-only without flagging the instructed
exception was imprecise. It agrees a second writer on a gated `main` is unsafe
as a pattern, and suggests a branch this seat gates through would satisfy the
same brief.

If that account is accurate, the collision window is closed and the risk is
retrospective rather than ongoing. This seat still holds promotion, for one
reason only: it told the owner it would, and a peer cannot release a commitment
made to the owner. The hold currently costs nothing, because the wave-three
tree needs a fresh gate anyway for the circus refusal test.

What the owner may want to settle beyond the immediate question: how audit
deliverables from a dispatched seat should land in future, given that "commit
only this file" plus a session sitting on `main` is a gate bypass by
construction, whatever the intent.

## The owner's ruling — 2026-08-21, ruled directly by the owner

Allowed. The seat was Fable, dispatched by the owner to run an independent audit
on this orchestration seat and on the Ox Alpha work. Its commit `87bf57a2`
stands, and this seat stops treating it as a collision.

Consequences recorded so a later session does not re-open this:

- A dispatched audit seat may commit its own findings file to `main`. That is
  not an another-writer collision and must not stop promotion.
- The stop-and-record rule still applies to any writer this seat cannot account
  for.
- The mechanical caution stands on its own merits and is not overruled: any
  commit to `main` invalidates every promotion gate then in flight, whoever
  makes it. This seat invalidated two of its own that way earlier today. The
  remedy is sequencing, not permission — gate one slice at a time, and re-absorb
  `main` before landing.

The audit's own findings were verified here before use and both held: the circus
refusal test could not detect a real defect, and the wave-three gate had gone
green unclaimed. See the entries above.
