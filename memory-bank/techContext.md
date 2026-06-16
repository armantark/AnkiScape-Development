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

Current Woodcutting backend parity data lives in `woodcutting_data.py`, with a detailed audit at `memory-bank/source-audits/woodcutting-2011scape-2026-06-01.md`. It stores raw 2011Scape low/high chop chances and hatchet ratios, then lets `logic_pure.py` adapt them to Anki review cadence.

Current Mining backend parity data lives in `mining_data.py`, with a detailed audit at `memory-bank/source-audits/mining-2011scape-2026-06-01.md`. It stores raw 2011Scape low/high Mining chances, respawn-time data, pickaxe roll cadence, scoped simple historical targets, gem-drop tables, tradability, and Mining bonus metadata consumed through worn equipment. Storage config version 8 migrates old display-name Mining targets to stable IDs; storage config version 10 moves passive bonus ownership into `player_data["equipment"]`.


Current Crafting backend parity data lives in `crafting_data.py`, with a detailed audit at `memory-bank/source-audits/crafting-2011scape-2026-06-03.md`. It stores stable recipe IDs, source family/station metadata, real requirements/outputs, corrected 2011Scape XP values, and notes for input-starved content whose acquisition loop is not built yet. Storage config version 11 migrates legacy display-name `current_craft` values to stable IDs.

Current Smithing backend parity data lives in `smithing_data.py`, with a detailed audit at `memory-bank/source-audits/smithing-2011scape-2026-06-01.md`. `tools/generate_smithing_data.py` parses the local 2011Scape Smithing plugin and item metadata into a checked-in Python module with 9 smelt recipes and 157 forge recipes. Storage config version 9 migrates old `current_bar` saves to stable `current_smith` recipe IDs and normalizes legacy `Adamantite bar`/`Runite bar` inventory keys to source item names.

Current equipment backend data lives in generated `equipment_data.py`. `tools/generate_equipment_data.py` combines checked-in `smithing_data.py`, local 2011Scape `data/cfg/items.yml` equipment blocks, and `mining_data.py` Mining bonus items. Storage config version 10 adds flat `equipment` state, removes `owned_equipment`, and scaffolds planned combat level/exp defaults so equipment gates are real `*_level` checks before combat training exists.

Current feather source data lives in `constants.UTILITY_ACTIVITY_DATA` as the
no-XP `scavenge_chicken_feathers` activity, with the audit at
`memory-bank/source-audits/feather-utility-2026-06-15.md`. It is deliberately a
temporary Utility bridge from local 2011Scape chicken feather drops, not the
final Combat drop or GE route.

## Asset Scraping (icons)
`tools/fetch_assets.py` pulls one wiki icon at a time (OSRS first, RS3 fallback) and records provenance. Two gotchas learned while adding Fletching, worth remembering before the next scrape:

- **Skill icons: prefer the `(detail)` variant.** The OSRS wiki ships both a small interface icon (e.g. `File:Fletching_icon.png`) and a higher-resolution `File:Fletching_icon_(detail).png`. The four original AnkiScape skill icons use the detail resolution, so fetch the `(detail)` file for new skills to match — the plain icon looks blurry/undersized next to them.
- **Item sprites render small unless they fill the frame — fix it in the asset, not at runtime.** Wiki item sprites are tightly cropped (e.g. an arrow is a thin diagonal, and Flax's real art is only ~30x23 inside a 64x64 file). Historically `--size N` normalized by `thumbnail((N,N))` then centering on a transparent NxN canvas, which *preserved* those transparent margins — so at the fixed 28px list icon box the visible sprite was much smaller than the legacy bundled icons (full-frame photos that fill the box edge-to-edge). The fix is to bake a trim into the PNG so the UI just does `QIcon(path)` like everything else (a brief experiment with per-paint runtime cropping was reverted: it scanned the 1000–1500px crafted photos pixel-by-pixel and beachballed when opening Crafting). Two pieces keep assets display-ready:
  - **Scrape time (new fetches):** `fetch_assets.py` trims the alpha bounding box (`getchannel("A").getbbox()`) *before* thumbnail/pad, so freshly fetched icons fill the frame. Lossless — only removes invisible pixels.
  - **Existing assets / batch fix:** `tools/trim_icons.py` trims small padded sprites (`<= 256px`) in `crafteditems/` and `fletcheditems/` in place. It is idempotent and skips the large full-frame photos (trimming those would change their look). Run it (via `.venv-qt/bin/python`, falls back to `QImage` when Pillow is absent) after adding sprites; then the UI renders them with a plain `QIcon(path)`. No runtime cropping helpers exist anymore.

### Woodcutting asset wiring (the log/hatchet/nest fetch)
- **Batch driver:** `tools/fetch_woodcutting_assets.py` (`uv run …`) fetches the whole Woodcutting manifest through one rate-limited `HttpWikiClient` so provenance is recorded per file and a single failure doesn't abort the rest. Re-run with `--force` to refresh.
- **Logs reuse `trees/`.** The `trees/<Name>.png` files *are* the log item sprites (see `WIKI_TITLE_OVERRIDES`: `Oak` → `Oak logs.png`). So `constants.LOG_IMAGES` just re-keys those files by log item name (`Oak logs` → `trees/Oak.png`) for the Bank/Stats registry — no second fetch. New tree rows only needed `Achey` (Achey tree logs) and `Hollow` (Bark).
- **Hatchets resolve on RS3, not OSRS.** OSRS calls them "axe"; the 2011 naming is "hatchet", which only exists on `runescape.wiki`. The OSRS-first/RS3-fallback order in `fetch_assets.py` handles this automatically.
- **Hatchets / nests / seeds live in `woodcuttingitems/`**, keyed by `constants._asset_slug(name)` and wired via `WOODCUTTING_EXTRA_ITEM_IMAGES`. Both `LOG_IMAGES` and that map are existence-guarded so `missing_required_asset_paths()` (asserted empty by tests) never trips on an unfetched item.
- **Ivy uses the Choking ivy interface icon.** Ivy has no inventory/log item, and `File:Ivy.png` (OSRS) is a full castle-wall *screenshot*, not an icon. The usable art is `File:Choking ivy icon.png` (RS3) — fetched into `trees/Ivy.png` so the (XP-only, no-output) row still shows a vine icon. Egg bird-nests and bird's eggs stay iconless (wiki titles don't resolve; vanishingly rare drops). Nest *ring* contents reuse the existing crafted ring sprites.

### Utility/Activities row icons
- Existing no-XP activity rows now use dedicated `activityicons/` PNGs instead of relying only on output-item material art. The row contract is `UTILITY_ACTIVITY_DATA[activity_id]["icon_path"]`.
- The Qt Utility target list prefers `icon_path` and falls back to `UTILITY_ITEM_IMAGES` for output-producing rows. Missing activity icons therefore degrade to the older output icon or text-only row, without changing action behavior.
- Fetch activity-row icons with `uv run tools/fetch_assets.py <item> --out activityicons/<activity_id>.png --wiki-title <File title> --size 64`, then confirm `assets_provenance.json` contains the `activityicons/` key. Do provenance-affecting fetches sequentially because the current JSON writer is not concurrency-safe.
- Current activity icon provenance: Soft clay, Wool, and Flax from OSRS wiki art; Open bird nests uses runescape.wiki `Bird's nest (seeds).png` because that title resolved there.

## Manual Testing Target
Manual verification should happen inside Anki when runtime behavior changes. Browser-based Pinchtab testing is only relevant if the change introduces browser-rendered surfaces that can be exercised outside Anki.
