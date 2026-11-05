# Papercuts fixed — 2026-11-05

## Dark Qt capture fixtures define row and button colors

Disposition: fixed.

Evidence: Added AlternateBase to tests/pace/test_pace_settings_qt.py and Button/ButtonText to tests/ui_flows/test_first_cell_selection.py. Two new capture-palette regressions first failed with AlternateBase lightness 247 and Button lightness 239, then python3 run_tests.py tests.pace.test_pace_settings_qt tests.ui_flows.test_first_cell_selection passed: Ran 14 tests, OK. Current tools/render_skill_panel_ui.py already explicitly sets AlternateBase to QColor(45, 45, 45). Only test fixtures changed; no product interface change.

- 2026-10-28T00:19:29-07:00 — Pass 18 ticket 06: the shared test dark palette (_dark_palette in tests/pace/test_pace_settings_qt.py) sets no AlternateBase, so offscreen dark captures paint every second list row white and a selected alternate row near-white on pale green; it reads as a dark-mode defect but is the test palette.
- 2026-10-28T00:27:07-07:00 — Pass 18 ticket 07: _dark_palette in tests/ui_flows/test_first_cell_selection.py sets no Button or ButtonText color, so Fusion tab labels are almost invisible in offscreen dark captures made with it.
- 2026-10-28T03:32:50-07:00 — Pass 18 ticket 10: the shared offscreen dark palettes in tools/render_skill_panel_ui.py and tests/pace/test_pace_settings_qt.py leave AlternateBase at the light theme's white, so every second list row paints white in dark captures; each capture script must set it (tickets 06 and 10 both did).

## NPC shop generation honors the configured source root

Disposition: fixed.

Evidence: tools/generate_npc_shop_data.py now derives its default --items-2011 from ANKISCAPE_GAME_MAIN, matching the existing source-root convention. Explicit --items-2011 takes precedence. The new fixture regression first failed because the manifest bound the Studio source instead of the configured fixture; python3 run_tests.py tests.shops.test_source_inputs then passed: Ran 33 tests, OK. These checks generated only disposable fixture catalogs and retained the digest refusal checks; no gameplay catalog was regenerated.

- 2026-10-28T00:19:29-07:00 — Pass 18 ticket 06: tools/generate_npc_shop_data.py defaults --items-2011 to the Mac Studio path /Users/ArmanTarkhanian1/Downloads/game-main/data/cfg/items.yml, which does not exist on the MacBook; every MacBook regeneration needs --items-2011 /Users/armantarkhanian/ankiscape-remote-test-host/sources/game-main/data/cfg/items.yml.

## Function metrics accepts a unique qualified method name

Disposition: fixed.

Evidence: tools/maintenance/function_metrics.py validates a qualified method against its exact AST scope, then joins the unchanged slop-gate instrument tables by its file-unique bare name. Duplicate bare names and nested functions remain refused; no fleet hook or guard was changed. The existing unique-method regression first failed for Example.choose with exit 2, then python3 run_tests.py tests.maintenance.test_function_metrics passed: Ran 11 tests, OK. Bare and qualified names produce identical measured CCN, cognitive complexity and Halstead difficulty.

- 2026-10-28T04:35:58-07:00 — Pass 18 review fixes: tools/maintenance/function_metrics.py refuses a qualified method name ("QueueCount._credit: expected one file-unique bare function name"), so a class method cannot be measured by name.

## Historical downloads already retry uncached and verify exact bytes

Disposition: fixed.

Evidence: Current tools/fetch_assets.py::_download_source_bytes constructs a unique cache_bust on every attempt and accepts bytes only when their SHA-1 matches the API revision. tools/reresearch_period_art.py::_download_matching_sha1 also retries each URL with an uncached query. python3 run_tests.py tests.historical_assets.test_fetch_assets_source_urls tests.test_fetch_assets passed: Ran 29 tests, OK (skipped=3 Pillow-only checks). The active local HTTP regressions test recompressed first responses, query preservation, distinct retries and rejection after three mismatches. No asset was fetched from the Internet or written to the repository.

- 2026-10-29T23:10:46-07:00 — Pass 19 renamed icons: tools/reresearch_period_art.py reported sha_mismatch for `File:White candle.png` on one asset and replaced the same revision on another; Cloudflare Polish ("cf-polished: ok, orig_size=394") serves recompressed bytes a41a2dd318bd18072587c7fe513dc7f31ed1a93e on a cache hit, while a never-cached query string returns the uploaded bytes dab5404b4da5e9f8eb2441509bf47ce58acc40f9. The tool now retries each URL uncached; tools/fetch_assets.py downloads do not.

## Dye menu fixtures preserve runtime aliases while restoring real Qt

Disposition: fixed.

Evidence: Current tests/main_menu/bank/test_dye_mixing.py::DyeMixingMenuTest.setUp snapshots sys.modules before the undo seam, retains the ankiscape_undo_seam modules needed by lazy imports, then restores real Qt before constructing menu widgets. python3 run_tests.py tests.main_menu.bank.test_dye_mixing passed: Ran 4 tests, OK, including opening and clicking the Bank mix menu, undo, and the Utility dye search. Neither reported import error recurred. Only simulated test players were used.

- 2026-10-28T00:25:18-07:00 — Pass 18 ticket 05: a mixed Qt and runtime test harness raised "ImportError: cannot import name 'ActionQueuePanel' from 'ankiscape.ui.ui_action_queue'" and then "ModuleNotFoundError: No module named 'ankiscape_undo_seam'" until the test kept runtime-package modules for lazy imports and restored real Qt and stable-alias modules before building widgets (tests/main_menu/bank/test_dye_mixing.py).

## Dispatcher fixtures restore process-wide random functions and state

Disposition: fixed.

Evidence: Current tests/runtime_actions/test_dispatcher_state.py saves each original random.random callable before replacement, registers addCleanup(setattr, ..., random_roll), and restores RNG state with addCleanup(setstate, ...). The permanent lambda assignment recorded in this incident no longer exists. python3 run_tests.py tests.runtime_actions.test_dispatcher_state tests.test_undo_seam_slayer tests.test_fight_caves passed: Ran 51 tests, OK. The combined papercut-focused run also passed 143 tests (3 unrelated Pillow-only skips), exercising real-Qt fixtures and these fake-runtime/undo consumers together.

- 2026-10-18T11:25:53-07:00 — Pace part C baseline: my new dispatcher test assigned `addon.random.random = lambda: 0.01`; `addon.random` is the process-wide `random` module, so every later test in the full plain lane saw a frozen RNG ("AssertionError" in tests.runtime_actions.test_dispatcher_state, tests.test_undo_seam_slayer, tests.test_fight_caves undo/RNG tests). Patch it with `self.enterContext(patch.object(addon.random, "random", ...))`.
