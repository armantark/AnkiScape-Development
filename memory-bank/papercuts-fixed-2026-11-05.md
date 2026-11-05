# Papercuts fixed — 2026-11-05

## Dark Qt capture fixtures define row and button colors

Disposition: fixed.

Evidence: Added AlternateBase to tests/pace/test_pace_settings_qt.py and Button/ButtonText to tests/ui_flows/test_first_cell_selection.py. Two new capture-palette regressions first failed with AlternateBase lightness 247 and Button lightness 239, then python3 run_tests.py tests.pace.test_pace_settings_qt tests.ui_flows.test_first_cell_selection passed: Ran 14 tests, OK. Current tools/render_skill_panel_ui.py already explicitly sets AlternateBase to QColor(45, 45, 45). Only test fixtures changed; no product interface change.

- 2026-10-28T00:19:29-07:00 — Pass 18 ticket 06: the shared test dark palette (_dark_palette in tests/pace/test_pace_settings_qt.py) sets no AlternateBase, so offscreen dark captures paint every second list row white and a selected alternate row near-white on pale green; it reads as a dark-mode defect but is the test palette.
- 2026-10-28T00:27:07-07:00 — Pass 18 ticket 07: _dark_palette in tests/ui_flows/test_first_cell_selection.py sets no Button or ButtonText color, so Fusion tab labels are almost invisible in offscreen dark captures made with it.
- 2026-10-28T03:32:50-07:00 — Pass 18 ticket 10: the shared offscreen dark palettes in tools/render_skill_panel_ui.py and tests/pace/test_pace_settings_qt.py leave AlternateBase at the light theme's white, so every second list row paints white in dark captures; each capture script must set it (tickets 06 and 10 both did).
