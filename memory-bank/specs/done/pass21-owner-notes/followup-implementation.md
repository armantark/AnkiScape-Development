# Pass 21 follow-up implementation, 2026-11-05

The eight-point authority is `followup-grill.md` in this directory. This work is committed on `goal/pass21-followup`; it does not promote the add-on.

1. Automatic ammunition compares the worn balance with Bank stock at each refill, then wears the strongest compatible type allowed by the player's levels. Returning the old stack conserves its entire count.
2. Hand-equipping ammunition records its type in `equipment_ammunition_manual`. Bank runs keep and refill that type until its worn and Bank supply is exhausted; then automatic choice resumes. Hand-removal clears the mark. Sanitizing an unmarked save defaults to automatic. Review recovery and isolated Dungeoneering combat preserve the mark.
3. The Ammunition row adds only “Manual” beside the count. Its native row delegate wraps that row at narrow widths, keeping count and mark together, without widening the Equipment layout.
4. Selecting a target with an empty slot readies Bank ammunition immediately. Direct combat dispatch has the same first-card preparation. Active encounters and requested bank runs retain travel; an empty Bank retains the existing refusal. Target-selection undo returns the stack to the Bank.
5. A single ordered stock projection reserves inputs for earlier entries before crediting their remaining products. Missing-input rows become queueable only when that stock clears the real recipe lock. Their count box is bounded by available supply, including every required input and batch yield. A request for one shaft still makes a whole batch of 15, so that full batch can fund a following 15-headless-arrow entry; the real queue flow proves both entries complete without a shortage stop. Quest, level and tool locks keep their existing predicates.
6. Material-only gray rows retain one-click selection through the existing shared skill and Utility selectors. Add now names that pick and remains disabled without its supply; Start waits for actual Bank materials. Supplied plan rows use normal text; gray rows use the dim helpers.
7. Queue edits reconcile dependencies in the same undoable change. A row that loses all supply is removed immediately with the existing “Queue: … stopped · Requires: …” Event-log line. A partially funded row keeps only its funded count. Removing the producer of the sole remaining dependent row ends at Bankstanding; moving the producer behind its consumer drops the consumer and keeps the producer. The edit does not spend a review discovering the missing material. Tests also play a partially funded row through to completion without a shortage stop.
8. Diary claim progress counts live rows. Completing those rows enables the tier reward even with dormant rows. A stored claim remains claimed when a dormant row becomes live, and the reward cannot be claimed twice. A tier with no live rows remains unclaimable.

The 50% ammunition recovery rule, Ava recovery values and bone mechanics are unchanged.

## Local behavior checks

```text
python3 run_tests.py tests.action_queue tests.pace.test_ammunition_pack tests.achievement_diaries.test_authored_deeds tests.test_achievement_diaries tests.integration_smoke.test_ammunition_undo
Ran 236 tests in 107.445s

OK
```

```text
python3 run_tests.py tests.test_combat_logic tests.combat tests.test_runtime_actions tests.runtime_actions.test_ranged_finisher tests.integration_smoke.test_ammunition_undo tests.pace.test_ammunition_pack
Ran 579 tests in 4.096s

OK
```

```text
python3 run_tests.py tests.action_queue.test_queue_plan_rows tests.main_menu.skills.test_combat_controls
Ran 32 tests in 17.058s

OK
```

Logs: `/tmp/pass21-followup-final-queue2.log`, `/tmp/pass21-followup-final-combat2.log` and `/tmp/pass21-followup-final-ui.log`.

## Visual reproduction

```text
.venv-qt/bin/python tools/maintenance/pass21_followup_evidence.py --output /tmp/pass21-followup-evidence
```

This uses fresh fixture saves only, opens real offscreen Qt menus before capture, and records light/dark Manual, unsupported gray-row and partially supplied arrow states at default size and 900×560. The screenshots and `probes.json` are under `/tmp/pass21-followup-evidence`; the command log is `/tmp/pass21-followup-visual.log`. No player save, Anki profile database, remote mirror or native Anki session was used. Native Anki, promotion checks and a frontend taste review remain outside this implementation run.

## Hook evidence

The first commit attempt was refused for added complexity, oversized-file growth, an import cycle and added import fan-out. The supply forecast now lives with the action product model below both callers; target preparation owns the combat start/bank window; Equipment's existing panel module owns its slot renderer. No hook was skipped. `/tmp/pass21-followup-queue-after.json` records the reconciler at CCN 7 / cognitive 10 / Halstead difficulty 2.25. `/tmp/pass21-followup-diary-after.json` records the diary function at CCN 18 / cognitive 17, equal to its pre-change debt rather than an increase.
