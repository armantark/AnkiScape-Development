# Tests for AnkiScape

- All tests live under `tests/`.
- They use Python's built-in `unittest` framework (no pytest dependency).
- Discovery recurses into subdirectories that carry an `__init__.py`
  (for example `tests/combat/`).

## How to run

Use the helper at repo root:

```
/opt/homebrew/bin/python3 run_tests.py
```

It discovers and runs all `tests/test_*.py` files. The script adds the repo root to `PYTHONPATH` so tests can import modules like `logic_pure` directly. Before importing optional Anki/Qt modules or discovering tests, the helper also anchors the process working directory to the checkout that contains `run_tests.py`.

Every test ID starts with `tests.`, and the helper refuses to run when one ID is
discovered twice. A selector such as `test_combat`, `tests.test_combat` or
`promotion.test_gate_lock_claim` matches whole dotted names, so `test_combat`
does not also select `test_combat_logic`; a selector that is no whole name
falls back to a case-insensitive fragment of the ID. Preview a selection with
`run_tests.py --list <selector>`.

Run the full real Qt suite separately through the checked-in environment:

```
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python run_tests.py
```

Worktrees created by `tools/worktree_guard.py add` receive `.venv-qt` as an
ignored local link to the canonical checkout's Qt environment, so this command
stays unchanged in each guard-provisioned worktree.

The non-Qt runner deliberately skips environment-dependent Qt cases; the
offscreen command is the release gate for those surfaces.

Run the two lanes **one after the other, never at the same time**. They share the
checkout, and a concurrent pair produced one bogus failure on 2026-07-28: an
integration test that reloads the add-on as a fresh package raised
`ImportError: cannot import name ... from ...ui.ui` for a function that plainly
exists, which is the shape of a partially loaded module. Both lanes passed
immediately afterwards when run sequentially. If you see an ImportError naming a
function you can grep at column zero, check whether the other lane was running.

`python3 tools/audit_item_reachability.py --check` exits 1 only when the report
differs from the seven counts pinned in `tests/test_item_reachability_audit.py`,
so it is safe in `&&` chains. The report modes (no flag, `--json`, `--summary`,
`--rank-roots N`) exit 0 whenever the report builds, even with orphan inputs.

## Debug logging during development

This add-on now uses a centralized, rotating debug log stored next to the package as `ankiscape_debug.log`.
Logging is disabled by default. To enable it temporarily while debugging, set an environment variable before launching Anki or running tests:

- macOS/Linux (zsh): `export ANKISCAPE_DEBUG=1`
- Windows (PowerShell): `$env:ANKISCAPE_DEBUG = '1'`

The logger rotates at ~1 MB with up to 3 backups (`ankiscape_debug.log.1`, etc.).
The log files are git-ignored and should not be shipped in releases.

## What is covered

- Core game logic, level/exp math, and probability helpers
- Storage migration and default data shape guarantees
- Settings helpers and toggles (Experience HUD, floating XP, popups)
- UI progress calculations and boundary conditions
- Hook registration planning (dry-run)
- A no-Qt integration smoke test that dynamically loads the add-on as a package and validates:
  - HUD ensure/update/hide are gated by the Experience HUD toggle
  - Floating XP toasts respect the Floating XP toggle
  - Overview refresh hides the HUD
- Registry, reachability, source-data, storage, undo, and direct-action contracts
- Offscreen Qt behavior for the Skills hub, Bank, Equipment, shops, quests, and activities
- Documentation and test-quality audits

These tests aim to catch regressions in gating, migrations, and core behavior without requiring a full Anki GUI runtime.
