# Papercuts fixed — 2026-10-27

## Bounded generated-catalog discovery

Disposition: fixed.

Evidence: already fixed: tools/repo_search.py DEFAULT_EXCLUDES omits shop_data.py/construction_data.py/combat_data.py; search_text uses --max-columns-preview and refuses incomplete result sets. python3 tools/repo_search.py Bucket data --max-results 2 --max-columns 120 returned two bounded results and exit 2 with Search stopped at 2 results. General packet/output truncation remains open.

- 2026-10-15T14:44:37.517135+00:00 — Warning: truncated output (original token count: 612614) rg matched generated single-line data/shop_data.py, defeating line-count bounds (1401878 bytes omitted). Switched to AST shape and filtered literals, never imported shops; no omitted output used as absence or values.
- 2026-10-15T15:03:49.254636+00:00 — A line search included the generated one-line data/shop_data.py. The result reported original token count583797 and1286609 bytes omitted. The Bucket producer was then read by AST at the exact shop/key. Omitted output supplied no evidence.
- 2026-10-15T15:48:58.426136+00:00 — Read-only source qualification round27 reported inspection friction (original event timestamp was not captured; this is Root receipt time): 2026-10-15: A Construction grep emitted a giant single-line literal; output original_token_count56964 truncated. No raw generated shop line was dumped. Later supply reads used AST projections.
- 2026-10-15T15:48:58.426136+00:00 — Read-only source qualification round28 reported inspection friction (original event timestamp was not captured; this is Root receipt time): {"at":"2026-10-15","what":"A git grep included the generated one-line shop literal despite the explicit prohibition.","path":"/Users/armantarkhanian/ankiscape_worktrees/pool/.treehouse/AnkiScape-091389/2/AnkiScape/data/shop_data.py","exact_tool_summary":"Warning: truncated output (original token count: 612260); ... 1400464 bytes omitted ...","effect":"Read-only output failure. The report records it for Root. Later inspection used AST-selected shop rows; raw literal is not embedded in this packet.","class_correction":"Select fields before printing; never grep a generated literal file directly.","recorded_at":"2026-10-15T15:43:28.040762+00:00","event_timestamp_status":"Exact event timestamp was not captured; recorded_at is the report timestamp."}

## Duplicate combat imports

Disposition: fixed.

Evidence: runtime/runtime_actions_combat.py now imports each shared combat helper and RuntimeActionContext once; the identical second import blocks were removed. AST duplicate-import probe and runtime tests verify this below.

- 2026-10-13 audit: runtime/runtime_actions_combat.py still imports _combat_review_ticks, _record_action and _refresh_combat_levels at both lines 389 and 413, and RuntimeActionContext at both lines 409 and 419; this Pass 14 follow-up remains open.

## Machine-local research paths

Disposition: fixed.

Evidence: Both current source documents now name /Users/armantarkhanian; Path.is_dir proved the Darkan and OpenRS2 roots exist. Historical incident paths remain verbatim.

- 2026-10-26T23:22:22.018799-07:00 — Owner supplement (2026-10-26): memory-bank/techContext.md:242 and the dated-cache section of the pre-EoC source verification standard use /Users/ArmanTarkhanian1/... paths. This MacBook home is /Users/armantarkhanian.

## Wiki title redirects

Disposition: fixed.

Evidence: tools/wiki_parity.py resolve emits every API redirect to stderr before returning the historical revision. The Inventory -> Backpack CLI/helper regression passes.

- 2026-10-26T23:22:22.018799-07:00 — Owner supplement (2026-10-26): tools/wiki_parity.py resolve follows redirects and gives no warning (Inventory became Backpack, and Grain became Wheat).

## Case-insensitive bounded search

Disposition: fixed.

Evidence: tools/repo_search.py accepts -i/--ignore-case and sends --ignore-case to rg. tests.maintenance.test_repo_search proves the same mixed-case fixture misses without -i and matches with it.

- 2026-10-26T23:22:22.018799-07:00 — Owner supplement (2026-10-26): tools/repo_search.py rejects -i; the agent must write (?i) in the pattern.

## Market ticks named as cards

Disposition: fixed.

Evidence: GE_MARKET_HOUR_TICKS=10, GE_BUY_LIMIT_WINDOW_TICKS=40, GE_MARKET_DAY_TICKS=240; every production/test reference uses ticks. The focused GE behavior suite passes.

- 2026-10-26T23:22:22.018799-07:00 — Owner supplement (2026-10-26): logic/grand_exchange_logic.py:16-18: the GE_MARKET_*_CARDS constants count market ticks, not cards.

## Runecrafting audit facts and citations

Disposition: fixed.

Evidence: The action-unit audit cites runecrafting_standard_base_capacity_pure by symbol and distinguishes the 27-essence carried-hood pack. runtime_actions_carried_requirements reserves the hood slot. The old Runecrafting adaptation now names daily allowances and commands implemented in wicked_hood_logic.py; caps probe returns essence=100, runes=1, teleports=2.

- 2026-10-26T23:22:22.018799-07:00 — Owner supplement (2026-10-26): memory-bank/source-audits/action-unit-normalisation-2026-08-22.md:11 cites stale lines (logic_pure/logic_pure_runecrafting.py:181-188; the code is now at :150-156) and omits that a packed Wicked hood gives 27 essence per trip.
- 2026-10-26T23:22:22.018799-07:00 — Owner supplement (2026-10-26): memory-bank/source-audits/runecrafting-2011scape-2026-06-17.md:38 says daily essence is deferred; logic/wicked_hood_logic.py:136-147 builds it.

## Assembled equipment catalog ownership

Disposition: fixed.

Evidence: memory-bank/techContext.md names core.constants as the EQUIPMENT_ITEM_DATA import owner; the exact import succeeds with a nonempty catalog.

- 2026-10-26T23:22:22.018799-07:00 — Owner supplement (2026-10-26): EQUIPMENT_ITEM_DATA lives in core.constants, not in data.equipment_data, which cost a probe a failed import.

## Missing speed versus malformed speed

Disposition: fixed.

Evidence: already fixed: tests/pace/test_game_speed_setting.py explicitly requires absent speed=1 and unreadable stored speed=10; tests/pace/test_pace_onboarding.py preserves existing players at 1 and recommends 10 for new players. Both suites passed in the 81-test focused run. No product change; techContext.md now records the deliberate distinction.

- 2026-10-26T23:22:22.018799-07:00 — Owner supplement (2026-10-26): The game speed read sites fall back to 1x when no speed is stored (ui/ui.py:1218, __init__.py:711, ui/ui_pace_settings.py:127), but sanitize_review_action_multiplier defaults to 10 (logic_pure/logic_pure_progression.py:330). Determine whether such a profile can exist before any fix.

## Shared speed reader for visible counters

Disposition: fixed.

Evidence: already fixed: ui/ui.py defines _game_speed; tests/pace/test_game_speed_setting.py checks runtime and UI against missing, valid, clamped and unreadable stored values. The complete focused selection passed: Ran 81 tests in 31.744s, OK. No UI code changed in this batch.

- 2026-10-18T17:00:00-07:00 — Pace counters: ui.py (27,916 lines, at its ratchet) had no shared game-speed reader, only an inline read in the Settings tab, which is why part E printed counters at x1; the new `_game_speed()` replaced that inline read so the file did not grow. Any new speed-dependent UI text should call it.
