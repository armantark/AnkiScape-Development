# Ammo pickup icon proof, 2026-11-05

Implementation branch: `goal/pass21-followup`. No promotion or native Anki acceptance is recorded here.

The review HUD uses the shared `_pixel_item_icon` lookup at 16 logical pixels. It chooses the first nonempty ground-pile type, then worn ammunition for an empty pile, with Bronze arrows as the missing-art fallback. The proof fixtures resolve to `fletcheditems/bronze_arrows.png`. Real HUD tests also cover Steel arrows in the pile, Iron arrows worn with an empty pile, and missing-art fallback. Existing click, zero-count disabled state and ranged-ammo visibility behavior remain covered.

Run from the pass21-followup worktree:

```sh
python3 run_tests.py tests.pace.test_ammunition_hud tests.test_review_hud tests.test_review_strip tests.integration_smoke.test_world_clock_and_routes tests.pace.test_ground_ammunition
```

Output copied from the run:

```text
Ran 68 tests in 3.913s

OK
```

Capture command:

```sh
.venv-qt/bin/python tools/maintenance/render_ground_ammunition_hud.py --output /Users/ArmanTarkhanian1/Documents/ankiscape-pass21/review/followup/
```

The real review-strip fixture shows the parent before resizing, pumps Qt events, uses Fusion with explicit light/dark palettes, and asserts tooltip, non-null icon, count, enabled state, content fit and non-intersection. At both 1000×700 and 720×560, in both themes, HUD-local rectangles `(x, y, width, height)` are:

| Count | Pickup | Title | Kills | Bank run |
| --- | --- | --- | --- | --- |
| 0 | (195, 99, 40, 20) | (50, 4, 278, 21) | (12, 94, 177, 30) | (241, 94, 87, 30) |
| 42 | (189, 99, 46, 20) | (50, 4, 278, 21) | (12, 94, 171, 30) | (241, 94, 87, 30) |

All three pickup intersection checks are false. Icon-plus-text content fits in 26 pixels at 0 and 32 pixels at 42. The render utility also uses Qt mouse events to assert hover and pressed images differ from the preceding state.

Evidence directory: `/Users/ArmanTarkhanian1/Documents/ankiscape-pass21/review/followup/`. `hud-icon-geometry.json` contains exact paths and measured rectangles; `hud-icon-render.log` contains the render output and `hud-icon-tests.log` contains the final test output. Eight primary HUD captures cover `hud-icon-{dark,light}-{1000x700,720x560}-ammo-{0,42}.png`. Each has a `-window.png` companion; enabled cases have `-hover.png` and `-pressed.png` button captures.

The implementer inspected all eight HUD and window captures, and both themes' 720×560 hover and pressed captures. No cut text or overlap was found. The visible frame reads as a button; the off icon and count remain legible. A small thumbnail initially made the dark count look dark; enlarged inspection showed light numerals, so no product change followed that impression. Offscreen evidence does not prove native macOS/Anki rendering. Frontend-taste review before promotion remains the parent task's gate.
