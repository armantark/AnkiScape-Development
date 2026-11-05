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

## Pirate hook fixture loads its earned state before the undo baseline

Disposition: fixed.

Evidence: Current tests/item_tradeability/test_pirates_hook_tradeability.py::test_earned_hook_exchange_escrow_settlement_undo_and_reload saves the earned inventory and loads it through storage_load_player_data before copying its before_reward snapshot. This applies bank_layout normalization before the strict undo comparison. python3 run_tests.py tests.item_tradeability.test_pirates_hook_tradeability passed: Ran 1 test, OK. It also passed within the 143-test combined run (3 unrelated Pillow-only skips). All collection data was the test dummy; no profile database or real player save was opened.

- 2026-10-15T17:36:29.349586+00:00 — Pirate’s hook pre-edit proof first exited 1 before GE: full Undo equality differed in `bank_layout` because the earned inventory was injected after load; normalize through existing save/load before the snapshot. Original failure retained in external `pirates-hook-implementation-2026-10-15/red.log`.

## Period art follows the earliest move after its cutoff

Disposition: fixed.

Evidence: Inspected current tools/reresearch_period_art.py::_first_move_since and _query_history_following_moves (sed -n 105,170p). The logevents request sets lestart to the supplied cutoff, ledir=newer and lelimit=1; the move-chain caller starts at CUTOFF and advances since to each returned move timestamp. The code therefore asks for the earliest post-cutoff move instead of the newest move of a re-created title. This is a current-code check only; no live wiki request or fresh Yew asset verification was run.

- 2026-10-29T23:14:00-07:00 — Pass 19 renamed icons: following the newest move of `File:Yew tree.png` landed on `File:Yew.png` (a 2011 in-game scene) because the title was re-created and moved again in 2016; the 2012 icon left with the first post-cutoff move, to `File:Yew tree (Construction) icon.png` on 2014-04-06, so the tool follows the first move after the cutoff.

## Worktrees inherit tracked repository rules

Disposition: fixed.

Evidence: git ls-files --error-unmatch AGENTS.md succeeded in this guarded worktree and the AGENTS.md file was read at task startup. Repository-specific worktree/runtime rules are now tracked content; a checkout of this revision includes them without a generated canonical-only copy. No AGENTS.md content was changed.

- 2026-10-08T04:21:41.460463+00:00 Fenkenstrain author checkout has no tracked AGENTS.md; cat AGENTS.md returned cat: AGENTS.md: No such file or directory. Author uses supplied user rules and current canonical AGENTS read-only; no source or gate change.

## Source-root resolution stays inside the existing source-input module

Disposition: fixed.

Evidence: The first source-root commit was refused for growing tools/generate_npc_shop_data.py from 1257 to 1261 lines. Resolution moved into tools/npc_shop_generation/source_inputs.py::default_2011_items. wc -l tools/generate_npc_shop_data.py now reports 1257; the normal unmodified commit hook accepted commit 906d2872d. The revised python3 run_tests.py tests.shops.test_source_inputs check passed 33 tests, OK. No hook, guard or limit changed.

- 2026-11-05T08:54:55-08:00 — Papercut cleanup source-root commit refused: slop-gate reported code files above 1000 lines were grown: tools/generate_npc_shop_data.py: 1261 lines (was 1257). Move environment resolution into the existing tools/npc_shop_generation/source_inputs.py boundary; keep the gate and limits unchanged.

## Pass 21 initial fixture and module-boundary repairs

Disposition: fixed.

Evidence: e3e904a54f5be974ad78993898dd7e6afc11fc09 corrects the Iron-arrow fixture to ranged_level=15, derives diary dormancy through conditions, moves startup/loadout handling into logic_pure_combat_loadout.py and keeps shared queue supply below its callers. The present ammo selection passed 77 tests; the live-row/waking-row diary regression passed in the 13-test closure selection. The current imports use the repaired module boundaries and successful commits retain the hook.

- 2026-11-05 08:53:19 PST — Pass 21 follow-up fixtures assumed level 1 Iron arrows and a writable DiaryTask.dormant field; catalog requires ranged 15 and dormant derives from empty conditions ("TypeError: DiaryTask.__init__() got an unexpected keyword argument 'dormant'").
- 2026-11-05 09:13:48 PST — Pass 21 follow-up commit refused new complexity, oversized-file growth, and an action_queue/menu_action_queue import cycle; it reported "core/action_queue.py: _queue_edit_values 21 (new)" and "logic/achievement_diary_logic.py: tier_claim_state_pure 20 (was 18)". Moved shared supply logic below both callers and extracted ammunition row rendering and combat start/bank-window preparation.
- 2026-11-05 09:23:31 PST — The next Pass 21 follow-up commit refused "ui/ui.py: fan-out 176 (was 175)", "ui: 43 code files (was 42)" and "logic_pure/logic_pure_combat_engine.py: unused import 'combat_start_ammo_values_pure' (90% confidence)"; kept slots in the existing Equipment panel module and made combat dispatch use the shared startup helper directly.

## Ammo pickup row, device identity and hook repairs

Disposition: fixed.

Evidence: f8a2ab84521212838055c70b74b7b333a954eb2a places pickup beside the title in ui/review_hud_buttons.py, retains the device-flow player dictionary with update(picked), and moves lifecycle/rendering into the existing loadout/button modules and tools/maintenance. 309289ed7c21651a55ca8e8684d78fa8e0ab4f4b protects full title height. The 77-test ammo/HUD/strip selection and twelve shown offscreen geometry cases pass; both successful commits ran the hook.

- 2026-11-05: Offscreen ammo HUD check caught `Pick up ammo (840)` at 79px with 119px of text in the existing bottom action row; the added button belongs beside the title, with its own size hint, to preserve the chip and Bank run widths.
- 2026-11-05: The device-flow test cleared a no-op pickup result that was the same object as its input; combat then stopped firing and the unbounded test loop stalled. Stopped recorded PID `48099`; kept fixture identity with `update` and bounded the card loop.
- 2026-11-05: Ammo return commit hook refused oversized-file growth in `__init__.py`, `logic_pure/logic_pure_combat_engine.py`, `logic_pure/logic_pure_combat_model.py`, `tests/test_review_strip.py` and `ui/ui.py`; import fan-out `121 (was 120)` and `27 (was 26)`; `tools: 149 code files (was 148)`; and new `E303`/`E306` spacing. Moved lifecycle and HUD glue into existing modules, the supply summary into the loadout module, and the renderer into `tools/maintenance/`.

## Registered IDs and activity-command payloads

Disposition: fixed.

Evidence: 15d4321931f17090ab6cd715effcb1835eb42bf0 corrects the registered craft_air_runes/craft_nature_runes/cook_shrimps IDs, validates queue recipe specs and passes the Pest Control command payload mapping. Current tests/action_queue/test_queue_followup.py and tests/pace/test_ground_ammunition.py contain these repairs. The queue closure selection passes 13 tests; the ammo selection passes 77 tests.

- 2026-11-05T18:27:57+00:00 — Initial follow-up regressions used `air_rune`/`nature_rune` instead of `craft_air_runes`/`craft_nature_runes`, and passed Pest Control policy as keywords instead of its payload argument (`TypeError: enter_pest_control_pure() got an unexpected keyword argument 'automation_mode'`). Corrected the synthetic fixtures from the registered data and signature.
- 2026-11-05T18:27:57+00:00 — The mixed-fish regression used `cook_shrimp`; the registry key is `cook_shrimps`, so its supply limit was `None` instead of exercising the recipe. Corrected the key and added registry validation to the queue fixture before its assertions.

## Bork follows the live diary-tier claim rule

Disposition: fixed.

Evidence: b12a756fb fixes Bork elite reward eligibility for the live-row diary contract. The renamed current regression tests.test_bork.BorkRewardTests.test_varrock_elite_live_rows_give_the_elite_payout_with_dormant_rows_open passes in the 13-test closure selection on this branch. The historical twelve-task expectation is retired.

- 2026-11-05T18:27:57+00:00 — The 697-test activity combat selection failed `tests.test_bork.BorkRewardTests.test_known_varrock_elite_rows_do_not_bypass_the_twelve_task_gate` at `tests/test_bork.py:420`, `AssertionError: True is not false`, before its combat call. Bork diary-gate code is untouched by the three review fixes.

## Batch projection complexity repair

Disposition: fixed.

Evidence: 15d4321931f17090ab6cd715effcb1835eb42bf0 extracts shared batch outputs. Re-measuring _inputs_and_yield with tools/maintenance/function_metrics.py gives cyclomatic 13 and cognitive 14, no violations (/tmp/pass21-yield-metrics.json). Queue projection regressions pass in the 13-test closure selection.

- 2026-11-05T18:31:36+00:00 — The follow-up commit hook refused `_inputs_and_yield`: cyclomatic `18 (was 13)` and cognitive `16 (was 12)`, both above `15`. Moved complete batch output quantities and alternative/simultaneous output rules into one shared batch projection used by yield calculation and stock projection.

## Reservation fixture excludes unrelated Strange Rock rolls

Disposition: fixed.

Evidence: 15d4321931f17090ab6cd715effcb1835eb42bf0 pins test_removing_a_producer_keeps_only_the_count_still_funded to random 0.5. The current test retains that pin and passes in the 13-test closure selection. This closes the nondeterministic fixture only; the separate Strange Rock planning issue in another open entry remains open.

- 2026-11-05T18:37:50+00:00 — The post-hook 176-test selection observed the same unseeded Fletching `29 != 30` failure (`Ran 176 tests in 88.693s`, `FAILED (failures=1)`). RNG `0.99` passed the isolated case; RNG `0.0` failed `28 != 30` and exposed both Strange Rock replacements in its Event log. The reservation-only fixture now uses RNG `0.5`; gameplay is unchanged.

## Native-title probe imports and matrix complexity

Disposition: fixed.

Evidence: 309289ed7c21651a55ca8e8684d78fa8e0ab4f4b imports pkg_alias before ankiscape in the repeatable probe, checks button containment in the title row without moving the button and traverses the independent matrix with itertools.product. The 77-test selection passes; the probe captures twelve cases. Re-measured cognitive scores are 10 for the HUD regression and 11 for capture_hud, with no violations (/tmp/pass21-hud-test-metrics.json and /tmp/pass21-capture-metrics.json).

- 2026-11-05T11:11:22: Pass 21 probes: package imports require import pkg_alias before ankiscape; one inline probe omitted it and raised ModuleNotFoundError: No module named 'ankiscape'. Native-title test also overconstrained button/title centres (AssertionError: 2 not less than 2); replaced with row containment to preserve the original button position.
- 2026-11-05T11:14:45: Pass 21 commit hook blocked verification matrix helpers: slop-gate: cognitive complexity above 15 was introduced; AmmunitionHudTest::test_combat_title_fits_with_and_without_pickup_at_laptop_size 19 (new), capture_hud 20 (new). Flattened independent matrix axes with itertools.product.

## HUD layout investigation lookup and record limits

Disposition: record_only.

Evidence: The HUD task used bounded source reads after the truncated combined read; no docs/adr directory exists in this checkout. Both one-off tool incidents are preserved here instead of counting as unresolved product defects. The papercut containment check and docs audit verify this record repair.

- 2026-11-05T19:31:09Z — HUD layout investigation: the initial combined memory-bank read exceeded the tool output budget and the ADR lookup reported "rg: docs/adr: IO error for operation on docs/adr: No such file or directory (os error 2)"; use bounded per-file reads and existing paths.
- 2026-11-05T19:42:19Z — HUD evidence documentation audit reported "memory-bank/papercuts.md:1: papercuts_line_cap_exceeded: 800 papercut lines must stay under 800" after this turn recorded its lookup incident; retain the one-off incidents verbatim in the fixed log with record_only disposition.

## HUD action-row construction has its own existing module

Disposition: fixed.

Evidence: The complete action-row builder now lives in ui/review_hud_buttons.py. ui/ui.py shrinks against HEAD; the helper passes function_metrics.py, and the required real-HUD selection reports Ran 67 tests in 4.512s, OK. DPR-2 geometry captures pass unchanged.

- 2026-11-05T19:49:25Z — HUD layout commit hook rejected "slop-gate: code files above 1000 lines were grown:" and "ui/ui.py: 26423 lines (was 26416)"; move the complete action-row builder into ui/review_hud_buttons.py before retrying the commit.
