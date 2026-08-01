# pass5-strip trace

## Round 1

- Hypothesis: A single fixed-height strip anchored to Anki's live answer-bar edge, with card scroll reserve owned by the same geometry pass, removes per-card bounce without covering card material; pure row projections and one shared feedback seam can close the Event and GE clauses without UI re-derivation.
- Change: `6d7cccc4` (`feat: pin the reviewer status strip`).
  - Added the fixed D&D → Farming → XP → Do bank run strip, upward Event/GE drawers, live answer-bar anchoring, base plus transient card padding, and strip-relative floating text.
  - Event rows name awarded skills, wrap, remain selectable/copyable, avoid GE green/yellow, and retain XP plus every activity popover emitted in mixed reviews.
  - GE rows remain newest-first with Now/N cards ago and partial/complete tones, clear on hide, and navigate to the existing GE tab.
  - The bank button uses a thin request seam: combat enters `combat_bank_run`; carried activities hand the request to the existing target-specific review-paced travel path. The separate pass5-combat export is not present on this branch, so this is the intended trivial merge seam.
- Test results before commit:
  - Targeted plain: 210 tests passed after preserving utility feedback aggregation while logging every mixed XP/activity emission.
  - Targeted offscreen Qt: 28 tests passed, with `show()` and event pumping before geometry probes at 700 and 560 logical pixels.
  - Compile and `git diff --check`: passed.
  - Full plain lane initially exposed one stale singleton test that still expected the HUD under `mw`; the test now verifies the ratified HUD-under-strip hierarchy and passes in the targeted lane.
  - Independent Kimi verifier found two real defects (mixed XP/activity messages dropped; bank button visibility latched after a too-short window). Both are fixed and covered by integration/offscreen regressions.
- Open questions: none in this branch. Owner playtest remains the final closure gate; status is fixed-pending-confirmation.

## Round 2

- Hypothesis: The floating popup must anchor above the highest visible member of the strip stack, not only above the XP box, or an open context/Event/GE drawer can overlap it even though both individually follow the pinned strip.
- Change: `6c2b2dfc` (`fix: keep floating feedback above strip drawers`).
- Test results:
  - Popup and strip offscreen regression set: 29 tests passed.
  - Final plain lane: 3,672 tests passed, 423 skipped.
  - Final offscreen Qt lane: 3,672 tests passed, 2 skipped.
  - Geometry probes used shown widgets and processed events; the final Qt lane covers the 560-point reviewer, live answer-bar edge, late tall-image growth, drawer scroll reserve, popup clearance, and bank-button hide/restore lifecycle.
  - Independent Kimi re-verification after both commits: `CLEAN` across all frozen clauses and the two earlier findings.
- Open questions: none. The external pass5-combat hook is still intentionally absent here; the committed thin seam is ready for the orchestrator's merge.

## Round 3 — diff-only simplification pass

- Hypothesis: The two strip commits carry complexity that no owner clause
  requires, so a deletion-only pass over `git diff main...HEAD` can shrink the
  diff without touching any clause behaviour.
- Change: `2711e380` (`refactor: simplification pass`). Net −43 lines across
  `__init__.py`, `logic/review_strip_logic.py` and `ui/ui.py`.
  - Skill naming for XP events ran through a context key `"skills"` *and* a
    parallel module tuple `_REVIEW_FEEDBACK_OUTPUT_SKILLS`, with the same
    de-duplication loop written out in four places, plus a `skills=` keyword on
    `_show_exp` that no caller ever passed. One module-level list
    `_REVIEW_FEEDBACK_SKILLS` now serves the per-award, quest-reward and
    end-of-review aggregate paths.
  - `_sync_card_bottom_padding` took a fabricated `{"visible": ...}` layout dict
    at three of its four call sites; it now takes the reserved height directly.
  - `_reposition_review_overlay` set widget visibility in two identical loops;
    they are one loop.
  - `review_overlay_layout_view_pure` kept an unused `gap` argument and wrapped
    an `int()` on a UI-supplied integer in `try/except (TypeError, ValueError,
    OverflowError)`; both are gone, and the docstring no longer claims
    back-compatibility with "older add-on copies" that do not exist.
  - `review_bank_run_button_view_pure` used a conditional expression whose
    `else` branch silently absorbed an `or` chain, and a three-way nested
    ternary for the tooltip; both are plain branches now.
- Deliberately kept, with reasons:
  - `content_rect` on the layout projection. It is ignored by design, but the
    frozen clause "vertical measurement includes images" is evidenced by tests
    that feed short and tall rects and assert identical geometry. Removing the
    parameter would delete that guard rather than the complexity.
  - `REVIEW_BANK_RUN_HANDLER_KEYS` duplicates runtime `_OVERLAY_TARGET_KEYS`.
    De-duplicating means the pure logic layer importing the runtime layer, which
    would drag runtime into the pure-logic tests. A comment now records the pair.
  - The per-row `"action": "open_grand_exchange"` on GE rows. Dropping it would
    also make the empty-state row open the exchange.
- Test results: plain lane 3,672 passed / 423 skipped; offscreen Qt lane 3,672
  passed / 2 skipped. No test needed editing, which is the evidence that the
  pass removed only unreferenced code.
- Open questions: none. Clause coverage is unchanged; owner playtest is still
  the closure gate.

## Round 4 — independent-verifier refix

- Hypothesis: The rejected clauses are Qt/runtime seam defects rather than pure-view defects: escape the ampersand only when assigning the D&D title to `QToolButton`; leave each wrapped event-log item's delegate text empty; when XP exists, record every activity row without replacing the XP popup; give the bank-run seat the same opaque HUD background; shrink all four seats within the clamped strip width; and cap the upward drawer stack while reserving exactly one strip height in the card document.
- Change: `158bea3f657a069af793ac49823e2790529dbc40` (`fix: close reviewer strip verifier regressions`).
  - D&D: the pure title remains `D&D`; the Qt seam assigns `D&&D`, so the painted label is `D&D` rather than mnemonic-rendered `DD`.
  - Event log: wrapped selectable `QLabel` rows are backed by empty `QListWidgetItem` text, preventing the delegate from painting a duplicate line underneath.
  - Popup/event coexistence: XP-bearing reviews emit one XP popup and persist every activity message to the Event log without calling `show_text` on the shared popup widget.
  - Bank-run visibility and narrow widths: the action has the opaque HUD background, and D&D → Farming → XP → bank-run seats remain ordered and inside the strip through the 480-point probe.
  - Drawer/card geometry: document padding stays exactly `REVIEW_STRIP_HEIGHT`; open drawers are height-bounded and remain above the strip without clipping at the 700×360 probe.
  - Combat merge note: `on_request_review_bank_run` is the single thin call to `request_review_bank_run_pure`. On merge, retain or re-point this seam to the pass5-combat exported hook; its combat state shape is `{"reviews_remaining": COMBAT_BANK_RUN_REVIEWS, "target_id": target}` and the carried-activity path remains handled by `runtime_actions_carried.run_answer_with_carried_overlay`.
- Test results:
  - Full plain lane: 3,656 tests passed, 417 skipped (`python3 run_tests.py`).
  - Full offscreen Qt lane: 3,656 tests passed, 2 skipped (`QT_QPA_PLATFORM=offscreen python run_tests.py` in `.venv-qt`).
  - Offscreen regressions show the parent before grabs and pump events; geometry probes cover the 480-point strip and 700×360 drawer stack, while the light-card bank seat is checked from its rendered pixels.
- Open questions: none. Every verifier rejection has a regression assertion; owner playtest remains the final closure gate.

## Round 5 — independent-verifier second refix

- Hypothesis: The remaining failures share three stale state boundaries: card padding tracked only the row instead of the complete visible stack; XP skill identity lived in a mutable module queue instead of the award/result and real review delta; and bank requests were artificially restricted to handlers with carried packs even though the registered dispatch wrapper can spend a review for every handler.
- Change: `03d4763d` (`fix: satisfy reviewer strip closure clauses`).
  - Card safety now derives the reserved document inset from the actual shown strip, collapsed/expanded drawers, and context strip. The status popover consumes a pure card-safe placement and closes when the measured card rectangle leaves no clear placement.
  - XP award results carry immutable skill names for direct emissions; review aggregation verifies names from actual experience deltas. Silent pouch-infusion Summoning XP can no longer leak into the later Hunter row.
  - The button projection derives support from all 22 registered review actions. Combat and carried handlers retain their existing paths; Magic, Construction, Dungeoneering, Quests, Utilities, and Activities consume the next review as the standard one-review bank trip.
  - A single-pass inline `/simplify` review removed redundant popover candidates and redundant review-context skill accumulation. Agent fan-out was unavailable in this subagent context.
- Test results:
  - Full plain lane: 3,679 tests passed, 426 skipped (`python3 run_tests.py`).
  - Full offscreen Qt lane: 3,679 tests passed, 2 skipped (`QT_QPA_PLATFORM=offscreen python run_tests.py` in `.venv-qt`).
  - Faithful shown-widget geometry probe at 1000×700: strip `y=500 h=128`, Event header `y=456 h=38`, GE header `y=412 h=38`, reserved padding `216`, protected top `412`; both headers are fully inside reserved document space.
  - Runtime registry probe: all 22 display actions, including the six rejected surfaces, report `visible=True` and `enabled=True` before a request.
  - Targeted integration/offscreen regressions cover silent Summoning → Hunter naming, generic-handler review consumption, tall-card popover refusal, short-card popover placement, collapsed headers, expanded drawers, and late image growth.
  - Documentation audit still reports six pre-existing status HTML files without doctypes; this round did not touch those archived artifacts.
- Open questions: none. The three rejected clauses are fixed-pending-confirmation; owner playtest remains the final closure gate.

## Round 6 — combat bank-run refix

- Hypothesis: The always-visible button failed only on Combat because the strip used an undefined default target and reconstructed the combat lane's bank-run state instead of delegating to its exported request hook.
- Change: `cf5e2e56` (`fix: route strip combat bank runs through engine hook`).
  - Imported the real `DEFAULT_COMBAT_TARGET`, so Combat surface refresh and callback dispatch no longer raise when the save omits `current_combat_target`.
  - Backported and exported the exact `request_combat_bank_run_now_pure` hook from `pass5-combat`, because that branch is not merged into this worktree.
  - Replaced the strip's hand-written `combat_bank_run` state literal with one thin call to that hook. On branch integration, reconcile the identical hook/export and retain this single strip call.
- Test results:
  - Full plain lane: 3,681 tests passed, 426 skipped (`python3 run_tests.py`).
  - Full offscreen Qt lane: 3,681 tests passed, 2 skipped (`QT_QPA_PLATFORM=offscreen python run_tests.py` in `.venv-qt`).
  - Driven add-on callback probe: the Combat strip resolved the missing target to `chicken`, invoked its captured button callback, committed one undoable direct action, queued `{"reviews_remaining": 2, "target_id": "chicken"}`, and refreshed from the committed state.
  - Engine-gate probe: a live combat encounter refused the request and left `combat_bank_run` empty, proving the strip consumes engine policy rather than re-deriving it.
- Open questions: none. The rejected clauses are fixed-pending-confirmation; owner playtest remains the final closure gate.
