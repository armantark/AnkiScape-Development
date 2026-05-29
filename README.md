# AnkiScape (Development)

AnkiScape adds a lightweight, game-like experience layer to Anki:
- Experience HUD during review (skill icon + level + progress bar).
- Floating XP toasts when you earn XP.
- Achievement and level-up popups.
- A small floating widget you can position on screen.

This branch contains the in-progress development version with a refined Settings experience and improved tests.

## Install (from source)

Pick one of the following:
- Zip install:
  1) Create a zip of this folder (excluding `.venv/`, `tests/`, `.pytest_cache/`, `.vscode/`, and log files).
  2) In Anki, Tools → Add-ons → Install from file, select the zip.
- Dev checkout (advanced):
  - Place/clone this folder into Anki’s add-ons directory (e.g. `~/Library/Application Support/Anki2/addons21/ankiscape`). Restart Anki.

Note: Paths differ by OS/profile; see Anki docs for the add-ons directory location.

## Settings overview

All user-visible options are in Anki: Tools → Add-ons → AnkiScape → Config/Settings.

- Experience
  - Enable experience HUD: toggles the entire in-review HUD (icon + level + progress).
- Notifications
  - Enable floating XP: toggles the small XP toast when XP is earned.
  - Enable achievements and level up pop ups: toggles achievement/level-up dialogs.
- Floating widget
  - Enable widget: show/hide the small floating button.
  - Widget Position: left/right.

### Defaults
- Enable experience HUD: true
- Enable floating XP: true
- Enable achievements and level up pop ups: true
- Enable widget: true
- Widget Position: "right"

### Migration of legacy settings
If you previously used a separate “progress bar” toggle, it’s automatically migrated on profile load:
- `ankiscape_hud_progress_enabled` → `ankiscape_review_hud_enabled` (only if the new key wasn’t set).
This migration is idempotent and covered by tests.

## Development

### Run tests
Use the helper script at the repo root:

```
python3 run_tests.py
```

- Uses Python’s built-in `unittest`.
- Discovers `tests/test_*.py`.
- Includes an integration smoke test that loads the add-on without Qt and verifies hook flow + settings gating.

### Debug logging
Set an environment variable before launching Anki or running tests to enable debug logs:
- macOS/Linux (zsh): `export ANKISCAPE_DEBUG=1`
- Windows (PowerShell): `$env:ANKISCAPE_DEBUG = '1'`

Logs are written next to the package as `ankiscape_debug.log` and rotate automatically. They’re git-ignored.

## Packaging notes
When preparing a release zip for Anki users, exclude development artifacts:
- `.venv/`, `.pytest_cache/`, `.vscode/`, `__pycache__/`, test files, and log files.

The add-on will work out-of-the-box with the defaults above, and all new settings are backward-compatible via the migration step.
