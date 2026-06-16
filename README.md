# AnkiScape (Development)

AnkiScape adds a lightweight, game-like experience layer to Anki:
- Review HUD feedback with the active skill or activity, level, and progress.
- Floating XP or material toasts, achievement popups, and level-up popups.
- A Skills hub for Mining, Woodcutting, Smithing, Crafting, and Fletching.
- Utility / Activities for no-XP material prep such as soft clay, wool, flax, bird nests, and feathers.
- Bank, Stats, Equipment, Achievements, and Settings tabs in the floating widget.
- Undo-aware review rewards with an `Actions per review` pacing control.

This development checkout tracks the local fork's current playable loop: study cards, run a selected skill or Utility activity, grow the inventory, and inspect progress from the widget.

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
- Gameplay
  - Actions per review: runs 1-10 game action ticks per successful review. XP, items, rolls, and material use scale because more actions run.
- Notifications
  - Enable floating XP: toggles the small XP toast when XP is earned.
  - Enable achievements and level up pop ups: toggles achievement/level-up dialogs.
- Floating widget
  - Enable widget: show/hide the small floating button.
  - Widget Position: bottom left/bottom right.
- Developer Mode
  - Enable developer mode: turns on debug logs and shows developer actions such as clearing logs and running unit tests.

### Defaults
- Enable experience HUD: true
- Actions per review: 1x
- Enable floating XP: true
- Enable achievements and level up pop ups: true
- Enable widget: true
- Widget Position: "right" (bottom right)
- Enable developer mode: false

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

For the Qt behavior suite, run the tests through the checked-in Qt virtual environment:

```
QT_QPA_PLATFORM=offscreen .venv-qt/bin/python -m unittest discover tests
```

- Confirms widget, Skills hub, Bank, Stats, Equipment, Settings, and Utility row behavior in an offscreen Qt runtime.
- Keeps UI contracts covered without requiring a visible Anki window.

### Debug logging
Set an environment variable before launching Anki or running tests to enable debug logs:
- macOS/Linux (zsh): `export ANKISCAPE_DEBUG=1`
- Windows (PowerShell): `$env:ANKISCAPE_DEBUG = '1'`

Logs are written next to the package as `ankiscape_debug.log` and rotate automatically. They’re git-ignored.

## Packaging notes
When preparing a release zip for Anki users, exclude development artifacts:
- `.venv/`, `.pytest_cache/`, `.vscode/`, `__pycache__/`, test files, and log files.

The add-on will work out-of-the-box with the defaults above, and all new settings are backward-compatible via the migration step.
