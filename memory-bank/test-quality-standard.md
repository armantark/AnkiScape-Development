# Test Quality Standard

## Purpose

The suite is a regression instrument, not a test-count target. Prefer one test
with named `subTest` scenarios when setup, exercised behavior, and assertions
are the same. Keep separate methods when they protect different branches,
fixtures, layers, or expected-failure contracts.

## Mechanical Gate

Run:

```bash
/opt/homebrew/bin/python3 tools/audit_test_quality.py
```

`tools/audit_test_quality.py` fails on:

- module-level `test_*` functions that `unittest` discovery ignores;
- `test_*` methods outside a `unittest.TestCase` class;
- tests with no assertion or assertion-helper call;
- literal membership checks against text read directly from a file, because
  source spelling does not prove executable behavior;
- identical method bodies inside the same test class.

The audit reports constant-normalized structural clones for human review but
does not fail them automatically. Similar test bodies can still be legitimate
when constants select different production branches, fixtures change the
system under test, or one method is an intentional `expectedFailure` contract.

## Verification

Use the Homebrew Python for the pure suite because the system Python is too old
for the repository's type syntax:

```bash
/opt/homebrew/bin/python3 run_tests.py
```

Use the shared Qt virtual environment for real offscreen discovery:

```bash
QT_QPA_PLATFORM=offscreen \
  '/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.venv-qt/bin/python' \
  -m unittest discover -s tests
```

Report executed methods, ordinary passes, skips, and expected failures
separately. Never describe `Ran N tests` as `N passing` when the total includes
skips or expected failures.

## Manual Playtesting

The owner plays the real save from level 1 at normal review pace and does not
create development saves for late-game checks. On 2026-07-11, the Construction
12-step smoke test was rejected as unreachable: "I currently would have level 1
so there's no way for me to reliably test that".

Manual test instructions must lead with low-level checks such as rung-zero
purchases, level-1 targets, and visible UI presence or gating. Cover level 60+
and other late-game behavior with pure and offscreen Qt tests instead of
assigning it as owner-run manual verification.
