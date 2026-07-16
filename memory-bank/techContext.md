# Tech Context

## Runtime
- Python Anki add-on running inside Anki/AQT.
- Qt UI is accessed through `aqt.qt`.
- Persistent data is stored in Anki collection config via `mw.col.get_config` and `mw.col.set_config`.

## Development Setup
- Source lives directly in an Anki add-ons directory.
- This working copy should live in `addons21/ankiscape_fork`, not the AnkiWeb-managed numeric folder `addons21/1808450369`.
- The canonical checkout is the only AnkiScape checkout allowed inside
  `addons21`. Linked worktrees belong in the sibling
  `Anki2/ankiscape_worktrees/` directory and must be created/audited through
  `python3 tools/worktree_guard.py`; otherwise Anki loads each enabled worktree
  as a separate add-on copy.
- Future AnkiWeb updates may recreate or update `addons21/1808450369`; treat that folder as upstream and manually diff/merge changes into `ankiscape_fork`.
- The local working copy is a solo-project git repository on `main`.
- Work directly in the canonical `main` checkout and commit there. Do not create
  feature branches or linked worktrees unless the owner explicitly requests
  isolation for that specific task.
- Tests are run with `python3 run_tests.py`.
- Tests use Python's built-in `unittest`, not pytest.
- `run_tests.py` adds the repo root to `PYTHONPATH` so pure modules can be imported directly.
- `python3 tools/audit_item_reachability.py --json` emits the deterministic live action/acquisition graph ledger; its focused regression test is `tests/test_item_reachability_audit.py`.

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

## Source Data (full pre-EOC parity)
AnkiScape targets RuneScape immediately before EOC, with a strict cutoff of **2012-11-20**. The 2011Scape rev-667 source remains a strong baseline for unchanged systems, but 2012 content is a substantial required layer rather than a negligible exception. The project-wide evidence and blocking rules live in `memory-bank/pre-eoc-source-verification-standard.md`; the `ankiscape-skill-expansion` skill supplies the working expansion workflow.

- **The OSRS wiki is NOT a 2011 source.** OSRS branched from a 2007 backup; treat OSRS data as 2007 baseline + OSRS-only additions, useful only as a cross-check for 2007/2011-unchanged content.
- **Baseline implementation evidence:** the local `2011Scape/game` emulator source (Apache-2.0, client rev 667 = Oct 4 2011; upstream `github.com/2011Scape/game`) at `/Users/ArmanTarkhanian1/Downloads/game-main`. It is authoritative only for mechanics unchanged between that snapshot and the cutoff; later content and changed mechanics require pre-EOC 2012 evidence.
- **Historical semantics:** literal wikitext from exact pre-cutoff RuneScape Wiki `oldid` revisions, backed by dated Wayback captures where page histories or transcluded dependencies are unavailable.
- **Dated cache cross-checks:** the six OpenRS2 disk caches listed in `memory-bank/pre-eoc-source-verification-standard.md`. They can prove client-side identities and configuration present in a particular build—item/NPC/object names and IDs, options, sprites/models, interfaces, scripts, varbits—but normally cannot prove server-side XP, random rolls, quest gates, drop rates, action timing, or economy behavior.
- **Darkan:** use the fidelity-revamped implementation as server-mechanics evidence only after reconciling it with pinned pre-EOC sources. A modern Darkan commit is a reconstruction, not automatically period proof. Wait when the necessary high-fidelity behavior or corroborating history does not yet exist.

Current Woodcutting backend parity data lives in `woodcutting_data.py`, with a detailed audit at `memory-bank/source-audits/woodcutting-2011scape-2026-06-01.md`. It stores raw 2011Scape low/high chop chances and hatchet ratios, then lets `logic_pure.py` adapt them to Anki review cadence.

Current Mining backend parity data lives in `mining_data.py`, with a detailed audit at `memory-bank/source-audits/mining-2011scape-2026-06-01.md`. It stores raw 2011Scape low/high Mining chances, respawn-time data, pickaxe roll cadence, scoped simple historical targets, gem-drop tables, tradability, and Mining bonus metadata consumed through worn equipment. Storage config version 8 migrates old display-name Mining targets to stable IDs; storage config version 10 moves passive bonus ownership into `player_data["equipment"]`.


Current Crafting backend parity data lives in `crafting_data.py`, with a detailed audit at `memory-bank/source-audits/crafting-2011scape-2026-06-03.md`. It stores stable recipe IDs, source family/station metadata, real requirements/outputs, corrected 2011Scape XP values, and notes for input-starved content whose acquisition loop is not built yet. Storage config version 11 migrates legacy display-name `current_craft` values to stable IDs.

Current Smithing backend parity data lives in `smithing_data.py`, with detailed audits at `memory-bank/source-audits/smithing-2011scape-2026-06-01.md` and `memory-bank/source-audits/cannonball-smithing-implementation-2026-07-10.md`. `tools/generate_smithing_data.py` emits 9 ordinary smelt recipes, 158 anvil recipes, and the separate source-backed cannonball furnace process. Storage config version 9 migrates old `current_bar` saves to stable `current_smith` recipe IDs and normalizes legacy `Adamantite bar`/`Runite bar` inventory keys to source item names.

Current equipment backend data lives in generated `equipment_data.py`. `tools/generate_equipment_data.py` combines checked-in `smithing_data.py`, local 2011Scape `data/cfg/items.yml` equipment blocks, and `mining_data.py` Mining bonus items. Storage config version 10 adds flat `equipment` state, removes `owned_equipment`, and scaffolds planned combat level/exp defaults so equipment gates are real `*_level` checks before combat training exists.

Feathers now enter through live NPC shop stock and Combat drops. The temporary
`scavenge_chicken_feathers` Utility bridge documented in the dated
`memory-bank/source-audits/feather-utility-2026-06-15.md` was retired during the
shop-economy integration pass and must not be re-added.

Current Firemaking data lives in `firemaking_data.py`, with the audit at
`memory-bank/source-audits/firemaking-2011scape-2026-06-16.md`. It stores 13
local-2011Scape burnable targets, stable target IDs, input item IDs, source XP,
`Ashes` output metadata, raw source low/high lighting odds, and explicit
deferred bonfire/fire-spirit notes. Runtime review behavior adapts the source
lighting roll in `logic_pure.py`; storage config version 12 adds
`firemaking_level`, `firemaking_exp`, and `current_firemaking`.

Current Runecrafting data lives in `runecrafting_data.py`, with the audit at
`memory-bank/source-audits/runecrafting-2011scape-2026-06-17.md`. It stores
standard rune, combination rune, tiara binding, pouch, and Wicked hood feed
metadata from the local 2011Scape Runecrafting source. `quest_data.py` stores
Rune Mysteries and the one-time Wicked hood claim. Runtime review behavior
lives in `logic_pure.py`; storage config version 15 adds
`runecrafting_level`, `runecrafting_exp`, `current_runecrafting`,
`current_quest`, `quests`, `quest_points`, `claims`, `wicked_hood`,
`runecrafting_pouches`, and `item_charges`.

## Asset Scraping (icons)
`tools/fetch_assets.py` pulls one wiki icon at a time and records provenance. For pre-EOC RuneScape content, pass `--source rs3` so a same-named modern OSRS file cannot silently win. Use OSRS art only after independently proving that exact art belongs to the target era. Two practical asset gotchas remain:

- **Skill icons: prefer the `(detail)` variant.** The OSRS wiki ships both a small interface icon (e.g. `File:Fletching_icon.png`) and a higher-resolution `File:Fletching_icon_(detail).png`. The four original AnkiScape skill icons use the detail resolution, so fetch the `(detail)` file for new skills to match — the plain icon looks blurry/undersized next to them.
- **Item sprites render small unless they fill the frame — fix it in the asset, not at runtime.** Wiki item sprites are tightly cropped (e.g. an arrow is a thin diagonal, and Flax's real art is only ~30x23 inside a 64x64 file). Historically `--size N` normalized by `thumbnail((N,N))` then centering on a transparent NxN canvas, which *preserved* those transparent margins — so at the fixed 28px list icon box the visible sprite was much smaller than the legacy bundled icons (full-frame photos that fill the box edge-to-edge). The fix is to bake a trim into the PNG so the UI just does `QIcon(path)` like everything else (a brief experiment with per-paint runtime cropping was reverted: it scanned the 1000–1500px crafted photos pixel-by-pixel and beachballed when opening Crafting). Two pieces keep assets display-ready:
  - **Scrape time (new fetches):** `fetch_assets.py` trims the alpha bounding box (`getchannel("A").getbbox()`) *before* thumbnail/pad, so freshly fetched icons fill the frame. Lossless — only removes invisible pixels.
  - **Existing assets / batch fix:** `tools/trim_icons.py` trims small padded sprites (`<= 256px`) in `crafteditems/` and `fletcheditems/` in place. It is idempotent and skips the large full-frame photos (trimming those would change their look). Run it (via `.venv-qt/bin/python`, falls back to `QImage` when Pillow is absent) after adding sprites; then the UI renders them with a plain `QIcon(path)`. No runtime cropping helpers exist anymore.

### Woodcutting asset wiring (the log/hatchet/nest fetch)
- **Batch driver:** `tools/fetch_woodcutting_assets.py` (`uv run …`) fetches the whole Woodcutting manifest through one rate-limited `HttpWikiClient` so provenance is recorded per file and a single failure doesn't abort the rest. Re-run with `--force` to refresh.
- **Logs reuse `trees/`.** The `trees/<Name>.png` files *are* the log item sprites (see `WIKI_TITLE_OVERRIDES`: `Oak` → `Oak logs.png`). So `constants.LOG_IMAGES` just re-keys those files by log item name (`Oak logs` → `trees/Oak.png`) for the Bank/Stats registry — no second fetch. New tree rows only needed `Achey` (Achey tree logs) and `Hollow` (Bark).
- **Hatchets resolve on RuneScape Wiki, not OSRS.** OSRS calls them "axe"; the 2011 naming is "hatchet". Fetch them explicitly with `--source rs3`.
- **Hatchets / nests / seeds live in `woodcuttingitems/`**, keyed by `constants._asset_slug(name)` and wired via `WOODCUTTING_EXTRA_ITEM_IMAGES`. Both `LOG_IMAGES` and that map are existence-guarded so `missing_required_asset_paths()` (asserted empty by tests) never trips on an unfetched item.
- **Ivy uses the Choking ivy interface icon.** Ivy has no inventory/log item, and `File:Ivy.png` (OSRS) is a full castle-wall *screenshot*, not an icon. The usable art is `File:Choking ivy icon.png` (RS3) — fetched into `trees/Ivy.png` so the (XP-only, no-output) row still shows a vine icon. Egg bird-nests and bird's eggs stay iconless (wiki titles don't resolve; vanishingly rare drops). Nest *ring* contents reuse the existing crafted ring sprites.

### Utility/Activities row icons
- Existing no-XP activity rows now use dedicated `activityicons/` PNGs instead of relying only on output-item material art. The row contract is `UTILITY_ACTIVITY_DATA[activity_id]["icon_path"]`.
- The Qt Utility target list prefers `icon_path` and falls back to `UTILITY_ITEM_IMAGES` for output-producing rows. Missing activity icons therefore degrade to the older output icon or text-only row, without changing action behavior.
- Fetch activity-row icons with `uv run tools/fetch_assets.py <item> --out activityicons/<activity_id>.png --wiki-title <File title> --size 64`, then confirm `assets_provenance.json` contains the `activityicons/` key. Do provenance-affecting fetches sequentially because the current JSON writer is not concurrency-safe.
- Current activity icon provenance: Soft clay, Wool, and Flax from OSRS wiki art; Open bird nests uses runescape.wiki `Bird's nest (seeds).png` because that title resolved there.

### Firemaking asset wiring
- `tools/fetch_firemaking_assets.py` derives the Firemaking-only asset manifest
  from `firemaking_data.FIREMAKING_TARGETS` and uses the shared
  `tools/fetch_assets.py` client/provenance writer.
- The skill icon uses `File:Firemaking icon (detail).png` and lands at
  `icon/firemaking_icon.png` with `--size 64`, matching the detail-icon
  convention for playable skills.
- Most logs reuse existing Woodcutting log art via `LOG_IMAGES`. Firemaking-only
  inputs plus Ashes live in `firemakingitems/` and are wired through
  `FIREMAKING_ITEM_IMAGES`: `ashes.png`, `arctic_pine_logs.png`,
  `eucalyptus_logs.png`, `curly_root.png`, and `cursed_magic_logs.png`.
- Provenance is recorded in `assets_provenance.json`; do Firemaking asset
  refreshes sequentially because the provenance JSON writer is not
  concurrency-safe.

### Runecrafting asset wiring
- `tools/fetch_runecrafting_assets.py` derives the Runecrafting manifest from
  `runecrafting_data.py` and uses the shared `tools/fetch_assets.py`
  client/provenance writer.
- The skill icon uses `File:Runecraft icon (detail).png` and lands at
  `icon/runecrafting_icon.png`.
- Runes, talismans, tiaras, pouches, the Wicked hood, and Binding necklace live
  in `runecraftingitems/` and are wired through `RUNECRAFTING_ITEM_IMAGES`.
- Rune/Pure essence reuse Mining ore art; do provenance-affecting refreshes
  sequentially because the provenance JSON writer is not concurrency-safe.

### Prayer passive asset wiring
- `tools/fetch_prayer_assets.py` derives Prayer materials and passive-item rows from `prayer_data.py` and `prayer_passive_data.py`.
- Its fetch path is explicitly restricted to `RS3_WIKI`; do not restore the shared OSRS-first fallback for these pre-EOC assets without independent exact-period art proof.
- Bonecrusher and Ectoplasmator live at `prayeritems/bonecrusher.png` and `prayeritems/ectoplasmator.png`; `tests/test_urns.py` requires `source_wiki == "rs3"` for both provenance rows.
- Run Prayer/provenance fetches sequentially because the shared JSON writer is not concurrency-safe.

### Herblore asset wiring
- `uv run tools/fetch_herblore_assets.py` derives its manifest from the live,
  already-filtered `CLEAN_TARGETS + UNF_TARGETS + FINISHED_TARGETS` catalog.
- The 113 row outputs are fetched through the RS3-only source path. The skill
  rail intentionally uses OSRS `Herblore icon (detail).png`, the compact icon
  family used by the other skill rails, rather than modern RS3
  `Herblore detail.png`.
- `HERBLORE_ITEM_IMAGES` is existence-guarded and target metadata looks up each
  row's output item, so clean herbs, unfinished potions, and finished potions
  render their own sprites.
- Run the manifest sequentially because every request updates `assets_provenance.json`.

## Manual Testing Target
Manual verification should happen inside Anki when runtime behavior changes. Browser-based Pinchtab testing is only relevant if the change introduces browser-rendered surfaces that can be exercised outside Anki.
