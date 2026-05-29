# Tech Context

## Runtime
- Python Anki add-on running inside Anki/AQT.
- Qt UI is accessed through `aqt.qt`.
- Persistent data is stored in Anki collection config via `mw.col.get_config` and `mw.col.set_config`.

## Development Setup
- Source lives directly in an Anki add-ons directory.
- This working copy should live in `addons21/ankiscape_fork`, not the AnkiWeb-managed numeric folder `addons21/1808450369`.
- Future AnkiWeb updates may recreate or update `addons21/1808450369`; treat that folder as upstream and manually diff/merge changes into `ankiscape_fork`.
- The local working copy is a solo-project git repository on `main`.
- Tests are run with `python3 run_tests.py`.
- Tests use Python's built-in `unittest`, not pytest.
- `run_tests.py` adds the repo root to `PYTHONPATH` so pure modules can be imported directly.

## Testing Coverage
Existing tests cover:
- core game logic and level/XP math
- probability helpers
- storage migration/default data shape
- settings toggles and UI gating
- hook registration dry-runs
- JavaScript injection contracts
- a no-Qt integration smoke test for package loading and hook flow

## Debugging
- Debug logging is centralized in `debug.py`.
- Logging is disabled by default.
- `ANKISCAPE_DEBUG=1` enables logs for local debugging.
- Logs are written near the package as `ankiscape_debug.log` and rotate automatically.

## Constraints
- Code must remain importable outside Anki/Qt for tests.
- Anki runtime imports should be guarded where possible.
- UI behavior should be optional and resilient; add-on failures should not interrupt studying.
- Storage migrations must be idempotent.
- New Python code should be fully typed where practical, especially new public helpers and data models.

## Package Management
There is no separate package manager requirement in the current add-on. If Python dependencies become necessary, prefer `uv` unless the project adopts another tool explicitly.

Developer-only scripts can use `uv run` inline script metadata when optional tooling dependencies should not become add-on runtime dependencies. `tools/fetch_assets.py` uses this pattern for Pillow-based PNG normalization.

## Manual Testing Target
Manual verification should happen inside Anki when runtime behavior changes. Browser-based Pinchtab testing is only relevant if the change introduces browser-rendered surfaces that can be exercised outside Anki.
