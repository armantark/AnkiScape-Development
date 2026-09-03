# The dispatcher seam is a restructure, not a slice — 2026-09-02 21:12 PDT

Ruling 53 rejected the root-dispatchers split because its eleven part modules
are code containers: their functions reference the root's mutable state as free
variables and only work through copies rebound against the root's `globals()`.
The ruling scoped the repair to "extract the shared mutable state into a module
both sides import", as one narrow slice, with a stop-and-report if it could not
be done that way.

It cannot. The slice stopped at that gate and measured why.

## What the measurement found

```
167  dispatcher function bodies reference shared root state
109  of those reference rebindable scalar state, so they need real body changes
 56  test files make 911 direct assignments or deletions against root attributes
```

The obstacle is not the container. A module holding `player_data` works, but
importing a scalar by value does not: a later assignment stays module-local and
every other reader keeps the stale value. So the seam has to be an object whose
fields are read through it, `state.player_data`, `state.current_skill`,
`state.exp_awarded`, and every one of the 109 bodies changes to reach through
it. Under ruling 47 each of those is a real change, so each carries a behaviour
test, on the review answer path.

A compatibility proxy that intercepted assignment to the root module would keep
the call sites unchanged, and it is the wrong answer: it recreates the hidden
coupling ruling 53 rejected, one layer further down.

The 911 test assignments are the second half of the cost. Those tests set root
state directly to arrange their cases, and each becomes a change too.

The seam slice verified its own claims and left no executable change: its branch
holds eight lines of papercuts, the root Qt surface digest is unchanged at
`2393cf594a63dfc240437408137c1732a4cd317e0ade7c3efd10e18889a5a8ca`, and the
complete 342-name root dump is byte-identical. My own spot check found 32 test
files assigning the three named attributes, consistent with its larger figure
across all root state.

## The choice, which is the owner's

The dispatchers cannot move until this is settled, so `__init__.py` stays at
6,254 lines and the preserved split stays parked at
`refs/preserved/init-dispatchers-2026-09-02`.

1. **Do the restructure.** Its own programme: a state object, 109 dispatcher
   bodies changed with behaviour tests, and 56 test files migrated. It removes
   the coupling honestly and makes the eleven modules real. It is large, and it
   is on the most load-bearing path in the add-on.
2. **Leave `__init__.py` unsplit.** Accept the 6,254-line root as permanent
   debt, and accept that anything needing to grow it stays blocked, which is
   what motivated the split in the first place.
3. **Reconsider the rebinding.** Ruling 53 rejected it on principle rather than
   on a measured failure: the rebound dispatchers work, the lanes pass, and the
   defect is that a part imported directly raises `NameError`. A narrower
   ruling could permit the mechanism where each part documents it and a test
   proves direct import fails loudly rather than silently.

My lean is option 3 first and option 1 as its own programme later, because the
split's value is the file-size unblock, which option 3 delivers now, and the
restructure's value is design cleanliness, which does not expire. I hold no
authority to choose, and the design seat is off.
