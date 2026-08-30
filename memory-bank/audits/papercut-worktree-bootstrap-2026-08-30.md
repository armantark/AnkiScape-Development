# Worktree Bootstrap Papercut — 2026-08-30

## Exact cause

`unsafe_registered_worktrees()` classified every non-canonical registered
worktree below `addons21` as unsafe. That rule also classified disposable test
harness worktrees nested below `canonical.resolve()` as live duplicate add-ons,
even though Anki only imports direct `addons21` children. Separately,
`tools/worktree_guard.py add` created a checkout without provisioning its ignored
`.venv-qt` path, so the documented `.venv-qt/bin/python` command was unavailable
inside a guard-created worktree.

## Scope

The guard now exempts only registered descendants of `canonical.resolve()` and
continues to reject a direct sibling of the canonical checkout and a registered
path nested below any other add-on. Before `git worktree add`, it requires
`canonical/.venv-qt/bin/python`. After Git creates the destination, it creates
`destination/.venv-qt` as an absolute directory symlink to
`canonical/.venv-qt`. Focused regression tests cover those boundaries, the
preflight stop, and the absolute link. `README.md` and `README-tests.md` only
document the ignored guard-provisioned local link; the existing
`.venv-qt/bin/python` command is unchanged.

## Pending MacBook verification

No tests ran on this Mac Studio, as required by the guarded worktree assignment.
On the MacBook, run:

```
.venv-qt/bin/python -m unittest tests.test_worktree_guard
```

Then use a disposable repository fixture to confirm that a missing canonical
interpreter exits before `git worktree add`, and that a successful guarded add
creates an absolute `.venv-qt` symlink before the final layout audit.
