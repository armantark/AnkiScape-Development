# Overnight Handoff: Audit Reachability Truth

## Committed This Stretch

Commit `eba91888` is on `goal/audit-truth-2026-08-12`.

Its message is: "Quest-stage grants looked reachable when their actions were inert; make the audit follow runtime blockers".

The plain lane passed:

```text
Ran 4059 tests in 198.194s
OK (skipped=496)
```

The offscreen Qt lane passed:

```text
Ran 4059 tests in 477.325s
OK (skipped=3)
```

The focused regression failed in each direction before the correction.

## The Headline

`tools/audit_item_reachability.py` seeded every quest-stage product without checking the stage's `required_action` blockers. `handle_quest_answer` rejects those products in `runtime/runtime_actions_production.py:1298-1362` when the blockers are not satisfiable.

The corrected totals on main's catalog are:

- 1556 actions.
- 2493 items.
- 103 orphans.
- 102 blocked items.

The item total decreased by 80 from 2573. This is a measurement correction, not a regression. The audit reported 80 items as reachable, but they were never reachable.

The full list is in `memory-bank/audits/quest-stage-reachability-truth-2026-08-12.md`.

Do not try to restore the old number.

## The Third Blind Spot in the Audit Tool

This is the third blind spot after `weighted_secondary_outputs` and quest-combat guaranteed drops. Those two blind spots under-reported reachability. Real routes looked like orphans, so a person eventually investigated them.

This blind spot over-reported reachability. It marked missing routes as complete, so nobody investigated them. This direction of error can hide work permanently.

The durable lesson is to separate under-reporting from over-reporting. Under-reporting creates visible false alarms. Over-reporting creates invisible omissions.

## A Committed Slice Overstated Its Result

Commit `d2faf1d2` on `goal/secondaries-2026-08-11` reported 23 newly reachable items. That result was overstated. Three items are inert:

- `Herb pouch`.
- `Diamond root`.
- `Diamond root dust`.

Nial Swiftfling defaults `minimum_player_combat` to the enemy level of 156. A normal maxed player has combat level 126. The real kernel therefore returns `combat_underpowered`, and the encounter is unreachable.

`Troll thistle` from `quest-stage:eadgars_ruse:4` is genuinely reachable. Eadgar stages 1 through 4 use `auto_actions`. The test helper does not seed `quest_stage_actions`. Therefore, only three of the 23 items are affected.

## Why the Orchestrator Missed the Error

The regression drives the real `apply_quest_combat_encounter_pure` kernel. It also checks the exact completed encounter and one pouch in the inventory. The orchestrator accepted this as proof.

That proof was necessary, but it was not sufficient. The test constructed a player who could meet the gate. Nobody checked whether a real player could reach that state.

Use this rule for future tests: "drives the real kernel" and "starts from a state a real player can reach" are separate claims. The first claim does not imply the second claim.

## Candidate Next Slice

The default value for `minimum_player_combat` is very likely wrong for quest combat. It uses the enemy's level. In the period game, the player fights Nial during Glorious Memories regardless of level.

Correct the default for quest encounters only after period sourcing for each encounter. This correction can legitimately restore the `Herb pouch` chain. Do not weaken the test.

## Other Open Work

### Crafting Moulds

`goal/moulds-2026-08-11` is blocked, with nothing committed. The four crafting-mould routes need a production emitter for quest-stage `required_action` values. This is a broader quest-interaction mechanism than an acquisition slice must introduce.

Its worktree also contains a `GOAL-BLOCKED.md`. That file is slice-level, not goal-level. Do not read it as a block on all work.

### Wyvern Worktree

`goal/wyvern-2026-08-11` contains uncommitted work. That work is entirely redundant with `goal/breadth-2026-08-11` and can be discarded.

### Remaining Orphan Families

The verified remaining-work list contains 26 orphan roots that no branch fixes. Take the work as families. The current best family candidates are:

- Chompy: `Raw chompy` and `Skewer stick`.
- Crab: `Fresh crab claw` and `Fresh crab shell`.
- Dragon tips: `Dragon arrowtips` and `Dragon dart tip`.
- Vines: `Corrupt`, `Guthix`, and `Shadow`.

This list was derived before `eba91888`. Re-derive it with the corrected audit before use.

## Merge Notes

The following branches await the owner:

- `goal/secondaries-2026-08-11`: `d2faf1d2` and `3c05da03`. Account for the three-item overstatement above.
- `goal/papercuts-2026-08-11`: `db14782b`.
- `goal/audit-truth-2026-08-12`: `eba91888`.
- `goal/breadth`.
- `goal/herbs`.
- `goal/vines`.
- `goal/bones`.

Three older branches predate main's current commit and need a rebase.

`goal/grind-2026-08-11` is abandoned and contested. Do not merge it.

## Still Open for the Owner

The owner must decide whether the runtime must enforce facility prerequisites such as an anvil or fire. This question is unresolved, not rejected.

A provenance failure also remains open. Work orders cited a code-review finding that the review never issued. This failure burned several sessions.
