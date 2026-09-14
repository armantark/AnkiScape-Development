# Pass 14 execution contract

Goal: end stale Encounters and show Slayer completion after the review.
Read the owner brief and STANDING-SLICE-CONTRACT in full. Rulings in design-thread-queue.md section 4.27 are settled.

## Ownership

- S1 author owns logic_pure/logic_pure_combat_engine.py, logic_pure/logic_pure_combat_supplies.py, __init__.py transition and combat callbacks (baseline lines 1553-1665, 4596-4620, 4800-4875, 5244-5343), ui/ui.py selectors (baseline lines 7693-7710 and 20599-21261), and its focused tests.
- S2 author starts after S1 commit. It owns runtime/runtime_actions_combat.py, the runtime context callback field if needed, __init__.py review notice queue, ui/ui.py completion dialog and HUD, and its focused tests.
- Codex owns tools/pass14_reproduce.py, tools/pass14_screenshots.py, evidence, audits, pins, commits, and promotion. No other agent writes these files.
- No concurrent writers share a file. The MacBook mirror has one owner during each lane.

## Acceptance

1. S1 accepts every live Encounter method change, keeps enemy LP and countdowns for method changes, and ends the Encounter on kill, death, flee, bank run, or Action/target change. The next fight is fresh.
2. S2 queues one completion notice on the final kill, flushes it after review, uses the exact owner text, preserves activity text, and keeps combat active. The HUD reads active assignment state.
3. Run focused suites and neighbours, then both lanes sequentially per slice. Verify S2 with shown offscreen Qt dialog and HUD screenshots at default size and 560 logical points tall. Kimi reviews the frontend before promotion.
4. Re-absorb main and run tools/promotion_gate.py run --remote-lanes, then land the exact passing tree. Do not push.

## Safety

Only the leased worktree can receive edits. Never edit canonical addons21, call treehouse directly, bypass hooks, amend, push, change git config, set SLOP_GATE_* variables, weaken audits, or change cadence/XP/menu loading. Keep __init__.py below 6250 lines. Record second-level findings without fixing them. Codex owns all git and release actions.

## Events

- 2026-09-13: Lease first failed with all 16 slots in use or dirty. Slot 8 was clean, already merged, and unused by running processes. Guard returned it and leased pass14 with id a6cf62363bab03fe74eff4211049a8b4; branch renamed goal/pass14.
- Baseline offscreen reproduction accepted the failure: black bear at 230 LP and both countdowns at 3 survived Bankstanding; style change returned false with the exact active-fight refusal.


- Evidence leaf now exclusively owns tools/pass14_reproduce.py, tools/pass14_screenshots.py, and evidence/pass14/reproductions/ plus screenshots/. Codex retains other records. S2 dialog contract: show_slayer_completion_dialog(count, enemy_plural).

- 2026-09-13T22:50:59: Both baseline reproductions are saved under evidence/pass14/reproductions/. The Encounter after probe passes on the S1 draft. Parent review found refill_combat_supply_loadout_pure and unload_combat_supply_loadout_pure still reject an active Encounter; close this before acceptance. Check per-mutation next-review coverage, automatic bank return, and all Action-selection seams before gates.

- 2026-09-13T22:56:15: Opus completed S1 without running tests. Codex now owns all production files and test fixtures except tests/test_integration_smoke.py and tests/test_combat_logic.py, which transfer exclusively to the S1 coverage leaf. That leaf must prove each mutation on its next real review and replace the remaining live-supply refusal pins. The bank-only-access restriction in the Opus report is unsupported by section 4.27 and is rejected.

- S1 transition neighbour rerun: 73 tests in 24.664s, OK. Remote surface evidence: `ankiscape_worktrees/pass14-evidence/s1-surfaces/`; root Qt digest is `cdec341680dfeb1297e139e69de079a140487a31f60ef4edb0930dbda2f6a383`; combat engine digest is unchanged. Standalone reachability audit exits 1 with `1663 actions; 2343 reachable items; 163 orphan inputs; 249 blocked actions`; retain the pinned debt and verify its equality in the gate.

- S1 coverage leaf returned ownership of tests/test_integration_smoke.py and tests/test_combat_logic.py. All production and tests are frozen for the parent focused run and sequential remote lanes. The leaf reports 44 focused tests passed in both environments; parent full module execution is binding.

- S1 focused rerun passed `Ran 1075 tests in 269.453s`, `OK`; sequential remote lanes are running under `ankiscape_worktrees/pass14-evidence/s1-verification-recheck/`. S2 preparation is stored as data-only patch artifacts, not applied source, so S1 stays fixed during both lanes.

- S1 storage neighbour now passes `Ran 75 tests in 2.597s`, `OK`. Main was re-absorbed by fast-forward to `615ed90071d689679b3257d2d687a07d91794fdb` (documentation changes only). Documentation audit: `Audited 713 Markdown and 446 HTML files. Documentation audit passed.` Final sequential S1 lane logs are in `ankiscape_worktrees/pass14-evidence/s1-lanes-final/`.

## Finding left outside this pass

The existing near-death confirmation in `__init__.py` (`_prompt_near_death`) asks "Walk away from the fight as well?" after its handler has switched to Bankstanding. Under the Encounter-ending seam, there is no retained fight at that point. Its Yes/No wording and redundant clear remain for a separate dialog pass.

## Independent review disposition

Kimi K3 reviewed S1 source and the prepared S2 patch. Its first read-only run hit `error: tool loop exceeded 24 turns`; the bounded source-only retry returned a review in `memory-bank/evidence/pass14/kimi-bounded-review-output.txt`.

- S1 Action objection rejected: `ui/ui.py` adds only `attack` and `finisher` to the Combat method combo. GLOSSARY.md defines Action as the selected skill, activity, or utility; selecting the finisher keeps Combat selected. The new finisher test retains the weakened enemy and executes the finisher. Clearing on this field would violate the settled ruling.
- S1 residual-refusal concern is unreachable: `unload_combat_supply_loadout_pure` and `refill_combat_supply_loadout_pure` return `(data, True, "")` unconditionally after the deleted guard. Reconciliation has no remaining refusal source. No new error path or rollback is added.
- S2 initial visibility correction accepted: construct the Slayer HUD label hidden, then render it from the pure view. The headless import will be executed in focused checks.
- S2 HUD height is a rendering risk, not a confirmed defect. The 340 by 128 logical-point strip stays fixed; verify all existing rows and the added row in the actual captures. `ReviewHUD.set_data` calls `show`, so the geometry test does operate on a shown widget.
- Existing near-death copy is left in the recorded follow-up. No cadence, XP, menu, or new mechanic work is added.

## S1 first passing result

The focused run passed 1075 tests in 269.453s; the storage neighbour passed 75 tests in 2.597s. Remote plain passed 5632 tests in 599.004s with 1367 skips. Remote offscreen Qt passed 5632 tests in 1153.127s with 5 skips. Lane evidence: `/Users/ArmanTarkhanian1/Library/Application Support/Anki2/ankiscape_worktrees/pass14-evidence/s1-lanes-final/`. The offscreen Encounter after reproduction accepts the style change, clears the old Encounter at Bankstanding, and returns to a fresh 250-LP bear. Both before and after records are under `memory-bank/evidence/pass14/reproductions/`.

## S1 commit-gate corrections

The global hook refused file growth and new complexity. Keep every behavioral assertion, group Encounter coverage in tests/combat/test_encounter_lifecycle.py and tests/ui/test_encounter_transitions.py, and group reusable pass tooling in tools/pass14/. Action selection now shares its state/config/menu transition. The deleted supply guards leave refill and unload infallible, so remove their dead error branches. The bank-run started flag is set from the presence of an existing run. Re-run focused neighbours and both lanes after this correction, then commit through the unchanged hook.

- Hook-fix verification: 23 moved Encounter tests pass in plain (2 widget skips) and offscreen Qt (no skips). A parent AST comparison against the staged pre-move S1 found the same test names across all six source modules and the new destinations; only three added success assertions differ in assertion counts. The saved-state, menu, direct-action and pure Encounter coverage remains intact. All remote module-surface digests match the existing S1 pins. Full lane logs are under ankiscape_worktrees/pass14-evidence/s1-hook-fix-lanes/.

## S1 completed verification

plain: Ran 5617 tests in 596.100s; OK (skipped=1361). qt: Ran 5617 tests in 1146.352s; OK (skipped=5). Logs are in ankiscape_worktrees/pass14-evidence/s1-hook-fix-lanes/. The unchanged global hook then found one newly missing blank line between moved-test definitions; restore it and verify Python AST equality before committing. This formatting correction changes no executed statement. The separate local new-module and six-module neighbour logs are in ankiscape_worktrees/pass14-evidence/test-organization/.

## S2 behavior and focused verification

S1 committed as a6622434659324c2fff5f7b76f155cc1d356cbca. S2 queues the completed assignment count and family name through the existing pending-review list. The shared completion renderer keeps the Level Up dialog surface; the native answer returns before the queued modal opens. The pure Slayer view supplies the HUD count. Active Slayer progress uses 2-point row spacing so all text fits the existing 340 by 128 HUD; other states retain 4-point spacing. All existing row text is preserved.

Focused suites and neighbours: Ran 890 tests in 253.149s; OK. The direct final-review test captures the native answer return before opening the real modal, accepts OK, and executes another Combat review that damages an enemy. Earlier, off-task, and subsequent completed-assignment kills do not queue another notice. The before/after Slayer reproduction changes from zero queued dialogs to one; assignment completion, existing activity text, and the Combat Action remain intact.

Offscreen Qt images were shown, resized, event-pumped, captured, and inspected by Codex at parent sizes 1000 by 700 and 900 by 560 logical points. All four captures pass text-fit, containment, and overlap probes in evidence/pass14/screenshots/probes.json. The HUD also fits inside its ReviewStrip and parent. No text is truncated. The dialog is 380 by 200 logical points. Independent source review found no actionable defect; the required final Kimi taste pass uses the rendered geometry and operator observations.

The standalone audits report: Audited 713 Markdown and 446 HTML files. Documentation audit passed. Test quality: 4761 tests across 266 files; hard issues: 0; structural clone candidates: 31 groups. Reachability remains the pinned debt: 1663 actions; 2343 reachable items; 163 orphan inputs; 249 blocked actions. Worktree layout is safe. The quick PEP 8 and cyclomatic ratchets report no new violations.

A second-level source finding remains unchanged: runtime/runtime_actions_combat.py imports RuntimeActionContext and shared helpers twice, around lines 388-420. This duplication does not affect the two requested behaviors and is outside this pass.

- Final Kimi K3 frontend-taste review: ACCEPT, no blocking defects found. It reviewed final source and all four geometry records, with Codex providing the image inspection. Review record: memory-bank/evidence/pass14/s2-kimi-taste-output.txt. The direct completed-assignment key and plural family name are existing pure-logic contracts, not new fallback cases.

- Bounded cognitive/Halstead preflight against S1 HEAD passed: 32 changed outer functions across 14 Python paths, no new or worsened violations. The combat handler cognitive value decreases from 187 to 184; new screenshot geometry code is 14. Raw evidence stays under ankiscape_worktrees/pass14-evidence/s2-cognitive-preflight/.

- S2 full plain lane passed: Ran 5620 tests in 593.072s; OK (skipped=1363). The offscreen Qt lane follows sequentially on the frozen source. Logs: ankiscape_worktrees/pass14-evidence/s2-full-lanes/.

## S2 completed verification

The full sequential lanes passed on the final S2 source: plain Ran 5620 tests in 593.072s; OK (skipped=1363). Offscreen Qt Ran 5620 tests in 1137.014s; OK (skipped=5). The focused and adjacent suites passed 890 tests in 253.149s. Lane logs are under ankiscape_worktrees/pass14-evidence/s2-full-lanes/. The one results artifact is memory-bank/status-updates/pass14-results-2026-09-14.html; its mechanical preflight passed, and it was opened in Zen. Final promotion must bind both remote lanes and audits to the committed tree before landing.

- Results artifact published at https://3804sun2odmh.postplan.dev. The immutable plan remains at https://qz880in824zp.postplan.dev. Final documentation audit: Audited 713 Markdown and 447 HTML files. Documentation audit passed.

## S2 commit-boundary correction

The normal commit hook rejected the additional UI dependency and the unused public import; no S2 commit was created. Keep post-review scheduling with the existing core/logic.py review orchestrators, and keep ui/completion_dialogs.py responsible only for rendering the shared dialog. The two function ASTs are identical before and after this separation. Root retains the queue snapshot and clear, then calls the scheduling helper through its existing core.logic dependency. No audit, threshold, hook, or bypass setting changed.

The actual import/dead-code/layout preflight now passes with zero violations. The gate identifies ui/completion_dialogs.py as a part of ui/ui.py. The reusable tools/pass14/check_imports.py records this evidence before the full commit hook. Final source pins were remeasured remotely; the root Qt digest is 029716e1c03079e0cf96e22b64e01ef710a988aeb6f4d403cb5f1acc72e894a5. The final scheduling neighbour run passed 60 tests in 8.814s with one expected skip. Both the final Slayer reproduction and all four screenshot probes passed; every PNG is byte-identical to the inspected and reviewed image. Expanded focused suites and both full sequential lanes now run on the final source under ankiscape_worktrees/pass14-evidence/s2-scheduling-verification/ and s2-scheduling-lanes/.

- 2026-09-14T09:46:51.677487+00:00: Final expanded focused and neighbouring suites passed: Ran 1058 tests in 275.975s; OK (skipped=1). The final plain and Qt lanes remain sequential in ankiscape_worktrees/pass14-evidence/s2-scheduling-lanes/. Source is frozen. The normal local commit hook may run alongside this remote verification; any source mutation or failed check requires correction and fresh verification before promotion.

- Final application verification passed: plain Ran 5620 tests in 581.546s; OK (skipped=1363). Offscreen Qt Ran 5620 tests in 1129.200s; OK (skipped=5). Logs: ankiscape_worktrees/pass14-evidence/s2-scheduling-lanes/. The commit hook found only the new import-preflight utility main at cognitive complexity 16, above 15; simplify that utility and check the explicit threshold before another normal commit. Application source stays unchanged.

- 2026-09-14T10:07:24.221593+00:00: The structural preflight utility now iterates the existing staged paths directly, removing one nested condition. Explicit complexipy -mx 15 reports tools/pass14/check_imports.py main 13 and exits 0. This tooling-only correction leaves all application and test source from the passing final lanes unchanged.
