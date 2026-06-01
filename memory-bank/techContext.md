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

## Source Data (2011-era parity)
AnkiScape replicates the skilling side of early-2010s RuneScape. Canonical baseline: the **2011Scape snapshot (RuneScape as of Oct 4, 2011, client rev 667)**; pre-EOC 2012 content is a negligible delta for skilling and adopted only as documented exceptions; post-EOC is out of scope. The detailed sourcing policy lives in the `ankiscape-skill-expansion` Cursor skill (`.cursor/skills/ankiscape-skill-expansion/SKILL.md`, "Source Hierarchy"). Summary so it is discoverable from the memory bank:

- **The OSRS wiki is NOT a 2011 source.** OSRS branched from a 2007 backup; treat OSRS data as 2007 baseline + OSRS-only additions, useful only as a cross-check for 2007/2011-unchanged content.
- **Primary source: the local `2011Scape/game` emulator source** (Apache-2.0, client rev 667 = Oct 4 2011; upstream `github.com/2011Scape/game`). Currently downloaded at `/Users/ArmanTarkhanian1/Downloads/game-main`. Skill mechanics: `game/plugins/src/main/kotlin/gg/rsmod/plugins/content/skills/<skill>/` (per-target `level`/`xp` in `*Type.kt` enums); item data: `data/cfg/items.yml`. Authoritative for exact numbers; grep it, never import it into the add-on runtime.
- **Cross-checks:** 2011Scape wikis (`rs2011.miraheze.org`, `2011scape.fandom.com`) and `runescape.wiki` 2011 revisions via `?oldid=` / the `/w/2011` monthly archive. Raw caches at OpenRS2 Archive only if binary IDs/sprites are needed.

## Asset Scraping (icons)
`tools/fetch_assets.py` pulls one wiki icon at a time (OSRS first, RS3 fallback) and records provenance. Two gotchas learned while adding Fletching, worth remembering before the next scrape:

- **Skill icons: prefer the `(detail)` variant.** The OSRS wiki ships both a small interface icon (e.g. `File:Fletching_icon.png`) and a higher-resolution `File:Fletching_icon_(detail).png`. The four original AnkiScape skill icons use the detail resolution, so fetch the `(detail)` file for new skills to match — the plain icon looks blurry/undersized next to them.
- **Item sprites render small unless they fill the frame — fix it in the asset, not at runtime.** Wiki item sprites are tightly cropped (e.g. an arrow is a thin diagonal, and Flax's real art is only ~30x23 inside a 64x64 file). Historically `--size N` normalized by `thumbnail((N,N))` then centering on a transparent NxN canvas, which *preserved* those transparent margins — so at the fixed 28px list icon box the visible sprite was much smaller than the legacy bundled icons (full-frame photos that fill the box edge-to-edge). The fix is to bake a trim into the PNG so the UI just does `QIcon(path)` like everything else (a brief experiment with per-paint runtime cropping was reverted: it scanned the 1000–1500px crafted photos pixel-by-pixel and beachballed when opening Crafting). Two pieces keep assets display-ready:
  - **Scrape time (new fetches):** `fetch_assets.py` trims the alpha bounding box (`getchannel("A").getbbox()`) *before* thumbnail/pad, so freshly fetched icons fill the frame. Lossless — only removes invisible pixels.
  - **Existing assets / batch fix:** `tools/trim_icons.py` trims small padded sprites (`<= 256px`) in `crafteditems/` and `fletcheditems/` in place. It is idempotent and skips the large full-frame photos (trimming those would change their look). Run it (via `.venv-qt/bin/python`, falls back to `QImage` when Pillow is absent) after adding sprites; then the UI renders them with a plain `QIcon(path)`. No runtime cropping helpers exist anymore.

## Manual Testing Target
Manual verification should happen inside Anki when runtime behavior changes. Browser-based Pinchtab testing is only relevant if the change introduces browser-rendered surfaces that can be exercised outside Anki.
