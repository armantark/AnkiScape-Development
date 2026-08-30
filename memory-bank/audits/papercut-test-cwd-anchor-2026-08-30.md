# Test helper cwd anchor — 2026-08-30

## Cause

`run_tests.py` derived its checkout root and inserted that path into `sys.path`,
but it never changed the process working directory. Invoking the helper by an
absolute path from another directory therefore left `os.getcwd()` and every
relative path used by a discovered test anchored to the caller's directory.

## Scope

- `run_tests.py` now changes the process working directory to the checkout that
  contains the helper before the optional `aqt` import and before unittest
  discovery.
- `tests/test_papercut_tools.py` contains a subprocess regression that copies
  `run_tests.py` into a temporary `Anki2/ankiscape_worktrees/cwd-fixture`
  checkout, invokes that copy by absolute path from an unrelated sibling
  directory, and runs a discovered probe that requires the process cwd to equal
  the fixture checkout root.
- `README-tests.md` records this helper cwd contract.
- No user interface, `tools/run_logged.py`, or
  `tools/audit_item_reachability.py` behavior is in scope.

## Pending MacBook verification

No tests were run on the Mac Studio, as required by the guarded worktree task.
The focused regression remains pending on the MacBook:

```
/opt/homebrew/bin/python3 run_tests.py PapercutToolTests.test_runner_anchors_process_cwd_to_its_checkout_root --verbosity 2
```

After that focused check passes, the ordinary non-Qt helper lane remains pending
for the same MacBook checkout:

```
/opt/homebrew/bin/python3 run_tests.py
```
