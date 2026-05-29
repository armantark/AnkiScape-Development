# Tests for AnkiScape

- All tests live under `tests/`.
- They use Python's built-in `unittest` framework (no pytest dependency).

## How to run

Use the helper at repo root:

```
python3 run_tests.py
```

It discovers and runs all `tests/test_*.py` files. The script adds the repo root to `PYTHONPATH` so tests can import modules like `logic_pure` directly.

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

These tests aim to catch regressions in gating, migrations, and core behavior without requiring a full Anki GUI runtime.
