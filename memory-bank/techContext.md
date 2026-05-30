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

### Fast Qt UI loop (no Anki restart)
- A dedicated `uv` venv at `.venv-qt` (git-ignored) has `aqt` installed, which bundles PyQt6.
- This lets us build the *real* dialogs headlessly instead of iterating by restarting Anki.
- Pattern (see `tests/test_main_menu_widget.py`):
  - `QT_QPA_PLATFORM=offscreen` so Qt runs without a display.
  - Monkeypatch `QDialog.exec` to capture the live dialog and return immediately (otherwise `exec()` blocks).
  - Monkeypatch `ui.get_config_bool` to control flags like developer mode.
  - Drive the actual widgets (`setCurrentRow`, `.click()`, `processEvents()`) and assert on the resulting widget tree (panel header text, etc.).
- Run it with:
  - `source .venv-qt/bin/activate && QT_QPA_PLATFORM=offscreen python tests/test_main_menu_widget.py`
- These tests are skipped automatically under the plain `run_tests.py` env (no `aqt`), so the core suite stays Qt-free.
- This loop caught the Skills-hub `_select_skill` closure-shadow bug in under a second; prefer it over manual Anki restarts for UI-behavior regressions.

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
- `ANKISCAPE_DEBUG=1` enables logs for local debugging (Developer Mode also enables it in-app).
- Logs are written near the package as `ankiscape_debug.log` and rotate automatically.
- The Skills hub emits `hub.*` trace lines (`hub.select_category`, `hub.skill_row`, `hub.select_skill`, `hub.render_panel`). A fired `hub.skill_row` with no following `hub.select_skill`/`hub.render_panel` means a click was misrouted rather than a Qt/signal failure — that gap is exactly how the closure-shadow bug was found.

## Constraints
- Code must remain importable outside Anki/Qt for tests.
- Anki runtime imports should be guarded where possible.
- UI behavior should be optional and resilient; add-on failures should not interrupt studying.
- Storage migrations must be idempotent.
- New Python code should be fully typed where practical, especially new public helpers and data models.

## Package Management
There is no separate package manager requirement in the current add-on. If Python dependencies become necessary, prefer `uv` unless the project adopts another tool explicitly.

Developer-only scripts can use `uv run` inline script metadata when optional tooling dependencies should not become add-on runtime dependencies. `tools/fetch_assets.py` uses this pattern for Pillow-based PNG normalization.

## Asset Scraping (icons)
`tools/fetch_assets.py` pulls one wiki icon at a time (OSRS first, RS3 fallback) and records provenance. Two gotchas learned while adding Fletching, worth remembering before the next scrape:

- **Skill icons: prefer the `(detail)` variant.** The OSRS wiki ships both a small interface icon (e.g. `File:Fletching_icon.png`) and a higher-resolution `File:Fletching_icon_(detail).png`. The four original AnkiScape skill icons use the detail resolution, so fetch the `(detail)` file for new skills to match — the plain icon looks blurry/undersized next to them.
- **Item sprites render small unless they fill the frame.** Wiki item sprites are tightly cropped (e.g. an arrow is a thin diagonal, and Flax's real art is only ~30x23 inside a 64x64 file). Historically `--size N` normalized by `thumbnail((N,N))` then centering on a transparent NxN canvas, which *preserved* those transparent margins — so at the fixed 28px list icon box the visible sprite was much smaller than the legacy bundled icons (full-frame photos with no alpha that fill the box edge-to-edge). This is now defended on two layers:
  - **Scrape time (durable):** `fetch_assets.py` trims the alpha bounding box (`getchannel("A").getbbox()`) *before* thumbnail/pad, so freshly fetched icons fill the frame. This is lossless — it only removes invisible pixels.
  - **Runtime (safety net for older assets):** `ui.scaled_item_icon()` routes anything under the scraped-sprite folders (`crafteditems/`, `fletcheditems/`) through `ui.icon_filled_to_box()`, which crops to the opaque box before Qt downscales. Legacy photo icons live in other folders and are passed straight through as plain `QIcon` to avoid scanning large full-frame images pixel-by-pixel. Use `scaled_item_icon()` for any item-icon list/bank cell rather than `QIcon(path)` directly, so already-on-disk padded assets (the existing Flax/Wool/Soft clay sprites were fetched before the trim step landed) still render correctly.

## Manual Testing Target
Manual verification should happen inside Anki when runtime behavior changes. Browser-based Pinchtab testing is only relevant if the change introduces browser-rendered surfaces that can be exercised outside Anki.
