# Pass 5 combat trace

## Round 1 — rejected

- Hypothesis: The combat pack-mode allocation was too small, Dream automation needed a level/quest gate when the dial changed, and the two activity controls only needed a shared callback when their selected target already matched the visible surface.
- Changes: `5861c6c4`, `0ec0989b`, `50d6a0cd`, `132e9815`.
- Test results: Both full lanes were green, but the verifier's read-only owner-save probe disproved closure.
- Evidence and verdicts:
  - Food allocation: rejected. The owner save still had `combat_dream_thrift=true`, a live Citizen encounter at 67 LP, and `Shrimps: 1`; unload/refill refused the live fight, so all three modes stayed identical.
  - Mode-switch visibility: rejected. The handler discarded both status tuples and displayed no refusal.
  - Bank run for all skills/activities: rejected. Activities, Utilities, and Quests had no target entry and returned false.
  - Dream lock: rejected. Migration to v104 preserved the invalid latch and stranded encounter.
  - Unified activity start: rejected. The top-right control retained a legacy `active`/`on_save_skill` fallback when the target belonged to the other surface.
  - Save repair: rejected. The migration tested a fictional `activity_session.active_id='shooting_stars'`; the owner payload had an empty session and a selected Shooting Star target.
  - Neighboring regressions: rejected. Pack-mode unload skipped achievement evaluation, and the low-level Dream checkbox remained clickable but ineffective.
- Decision: Keep the underlying mode allocations and callback seam, then replace the failed diagnosis and fallback behavior in round 2.
- Open questions: None. The owner-verbatim clauses and rejected owner-save payload determine the repair.

## Round 2 — fixed pending owner confirmation

- Hypothesis: An ineligible latched Dream flag strands the live encounter before combat can resolve it; that encounter blocks every supply rebalance. The remaining failures come from incomplete review-surface target routing and a legacy activity-start fallback.
- Change: `7cd759c2`.
- Test results:
  - `python3 run_tests.py` — 3,656 tests passed, 417 skipped.
  - `source "/Users/ArmanTarkhanian1/Library/Application Support/Anki2/addons21/ankiscape_fork/.venv-qt/bin/activate" && QT_QPA_PLATFORM=offscreen python run_tests.py` — 3,656 tests passed, 2 skipped.
  - Targeted pure/integration lane — 703 tests passed.
  - Offscreen main-menu lane — 347 tests passed. The dialog was shown, resized to 1200×560, and processed before the driven probes.
- Evidence per clause:
  - Read-only owner-save inspection: SQLite was opened with `mode=ro`. The live payload was config v103 with `combat_dream_thrift=true`, Magic 1, Dream Mentor incomplete, Citizen at 67 LP, `Shrimps: 1` loaded, 89 banked, `current_utility='shooting_stars'`, and `activity_session.active_id=''`.
  - Food modes differ and auto-repair: migrating the reported payload to v105 cleared Dream and the stranded encounter, removed all preset lock reasons, and automatically loaded 14 Shrimps. Driven mode switches then loaded Balanced 14, Max output 8, and Max safety 20, all with `ok=true`.
  - Visible mode-switch result: a real active fight returned false, kept the visible and saved mode on Balanced, kept 14 food, saved nothing, and displayed `Finish the active fight before changing supply mode.` Between fights, Max output succeeded and visibly loaded 8.
  - Bank run for every review surface: driven add-on calls returned true for Combat, Mining, Activities, Utilities, and Quests. Activities/Utilities requested `shooting_stars`; Quests requested `rune_mysteries`; their next review consumed the request, skipped the ordinary handler, saved once, and emitted `Bank run — arrived and ready`.
  - Dream root cause and migration: the combat sanitizer now gates Dream from the source-backed 79 Magic/Dream Mentor rule and clears only an encounter stranded by that invalid latch. The v105 load repair refills supplies immediately. `combat_magic_preset_locked_reasons_pure` returned no reasons after migration.
  - One activity transition: with `current_utility='make_soft_clay'`, the shown Activities panel's top-right Start activity button made exactly one `on_start_activity` call, selected `warriors_guild_animated_armour`, and did not use the legacy `active`/`on_save_skill` pair. The Shooting Star card uses the same surface-keyed transition.
  - Existing-save repair: the v105 current-skill migration maps the reported selected Shooting Star plus inactive review surface to `Activities` exactly once; it does not override an active `Woodcutting` surface or a v105 save.
  - Achievement regression: switching Balanced 14 food to Max output 8 evaluated achievements after returning the excess; the driven observation saw 92 banked Shrimps and one save.
  - Dream control: at Magic 1 with Dream Mentor incomplete, the shown checkbox was disabled and its tooltip read `Requires 79 Magic and Dream Mentor.`
- Per-clause verdict: pass for implementation evidence; package status is `fixed-pending-confirmation` until the owner's pass-6 playtest.
- Simplification review: one inline four-angle pass found no safe deletion that preserved the owner-save migration, status propagation, universal routing, and unified UI transition. The full four-agent fan-out was unavailable.
- Open questions: Only owner confirmation on the next playtest.
